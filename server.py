from __future__ import annotations

import base64
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import socket
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from jsonschema import Draft202012Validator, FormatChecker

from bazi_core.annual_engine import annual_schema_path, build_annual_outlook
from bazi_core.generator import build_core_output, schema_path
from bazi_core.monthly_compass import build_monthly_compass, monthly_compass_schema_path
from bazi_core.oracle_engine import interpret_cast, oracle_schema_path
from bazi_core.system_info import build_system_status
from bazi_core.trait_engine import build_trait_output, trait_schema_path

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
API_VERSION = "0.2.0"
MAX_JSON_BODY_BYTES = 64 * 1024
MAX_NOTIFICATION_BODY_BYTES = 256 * 1024
PRO_SESSION_SECONDS = 30 * 60
ALLOWED_PRODUCT_IDS = {"ming.pro.monthly", "ming.pro.yearly"}
ALLOWED_ORACLE_CATEGORIES = {"general", "career", "wealth", "relationship", "decision", "growth"}
ALLOWED_ORACLE_HORIZONS = {"seven_days", "one_month", "three_months"}
SESSION_COOKIE = "bazi_session"
SESSION_SECRET = os.environ.get("BAZI_SESSION_SECRET", secrets.token_urlsafe(48)).encode("utf-8")
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMITS = {
    "/api/generate": 40,
    "/api/pro/report": 24,
    "/api/pro/annual-report": 24,
    "/api/pro/monthly-compass": 24,
    "/api/oracle/interpret": 30,
    "/api/app-store/transactions": 20,
    "/api/app-store/notifications": 120,
    "/api/entitlement/demo-unlock": 12,
    "/api/entitlement/demo-lock": 12,
}
_RATE_BUCKETS: dict[tuple[str, str], list[float]] = {}
_RATE_LOCK = threading.Lock()
_ENTITLEMENT_LOCK = threading.Lock()
_ENTITLEMENTS: dict[str, "EntitlementRecord"] = {}


class ClientInputError(Exception):
    def __init__(self, error: str, message: str | None = None, status: int = 400):
        super().__init__(error)
        self.error = error
        self.message = message or error
        self.status = status


class RequestTooLarge(ClientInputError):
    def __init__(self) -> None:
        super().__init__("request_body_too_large", "Request body is too large.", 413)


class RateLimitExceeded(ClientInputError):
    def __init__(self) -> None:
        super().__init__("rate_limited", "Too many requests. Please retry later.", 429)


class EntitlementUnavailable(Exception):
    pass


@dataclass
class EntitlementRecord:
    subject: str
    status: str
    is_pro: bool
    source: str
    environment: str
    product_id: str | None
    expires_at: datetime | None
    transaction_id: str | None = None
    original_transaction_id: str | None = None
    app_account_token: str | None = None
    anonymous_install_id: str | None = None
    revocation_date: datetime | None = None
    last_event: str | None = None
    updated_at: datetime | None = None

    @property
    def needs_restore(self) -> bool:
        return self.status in {"expired", "revoked", "needs_restore"}

    def to_public(self, *, can_demo_unlock: bool = False, storekit_ready: bool = True) -> dict[str, Any]:
        active = self.is_pro and self.status == "pro_active" and not self.is_expired()
        status = "pro_active" if active else self.status
        if not active and status == "pro_active":
            status = "expired"
        return {
            "status": status,
            "is_pro": active,
            "tier": "pro" if active else "free",
            "source": self.source,
            "environment": self.environment,
            "product_id": self.product_id if active else None,
            "expires_at": _format_dt(self.expires_at) if active and self.expires_at else None,
            "needs_restore": not active and self.needs_restore,
            "can_demo_unlock": can_demo_unlock,
            "storekit_ready": storekit_ready,
        }

    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= datetime.now(timezone.utc)


def _format_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _millis_to_datetime(value: int | None) -> datetime | None:
    if value in (None, 0):
        return None
    return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)


class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


@dataclass(frozen=True)
class AppStoreConfig:
    issuer_id: str
    key_id: str
    private_key: bytes
    bundle_id: str
    environment: str
    root_certificates: tuple[bytes, ...]
    app_apple_id: int | None

    @classmethod
    def from_env(cls) -> "AppStoreConfig":
        issuer_id = os.environ.get("APP_STORE_ISSUER_ID", "").strip()
        key_id = os.environ.get("APP_STORE_KEY_ID", "").strip()
        bundle_id = os.environ.get("APP_STORE_BUNDLE_ID", "app.mingpattern.life").strip()
        environment = os.environ.get("APP_STORE_ENVIRONMENT", "sandbox").strip().lower()
        private_key = _read_private_key()
        root_certificates = _read_root_certificates()
        if not all([issuer_id, key_id, bundle_id, private_key, root_certificates]):
            raise EntitlementUnavailable("app_store_validation_not_configured")
        if environment not in {"sandbox", "production"}:
            raise EntitlementUnavailable("app_store_validation_not_configured")
        app_apple_id_value = os.environ.get("APP_STORE_APP_APPLE_ID", "").strip()
        app_apple_id = int(app_apple_id_value) if app_apple_id_value else None
        if environment == "production" and app_apple_id is None:
            raise EntitlementUnavailable("app_store_validation_not_configured")
        return cls(
            issuer_id=issuer_id,
            key_id=key_id,
            private_key=private_key,
            bundle_id=bundle_id,
            environment=environment,
            root_certificates=tuple(root_certificates),
            app_apple_id=app_apple_id,
        )


def _read_private_key() -> bytes:
    inline_key = os.environ.get("APP_STORE_PRIVATE_KEY", "").strip()
    if inline_key:
        return inline_key.replace("\\n", "\n").encode("utf-8")
    key_path = os.environ.get("APP_STORE_PRIVATE_KEY_PATH", "").strip()
    if not key_path:
        return b""
    try:
        return Path(key_path).expanduser().read_bytes()
    except OSError as exc:
        raise EntitlementUnavailable("app_store_validation_not_configured") from exc


def _read_root_certificates() -> list[bytes]:
    raw_paths = os.environ.get("APP_STORE_ROOT_CERT_PATHS", "").strip()
    if not raw_paths:
        return []
    separators = [os.pathsep, ","]
    paths = [raw_paths]
    for separator in separators:
        paths = [item for value in paths for item in value.split(separator)]
    certificates: list[bytes] = []
    for raw_path in paths:
        path = raw_path.strip()
        if not path:
            continue
        try:
            certificates.append(Path(path).expanduser().read_bytes())
        except OSError as exc:
            raise EntitlementUnavailable("app_store_validation_not_configured") from exc
    return certificates


def _app_store_environment(config: AppStoreConfig) -> Any:
    from appstoreserverlibrary.models.Environment import Environment

    return Environment.PRODUCTION if config.environment == "production" else Environment.SANDBOX


def _app_store_client(config: AppStoreConfig) -> Any:
    from appstoreserverlibrary.api_client import AppStoreServerAPIClient

    return AppStoreServerAPIClient(
        signing_key=config.private_key,
        key_id=config.key_id,
        issuer_id=config.issuer_id,
        bundle_id=config.bundle_id,
        environment=_app_store_environment(config),
    )


def _app_store_verifier(config: AppStoreConfig) -> Any:
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier

    return SignedDataVerifier(
        root_certificates=list(config.root_certificates),
        enable_online_checks=True,
        environment=_app_store_environment(config),
        bundle_id=config.bundle_id,
        app_apple_id=config.app_apple_id,
    )


def _is_storekit_stub_allowed() -> bool:
    return (
        os.environ.get("BAZI_STOREKIT_STUB") == "1"
        and os.environ.get("BAZI_ALLOW_INSECURE_STOREKIT_STUB") == "1"
        and os.environ.get("APP_STORE_ENVIRONMENT", "sandbox").lower() != "production"
    )


def _store_entitlement(record: EntitlementRecord) -> EntitlementRecord:
    with _ENTITLEMENT_LOCK:
        record.updated_at = datetime.now(timezone.utc)
        keys = {
            record.subject,
            f"tx:{record.original_transaction_id}" if record.original_transaction_id else "",
            f"txn:{record.transaction_id}" if record.transaction_id else "",
            f"app:{record.app_account_token}" if record.app_account_token else "",
            f"install:{record.anonymous_install_id}" if record.anonymous_install_id else "",
        }
        for key in keys:
            if key:
                _ENTITLEMENTS[key] = record
    return record


def _free_entitlement(*, can_demo_unlock: bool = False, storekit_ready: bool = True, status: str = "free") -> dict[str, Any]:
    return {
        "status": status,
        "is_pro": False,
        "tier": "free",
        "source": "server",
        "environment": os.environ.get("APP_STORE_ENVIRONMENT", "sandbox"),
        "product_id": None,
        "expires_at": None,
        "needs_restore": status in {"expired", "revoked", "needs_restore"},
        "can_demo_unlock": can_demo_unlock,
        "storekit_ready": storekit_ready,
    }


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unbase64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _sign_session(payload: dict[str, Any]) -> str:
    body = _base64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(SESSION_SECRET, body.encode("ascii"), hashlib.sha256).digest()
    return f"{body}.{_base64url(signature)}"


def _verify_session(token: str) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    body, signature = token.rsplit(".", 1)
    expected = _base64url(hmac.new(SESSION_SECRET, body.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        payload = json.loads(_unbase64url(body).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) <= int(time.time()):
        return None
    return payload


def _issue_session(record: EntitlementRecord) -> tuple[str, str]:
    now = int(time.time())
    token = _sign_session(
        {
            "sub": record.subject,
            "source": record.source,
            "product_id": record.product_id,
            "original_transaction_id": record.original_transaction_id,
            "iat": now,
            "exp": now + PRO_SESSION_SECONDS,
        }
    )
    cookie = (
        f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict; "
        f"Max-Age={PRO_SESSION_SECONDS}"
    )
    if os.environ.get("BAZI_COOKIE_SECURE") == "1":
        cookie += "; Secure"
    return token, cookie


def _clear_session_cookie() -> str:
    return f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"


def _session_subject_from_record(record: EntitlementRecord) -> str:
    if record.app_account_token:
        return f"app:{record.app_account_token}"
    if record.original_transaction_id:
        return f"tx:{record.original_transaction_id}"
    if record.anonymous_install_id:
        return f"install:{record.anonymous_install_id}"
    if record.transaction_id:
        return f"txn:{record.transaction_id}"
    return f"session:{secrets.token_urlsafe(18)}"


def _subject_from_payload(payload: dict[str, Any], decoded_transaction: Any) -> str:
    app_account_token = _string_attr(decoded_transaction, "appAccountToken") or _optional_uuid_string(payload.get("app_account_token"))
    original_transaction_id = _string_attr(decoded_transaction, "originalTransactionId") or _optional_identifier(payload.get("original_transaction_id"))
    transaction_id = _string_attr(decoded_transaction, "transactionId") or _optional_identifier(payload.get("transaction_id"))
    anonymous_install_id = _optional_uuid_string(payload.get("anonymous_install_id"))
    if app_account_token:
        return f"app:{app_account_token}"
    if original_transaction_id:
        return f"tx:{original_transaction_id}"
    if anonymous_install_id:
        return f"install:{anonymous_install_id}"
    if transaction_id:
        return f"txn:{transaction_id}"
    raise ClientInputError("invalid_transaction", "Transaction identity is missing.")


def _record_from_transaction(
    decoded_transaction: Any,
    *,
    status: Any = None,
    fallback_subject: str | None = None,
    anonymous_install_id: str | None = None,
    last_event: str | None = None,
) -> EntitlementRecord:
    product_id = _string_attr(decoded_transaction, "productId")
    if product_id not in ALLOWED_PRODUCT_IDS:
        raise ClientInputError("unsupported_product", "Product is not a supported Pro subscription.", 403)
    expires_at = _millis_to_datetime(getattr(decoded_transaction, "expiresDate", None))
    revocation_date = _millis_to_datetime(getattr(decoded_transaction, "revocationDate", None))
    status_value = _status_value(status)
    active_status = status_value in (None, 1, 4)
    is_active = active_status and revocation_date is None and (expires_at is None or expires_at > datetime.now(timezone.utc))
    if revocation_date is not None or status_value == 5:
        entitlement_status = "revoked"
    elif not is_active and expires_at is not None and expires_at <= datetime.now(timezone.utc):
        entitlement_status = "expired"
    elif not is_active:
        entitlement_status = "needs_restore"
    else:
        entitlement_status = "pro_active"
    app_account_token = _string_attr(decoded_transaction, "appAccountToken")
    record = EntitlementRecord(
        subject=fallback_subject or "pending",
        status=entitlement_status,
        is_pro=is_active,
        source="app_store",
        environment=_environment_value(getattr(decoded_transaction, "environment", None)),
        product_id=product_id,
        expires_at=expires_at,
        transaction_id=_string_attr(decoded_transaction, "transactionId"),
        original_transaction_id=_string_attr(decoded_transaction, "originalTransactionId"),
        app_account_token=app_account_token,
        anonymous_install_id=anonymous_install_id,
        revocation_date=revocation_date,
        last_event=last_event,
    )
    if record.subject == "pending":
        record.subject = _session_subject_from_record(record)
    return record


def _latest_subscription_record(client: Any, verifier: Any, any_transaction_id: str, fallback_subject: str) -> EntitlementRecord | None:
    status_response = client.get_all_subscription_statuses(any_transaction_id)
    candidates: list[EntitlementRecord] = []
    for group in getattr(status_response, "data", None) or []:
        for item in getattr(group, "lastTransactions", None) or []:
            signed_transaction = getattr(item, "signedTransactionInfo", None)
            if not signed_transaction:
                continue
            decoded = verifier.verify_and_decode_signed_transaction(signed_transaction)
            try:
                candidates.append(
                    _record_from_transaction(
                        decoded,
                        status=getattr(item, "status", None),
                        fallback_subject=fallback_subject,
                    )
                )
            except ClientInputError:
                continue
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.expires_at or datetime.min.replace(tzinfo=timezone.utc))


def _validate_signed_transaction_payload(payload: dict[str, Any]) -> str:
    signed_transaction = payload.get("signed_transaction")
    if not isinstance(signed_transaction, str) or not signed_transaction:
        raise ClientInputError("missing_signed_transaction", "Signed transaction is required.")
    if len(signed_transaction) > 128 * 1024 or not re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", signed_transaction):
        raise ClientInputError("invalid_signed_transaction", "Signed transaction format is invalid.")
    return signed_transaction


def _validate_app_store_transaction(payload: dict[str, Any]) -> EntitlementRecord:
    signed_transaction = _validate_signed_transaction_payload(payload)
    if _is_storekit_stub_allowed():
        return _storekit_stub_record(payload)
    try:
        config = AppStoreConfig.from_env()
        verifier = _app_store_verifier(config)
        decoded = verifier.verify_and_decode_signed_transaction(signed_transaction)
        subject = _subject_from_payload(payload, decoded)
        anonymous_install_id = _optional_uuid_string(payload.get("anonymous_install_id"))
        transaction_id = _string_attr(decoded, "transactionId") or _optional_identifier(payload.get("transaction_id"))
        original_transaction_id = _string_attr(decoded, "originalTransactionId") or _optional_identifier(payload.get("original_transaction_id"))
        if not (transaction_id or original_transaction_id):
            raise ClientInputError("invalid_transaction", "Transaction identifier is missing.")
        client = _app_store_client(config)
        record = _latest_subscription_record(client, verifier, transaction_id or original_transaction_id, subject)
        if record is None:
            record = _record_from_transaction(
                decoded,
                fallback_subject=subject,
                anonymous_install_id=anonymous_install_id,
            )
        else:
            record.anonymous_install_id = anonymous_install_id
        return _store_entitlement(record)
    except EntitlementUnavailable:
        raise
    except ClientInputError:
        raise
    except ImportError as exc:
        raise EntitlementUnavailable("app_store_validation_not_configured") from exc
    except Exception as exc:
        raise EntitlementUnavailable("app_store_validation_unavailable") from exc


def _validate_app_store_notification(payload: dict[str, Any]) -> dict[str, Any]:
    signed_payload = payload.get("signedPayload") or payload.get("signed_payload")
    if not isinstance(signed_payload, str) or not signed_payload:
        raise ClientInputError("missing_signed_payload", "Signed notification payload is required.")
    if len(signed_payload) > 256 * 1024:
        raise RequestTooLarge()
    try:
        config = AppStoreConfig.from_env()
        verifier = _app_store_verifier(config)
        notification = verifier.verify_and_decode_notification(signed_payload)
        notification_type = _enum_value(getattr(notification, "notificationType", None))
        subtype = _enum_value(getattr(notification, "subtype", None))
        notification_uuid = getattr(notification, "notificationUUID", None)
        data = getattr(notification, "data", None)
        record = None
        if data and getattr(data, "signedTransactionInfo", None):
            decoded = verifier.verify_and_decode_signed_transaction(data.signedTransactionInfo)
            record = _record_from_transaction(
                decoded,
                status=getattr(data, "status", None),
                last_event=notification_type,
            )
            record = _apply_notification_status(record, notification_type)
            _store_entitlement(record)
        return {
            "notification_uuid": notification_uuid,
            "notification_type": notification_type,
            "subtype": subtype,
            "entitlement": record.to_public(storekit_ready=True) if record else None,
        }
    except EntitlementUnavailable:
        raise
    except ClientInputError:
        raise
    except ImportError as exc:
        raise EntitlementUnavailable("app_store_validation_not_configured") from exc
    except Exception as exc:
        raise ClientInputError("invalid_signed_payload", "Signed notification payload could not be verified.", 400) from exc


def _apply_notification_status(record: EntitlementRecord, notification_type: str | None) -> EntitlementRecord:
    if notification_type in {"REFUND", "REVOKE"}:
        record.status = "revoked"
        record.is_pro = False
    elif notification_type in {"EXPIRED", "GRACE_PERIOD_EXPIRED"}:
        record.status = "expired"
        record.is_pro = False
    elif notification_type in {"SUBSCRIBED", "DID_RENEW", "REFUND_REVERSED"}:
        record.is_pro = not record.is_expired() and record.revocation_date is None
        record.status = "pro_active" if record.is_pro else "expired"
    elif notification_type == "DID_FAIL_TO_RENEW" and record.is_expired():
        record.status = "needs_restore"
        record.is_pro = False
    return record


def _storekit_stub_record(payload: dict[str, Any]) -> EntitlementRecord:
    now = datetime.now(timezone.utc)
    app_account_token = _optional_uuid_string(payload.get("app_account_token"))
    anonymous_install_id = _optional_uuid_string(payload.get("anonymous_install_id"))
    record = EntitlementRecord(
        subject=f"app:{app_account_token}" if app_account_token else f"install:{anonymous_install_id or 'local-stub'}",
        status="pro_active",
        is_pro=True,
        source="app_store_stub",
        environment="sandbox",
        product_id="ming.pro.yearly",
        expires_at=now + timedelta(days=365),
        transaction_id="stub-transaction",
        original_transaction_id="stub-original-transaction",
        app_account_token=app_account_token,
        anonymous_install_id=anonymous_install_id,
    )
    return _store_entitlement(record)


def _status_value(status: Any) -> int | None:
    if status is None:
        return None
    value = getattr(status, "value", status)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    return str(getattr(value, "value", value))


def _environment_value(value: Any) -> str:
    raw = _enum_value(value) or os.environ.get("APP_STORE_ENVIRONMENT", "sandbox")
    return raw.lower()


def _string_attr(obj: Any, name: str) -> str | None:
    value = getattr(obj, name, None)
    if value is None:
        return None
    return str(value)


def _optional_identifier(value: Any, *, max_length: int = 80) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,%d}" % max_length, text):
        raise ClientInputError("invalid_identifier", "Identifier format is invalid.")
    return text


def _optional_uuid_string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text):
        raise ClientInputError("invalid_identifier", "UUID format is invalid.")
    return text


class BaziHandler(BaseHTTPRequestHandler):
    server_version = "BaziCoreHTTP/0.2"

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        path = unquote(self.path.split("?", 1)[0])
        if path == "/api/entitlement":
            self._send_json(
                {
                    "ok": True,
                    "entitlement": self._current_entitlement(),
                }
            )
            return
        if path == "/api/system/status":
            self._send_json(
                {
                    "ok": True,
                    "system": build_system_status(),
                }
            )
            return
        if path in ("/", "/app"):
            self._send_file(WEB_ROOT / "index.html")
            return
        if path in ("/legal/privacy", "/privacy"):
            self._send_file(WEB_ROOT / "legal" / "privacy.html")
            return
        if path in ("/legal/terms", "/terms"):
            self._send_file(WEB_ROOT / "legal" / "terms.html")
            return
        if path in ("/legal/support", "/support"):
            self._send_file(WEB_ROOT / "legal" / "support.html")
            return
        if path in ("/legal/methodology", "/methodology", "/data-sources", "/legal/data-sources"):
            self._send_file(WEB_ROOT / "legal" / "methodology.html")
            return
        if path.startswith("/assets/") or path.startswith("/legal/"):
            self._send_web_file(path)
            return
        self._send_json({"error": "not_found"}, status=404)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        try:
            self._check_rate_limit(path)
            if path == "/api/entitlement/demo-unlock":
                self._handle_demo_unlock(True)
                return
            if path == "/api/entitlement/demo-lock":
                self._handle_demo_unlock(False)
                return
            if path == "/api/app-store/transactions":
                self._handle_app_store_transaction()
                return
            if path == "/api/app-store/notifications":
                self._handle_app_store_notification()
                return
            if path == "/api/pro/report":
                self._handle_pro_report()
                return
            if path == "/api/pro/annual-report":
                self._handle_annual_report()
                return
            if path == "/api/pro/monthly-compass":
                self._handle_monthly_compass()
                return
            if path == "/api/oracle/interpret":
                self._handle_oracle_interpret()
                return
            if path == "/api/generate":
                self._handle_generate()
                return
            self._send_json({"ok": False, "error": "not_found"}, status=404)
        except RequestTooLarge as exc:
            self._send_json({"ok": False, "error": exc.error, "message": exc.message}, status=exc.status)
        except RateLimitExceeded as exc:
            self._send_json({"ok": False, "error": exc.error, "message": exc.message}, status=exc.status)
        except ClientInputError as exc:
            self._send_json({"ok": False, "error": exc.error, "message": exc.message}, status=exc.status)
        except EntitlementUnavailable as exc:
            self._send_json(
                {
                    "ok": False,
                    "error": str(exc) or "app_store_validation_unavailable",
                    "message": "App Store entitlement validation is temporarily unavailable.",
                    "entitlement": _free_entitlement(storekit_ready=False, status="needs_restore"),
                },
                status=503,
                extra_headers={"Set-Cookie": _clear_session_cookie()},
            )
        except Exception as exc:
            self.log_error("Unhandled API error on %s: %r", path, exc)
            self._send_json(
                {
                    "ok": False,
                    "error": "internal_error",
                    "message": "The request could not be processed.",
                },
                status=500,
            )

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "not_found"}, status=404)
            return
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _send_web_file(self, path: str) -> None:
        target = (WEB_ROOT / path.lstrip("/")).resolve()
        try:
            target.relative_to(WEB_ROOT.resolve())
        except ValueError:
            self._send_json({"error": "not_found"}, status=404)
            return
        self._send_file(target)

    def _handle_generate(self) -> None:
        payload = self._read_json_body()
        result, traits = _build_and_validate(payload)
        self._send_json({"ok": True, "result": result, "traits": traits, "system": build_system_status()})

    def _handle_demo_unlock(self, unlock: bool) -> None:
        if not self._demo_unlock_enabled():
            raise ClientInputError("demo_unlock_disabled", "Demo unlock is disabled.", 403)
        if not unlock:
            self._send_json(
                {"ok": True, "entitlement": _free_entitlement(can_demo_unlock=True)},
                extra_headers={"Set-Cookie": _clear_session_cookie()},
            )
            return
        now = datetime.now(timezone.utc)
        record = _store_entitlement(
            EntitlementRecord(
                subject=f"demo:{secrets.token_urlsafe(12)}",
                status="pro_active",
                is_pro=True,
                source="local_demo",
                environment="web_test",
                product_id="ming.pro.yearly",
                expires_at=now + timedelta(hours=1),
            )
        )
        session_token, cookie = _issue_session(record)
        self._send_json(
            {
                "ok": True,
                "entitlement": record.to_public(can_demo_unlock=True, storekit_ready=False),
                "session_token": session_token,
            },
            extra_headers={"Set-Cookie": cookie},
        )

    def _handle_app_store_transaction(self) -> None:
        payload = self._read_json_body()
        record = _validate_app_store_transaction(payload)
        if not record.is_pro or record.status != "pro_active":
            self._send_json(
                {"ok": True, "entitlement": record.to_public(storekit_ready=True)},
                extra_headers={"Set-Cookie": _clear_session_cookie()},
            )
            return
        session_token, cookie = _issue_session(record)
        self._send_json(
            {
                "ok": True,
                "entitlement": record.to_public(storekit_ready=True),
                "session_token": session_token,
            },
            extra_headers={"Set-Cookie": cookie},
        )

    def _handle_app_store_notification(self) -> None:
        payload = self._read_json_body(max_bytes=MAX_NOTIFICATION_BODY_BYTES)
        result = _validate_app_store_notification(payload)
        self._send_json({"ok": True, **result})

    def _handle_pro_report(self) -> None:
        self._require_pro_entitlement()
        payload = self._read_json_body()
        module = str(payload.get("module", "career"))
        if module not in {"career", "wealth", "relationship"}:
            raise ClientInputError("invalid_module", "Unsupported Pro report module.")
        result, traits = _build_and_validate(payload)
        report = _build_pro_report(module, result, traits, language=str(payload.get("language", "en")))
        self._send_json({"ok": True, "report": report})

    def _handle_annual_report(self) -> None:
        self._require_pro_entitlement()
        payload = self._read_json_body()
        result, traits = _build_and_validate(payload)
        years = _int_range(payload.get("annual_report_years", 5), "annual_report_years", 1, 12)
        annual = build_annual_outlook(result, traits, years=years)
        annual_schema = json.loads(annual_schema_path().read_text(encoding="utf-8"))
        Draft202012Validator(annual_schema, format_checker=FormatChecker()).validate(annual)
        self._send_json({"ok": True, "annual": annual})

    def _handle_monthly_compass(self) -> None:
        self._require_pro_entitlement()
        payload = self._read_json_body()
        result, traits = _build_and_validate(payload)
        now = datetime.now()
        start_year = _int_range(payload.get("monthly_start_year", now.year), "monthly_start_year", 1900, 2100)
        start_month = _int_range(payload.get("monthly_start_month", now.month), "monthly_start_month", 1, 12)
        count = _int_range(payload.get("monthly_count", 6), "monthly_count", 1, 12)
        compass = build_monthly_compass(
            result,
            traits,
            start_year=start_year,
            start_month=start_month,
            count=count,
        )
        compass_schema = json.loads(monthly_compass_schema_path().read_text(encoding="utf-8"))
        Draft202012Validator(compass_schema, format_checker=FormatChecker()).validate(compass)
        self._send_json({"ok": True, "compass": compass})

    def _handle_oracle_interpret(self) -> None:
        self._require_pro_entitlement()
        payload = self._read_json_body()
        lines = payload.get("lines")
        if not isinstance(lines, list) or len(lines) != 6 or any(value not in {6, 7, 8, 9} for value in lines):
            raise ClientInputError("invalid_oracle_lines", "Oracle cast must contain six values in 6, 7, 8, or 9.")
        category = str(payload.get("category", "general"))
        horizon = str(payload.get("horizon", "one_month"))
        if category not in ALLOWED_ORACLE_CATEGORIES:
            raise ClientInputError("invalid_oracle_category", "Oracle category is invalid.")
        if horizon not in ALLOWED_ORACLE_HORIZONS:
            raise ClientInputError("invalid_oracle_horizon", "Oracle horizon is invalid.")
        oracle = interpret_cast(lines, category=category, horizon=horizon)
        oracle_schema = json.loads(oracle_schema_path().read_text(encoding="utf-8"))
        Draft202012Validator(oracle_schema, format_checker=FormatChecker()).validate(oracle)
        self._send_json({"ok": True, "oracle": oracle})

    def _check_rate_limit(self, path: str) -> None:
        limit = RATE_LIMITS.get(path)
        if not limit:
            return
        client_ip = self.client_address[0] if self.client_address else "unknown"
        now = time.monotonic()
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        key = (client_ip, path)
        with _RATE_LOCK:
            bucket = [timestamp for timestamp in _RATE_BUCKETS.get(key, []) if timestamp > cutoff]
            if len(bucket) >= limit:
                _RATE_BUCKETS[key] = bucket
                raise RateLimitExceeded()
            bucket.append(now)
            _RATE_BUCKETS[key] = bucket

    def _current_entitlement(self, is_demo_unlocked: bool | None = None) -> dict:
        if is_demo_unlocked is not None:
            return _free_entitlement(can_demo_unlock=self._demo_unlock_enabled(), storekit_ready=False)
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        token = cookie.get(SESSION_COOKIE).value if cookie.get(SESSION_COOKIE) else ""
        claims = _verify_session(token)
        storekit_ready = self._storekit_configured()
        if not claims:
            return _free_entitlement(can_demo_unlock=self._demo_unlock_enabled(), storekit_ready=storekit_ready)
        subject = str(claims.get("sub", ""))
        with _ENTITLEMENT_LOCK:
            record = _ENTITLEMENTS.get(subject)
        if record is None:
            return _free_entitlement(can_demo_unlock=self._demo_unlock_enabled(), storekit_ready=storekit_ready, status="needs_restore")
        if record.source == "local_demo" and not self._demo_unlock_enabled():
            return _free_entitlement(can_demo_unlock=False, storekit_ready=storekit_ready)
        return record.to_public(can_demo_unlock=self._demo_unlock_enabled(), storekit_ready=storekit_ready)

    def _has_pro_entitlement(self) -> bool:
        return self._current_entitlement()["is_pro"]

    def _require_pro_entitlement(self) -> None:
        if not self._has_pro_entitlement():
            raise ClientInputError("pro_required", "An active Pro entitlement is required.", 403)

    def _demo_unlock_enabled(self) -> bool:
        return os.environ.get("BAZI_DEMO_UNLOCK") == "1"

    def _storekit_configured(self) -> bool:
        try:
            AppStoreConfig.from_env()
            return True
        except EntitlementUnavailable:
            return _is_storekit_stub_allowed()

    def _read_json_body(self, *, max_bytes: int = MAX_JSON_BODY_BYTES) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ClientInputError("invalid_content_length", "Content-Length is invalid.") from exc
        if length > max_bytes:
            self.rfile.read(0)
            raise RequestTooLarge()
        if length <= 0:
            raise ClientInputError("empty_request_body", "JSON request body is required.")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ClientInputError("invalid_json", "Request body must be valid JSON.") from exc
        if not isinstance(payload, dict):
            raise ClientInputError("invalid_json", "JSON request body must be an object.")
        return payload

    def _send_json(self, payload: dict, status: int = 200, extra_headers: dict[str, str] | None = None) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)


def _int_range(value: object, field: str, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ClientInputError("invalid_request", f"{field} must be an integer.") from exc
    if parsed < minimum or parsed > maximum:
        raise ClientInputError("invalid_request", f"{field} is out of range.")
    return parsed


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ClientInputError("invalid_request", "Location coordinates must be numbers.") from exc


def _optional_text(value: object, field: str, max_length: int = 80) -> str:
    if value in (None, ""):
        return ""
    text = str(value).strip()
    if len(text) > max_length:
        raise ClientInputError("invalid_request", f"{field} is too long.")
    return text


def _validate_chart_payload(payload: dict[str, Any]) -> None:
    birth_datetime = payload.get("birth_datetime")
    if not isinstance(birth_datetime, str) or len(birth_datetime) < 10 or len(birth_datetime) > 40:
        raise ClientInputError("invalid_request", "birth_datetime is required.")
    try:
        parsed_birth = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ClientInputError("invalid_request", "birth_datetime must be ISO-8601.") from exc
    if parsed_birth.year < 1900 or parsed_birth.year > 2100:
        raise ClientInputError("invalid_request", "birth_datetime is out of supported range.")

    timezone_name = payload.get("timezone")
    if not isinstance(timezone_name, str) or not re.fullmatch(r"[A-Za-z0-9_+./-]{1,64}", timezone_name):
        raise ClientInputError("invalid_request", "timezone is invalid.")
    if payload.get("gender", "unknown") not in {"male", "female", "unknown"}:
        raise ClientInputError("invalid_request", "gender is invalid.")
    if payload.get("calendar", "gregorian") not in {"gregorian", "lunar"}:
        raise ClientInputError("invalid_request", "calendar is invalid.")
    country = _optional_text(payload.get("country"), "country", 3)
    if country and not re.fullmatch(r"[A-Za-z]{2,3}", country):
        raise ClientInputError("invalid_request", "country is invalid.")
    _optional_text(payload.get("region"), "region", 80)
    _optional_text(payload.get("city"), "city", 80)

    longitude = _optional_float(payload.get("longitude"))
    latitude = _optional_float(payload.get("latitude"))
    if longitude is not None and not -180 <= longitude <= 180:
        raise ClientInputError("invalid_request", "longitude is out of range.")
    if latitude is not None and not -90 <= latitude <= 90:
        raise ClientInputError("invalid_request", "latitude is out of range.")
    _int_range(payload.get("annual_years", 12), "annual_years", 1, 20)
    _int_range(payload.get("annual_start_year", datetime.now().year), "annual_start_year", 1900, 2100)
    _int_range(payload.get("luck_cycles", 8), "luck_cycles", 1, 12)


LEVEL_LABELS = {
    "very_prominent": "very prominent",
    "relatively_strong": "relatively strong",
    "moderate": "moderate",
    "relatively_weak": "relatively low",
}

TRAIT_LABELS = {
    "career_momentum": "career momentum",
    "wealth_generation": "opportunity access",
    "wealth_retention": "resource retention",
    "relationship_support": "relationship support",
    "relationship_pressure": "relationship pressure",
    "execution_stability": "execution stability",
    "risk_appetite": "risk appetite",
}

FACTOR_LABELS = {
    "structured_output": "structured output",
    "challenge_drive": "challenge drive",
    "responsibility": "responsibility",
    "expressive_output": "expressive output",
    "analysis_delay": "analysis delay",
    "practical_follow_through": "practical follow-through",
    "steady_output": "steady output",
    "rule_awareness": "rule awareness",
    "rule_friction": "rule friction",
    "priority_competition": "priority competition",
    "structured_learning": "structured learning",
    "pattern_learning": "pattern learning",
    "support_dependence": "support dependence",
    "boundary_pressure": "boundary pressure",
    "resource_leakage": "resource leakage",
    "relationship_load": "relationship load",
}


def _trait(traits: dict[str, Any], key: str) -> dict[str, Any]:
    return traits.get("traits", {}).get(key, {"score": 0, "level": "moderate", "confidence": 0, "evidence_ids": []})


def _trait_level(traits: dict[str, Any], key: str) -> str:
    level = str(_trait(traits, key).get("level", "moderate"))
    return LEVEL_LABELS.get(level, level.replace("_", " "))


def _factor_summary(traits: dict[str, Any], key: str, direction: str) -> str:
    factors = _trait(traits, key).get(f"{direction}_factors", [])
    labels = [FACTOR_LABELS.get(str(item.get("label_key")), str(item.get("label_key"))) for item in factors[:3]]
    return ", ".join(label for label in labels if label) or "no single dominant factor"


def _report_common_metrics(core: dict[str, Any], traits: dict[str, Any]) -> dict[str, Any]:
    context = traits.get("context", {})
    annual = ", ".join(
        f"{item['year']} {item['pillar']['stem']['char']}{item['pillar']['branch']['char']}"
        for item in core.get("annual_flows", [])[:3]
    )
    main_reminder = str(context.get("main_reminder", "execution_stability"))
    return {
        "strongest_element": context.get("strongest_element", "balanced"),
        "strongest_ten_god": context.get("strongest_ten_god", "mixed"),
        "main_reminder": TRAIT_LABELS.get(main_reminder, main_reminder.replace("_", " ")),
        "annual": annual,
        "evidence_count": len(core.get("evidence", [])),
    }


def _build_pro_report(module: str, core: dict[str, Any], traits: dict[str, Any], *, language: str = "en") -> dict[str, Any]:
    metrics = _report_common_metrics(core, traits)
    module_data = {
        "career": {
            "title": "Career Pro Structured Report",
            "intro": "This server-generated report separates work drive, delivery style, evidence, risk boundary, and a practical plan. It is a reflection tool, not a career prediction.",
            "primary_trait": "career_momentum",
            "secondary_trait": "execution_stability",
            "actions": [
                "Define one deliverable that can be reviewed this week.",
                "Write the acceptance standard before starting the work.",
                "Reserve one weekly review slot for output, feedback, and scope changes.",
                "Turn repeatable work into a case, process, or portfolio artifact.",
            ],
        },
        "wealth": {
            "title": "Money and Resources Pro Structured Report",
            "intro": "This server-generated report separates opportunity access, retention pressure, decision boundaries, and reviewable resource choices. It does not forecast income.",
            "primary_trait": "wealth_generation",
            "secondary_trait": "wealth_retention",
            "actions": [
                "Classify each major decision as income potential, necessary cost, or impulse spend.",
                "Set a budget cap, validation window, and exit condition before committing.",
                "Wait one night before large irreversible resource decisions.",
                "Review opportunities monthly by actual result, not by initial excitement.",
            ],
        },
        "relationship": {
            "title": "Relationship Pro Structured Report",
            "intro": "This server-generated report separates support, pressure, communication rhythm, and explicit requests. It does not decide relationship outcomes.",
            "primary_trait": "relationship_support",
            "secondary_trait": "relationship_pressure",
            "actions": [
                "Separate the fact, your interpretation, and the request before important conversations.",
                "Name one expectation as a concrete action, timing, or boundary.",
                "Confirm what the other person can realistically offer.",
                "Reduce repeated guessing before deciding whether to invest more energy.",
            ],
        },
    }[module]
    primary = module_data["primary_trait"]
    secondary = module_data["secondary_trait"]
    primary_level = _trait_level(traits, primary)
    secondary_level = _trait_level(traits, secondary)
    evidence_ids = sorted(set(_trait(traits, primary).get("evidence_ids", []) + _trait(traits, secondary).get("evidence_ids", [])))
    blocks = [
        {
            "title": "Core Profile",
            "body": (
                f"The strongest visible entry point is {metrics['strongest_element']} with {metrics['strongest_ten_god']}. "
                f"For this module, {TRAIT_LABELS.get(primary, primary)} is {primary_level} and "
                f"{TRAIT_LABELS.get(secondary, secondary)} is {secondary_level}."
            ),
        },
        {
            "title": "Why This Pattern Appears",
            "body": (
                f"Supporting factors include {_factor_summary(traits, primary, 'positive')}. "
                f"Constraining factors include {_factor_summary(traits, secondary, 'negative')}. "
                "The engine keeps support and constraint separate before turning them into advice."
            ),
        },
        {
            "title": "Risk Boundary",
            "body": (
                f"The main watch point is {metrics['main_reminder']}. Treat this as a place to set scope, "
                "cost, timing, or communication boundaries before the situation becomes expensive to revise."
            ),
        },
        {
            "title": "Timing Lens",
            "body": (
                f"The next annual reference points are {metrics['annual'] or 'not available'}. "
                "Use them as review checkpoints for experiments, commitments, and course correction rather than fixed outcomes."
            ),
        },
        {
            "title": "Practical Plan",
            "body": "Choose one reversible action, write the success condition, record the result, and adjust from evidence instead of mood.",
        },
    ]
    return {
        "schema_version": "1.0.0",
        "model_version": "pro-report-v1",
        "module": module,
        "language": "zh" if language.lower().startswith("zh") else "en",
        "title": module_data["title"],
        "intro": module_data["intro"],
        "badges": ["Server generated", "Rules engine", "No fixed prediction"],
        "summary": [
            {"label": "Primary signal", "title": TRAIT_LABELS.get(primary, primary), "body": primary_level},
            {"label": "Boundary", "title": metrics["main_reminder"], "body": "Make this explicit before committing."},
            {"label": "Evidence", "title": f"{len(evidence_ids)} linked signals", "body": f"{metrics['evidence_count']} core evidence items available."},
            {"label": "Next step", "title": "Small test", "body": module_data["actions"][0]},
        ],
        "blocks": blocks,
        "actions": module_data["actions"],
        "evidence": {
            "body": f"This report references {len(evidence_ids)} trait evidence ids and {metrics['evidence_count']} core calculation evidence items.",
            "evidence_ids": evidence_ids,
        },
    }


def _build_and_validate(payload: dict) -> tuple[dict, dict]:
    _validate_chart_payload(payload)
    result = build_core_output(
        birth_datetime=payload["birth_datetime"],
        timezone=payload["timezone"],
        gender=payload.get("gender", "unknown"),
        calendar=payload.get("calendar", "gregorian"),
        country=payload.get("country", ""),
        region=payload.get("region", ""),
        city=payload.get("city", ""),
        longitude=_optional_float(payload.get("longitude")),
        latitude=_optional_float(payload.get("latitude")),
        use_true_solar_time=bool(payload.get("use_true_solar_time", False)),
        annual_years=_int_range(payload.get("annual_years", 12), "annual_years", 1, 20),
        annual_start_year=_int_range(payload.get("annual_start_year", datetime.now().year), "annual_start_year", 1900, 2100),
        luck_cycles=_int_range(payload.get("luck_cycles", 8), "luck_cycles", 1, 12),
    )
    schema = json.loads(schema_path().read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(result)
    traits = build_trait_output(result)
    trait_schema = json.loads(trait_schema_path().read_text(encoding="utf-8"))
    Draft202012Validator(trait_schema, format_checker=FormatChecker()).validate(traits)
    return result, traits


def main() -> None:
    host = "127.0.0.1"
    port = int(os.environ.get("BAZI_PORT", "8787"))
    server = ExclusiveThreadingHTTPServer((host, port), BaziHandler)
    if sys.stdout is not None:
        print(f"BaziCore test system running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if sys.stderr is None:
            import traceback

            (ROOT / "server-startup-error.log").write_text(
                traceback.format_exc(),
                encoding="utf-8",
            )
        raise
