from __future__ import annotations

import json
import mimetypes
import os
import socket
import sys
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
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


class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class BaziHandler(BaseHTTPRequestHandler):
    server_version = "BaziCoreHTTP/0.1"

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
        if path == "/api/entitlement/demo-unlock":
            if not self._demo_unlock_enabled():
                self._send_json({"ok": False, "error": "demo_unlock_disabled"}, status=403)
                return
            self._send_json(
                {
                    "ok": True,
                    "entitlement": self._current_entitlement(is_demo_unlocked=True),
                },
                extra_headers={"Set-Cookie": "bazi_demo_pro=1; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400"},
            )
            return
        if path == "/api/entitlement/demo-lock":
            if not self._demo_unlock_enabled():
                self._send_json({"ok": False, "error": "demo_unlock_disabled"}, status=403)
                return
            self._send_json(
                {
                    "ok": True,
                    "entitlement": self._current_entitlement(is_demo_unlocked=False),
                },
                extra_headers={"Set-Cookie": "bazi_demo_pro=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"},
            )
            return
        if path == "/api/app-store/transactions":
            try:
                payload = self._read_json_body()
                if not payload.get("signed_transaction"):
                    self._send_json({"ok": False, "error": "missing_signed_transaction"}, status=400)
                    return
                if os.environ.get("BAZI_STOREKIT_STUB") == "1":
                    self._send_json({"ok": True, "entitlement": self._storekit_stub_entitlement()})
                    return
                self._send_json(
                    {
                        "ok": False,
                        "error": "app_store_validation_not_configured",
                        "message": "Configure App Store Server API validation before production.",
                    },
                    status=501,
                )
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
            return
        if path == "/api/pro/annual-report":
            if not self._has_pro_entitlement():
                self._send_json({"ok": False, "error": "pro_required"}, status=403)
                return
            try:
                payload = self._read_json_body()
                result, traits = _build_and_validate(payload)
                annual = build_annual_outlook(result, traits, years=min(int(payload.get("annual_report_years", 5)), 12))
                annual_schema = json.loads(annual_schema_path().read_text(encoding="utf-8"))
                Draft202012Validator(annual_schema, format_checker=FormatChecker()).validate(annual)
                self._send_json({"ok": True, "annual": annual})
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
            return
        if path == "/api/pro/monthly-compass":
            if not self._has_pro_entitlement():
                self._send_json({"ok": False, "error": "pro_required"}, status=403)
                return
            try:
                payload = self._read_json_body()
                result, traits = _build_and_validate(payload)
                start_year = int(payload.get("monthly_start_year", datetime.now().year))
                start_month = int(payload.get("monthly_start_month", datetime.now().month))
                compass = build_monthly_compass(
                    result,
                    traits,
                    start_year=start_year,
                    start_month=start_month,
                    count=min(int(payload.get("monthly_count", 6)), 12),
                )
                compass_schema = json.loads(monthly_compass_schema_path().read_text(encoding="utf-8"))
                Draft202012Validator(compass_schema, format_checker=FormatChecker()).validate(compass)
                self._send_json({"ok": True, "compass": compass})
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
            return
        if path == "/api/oracle/interpret":
            if not self._has_pro_entitlement():
                self._send_json({"ok": False, "error": "pro_required"}, status=403)
                return
            try:
                payload = self._read_json_body()
                oracle = interpret_cast(
                    payload["lines"],
                    category=payload.get("category", "general"),
                    horizon=payload.get("horizon", "one_month"),
                )
                oracle_schema = json.loads(oracle_schema_path().read_text(encoding="utf-8"))
                Draft202012Validator(oracle_schema, format_checker=FormatChecker()).validate(oracle)
                self._send_json({"ok": True, "oracle": oracle})
            except Exception as exc:
                self._send_json({"ok": False, "error": str(exc)}, status=400)
            return
        if path != "/api/generate":
            self._send_json({"error": "not_found"}, status=404)
            return

        try:
            payload = self._read_json_body()
            result, traits = _build_and_validate(payload)
            self._send_json({"ok": True, "result": result, "traits": traits, "system": build_system_status()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)

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

    def _current_entitlement(self, is_demo_unlocked: bool | None = None) -> dict:
        active = self._has_native_pro_entitlement()
        if not active:
            if is_demo_unlocked is None:
                active = self._demo_unlock_enabled() and self._has_demo_pro_entitlement()
            else:
                active = self._demo_unlock_enabled() and is_demo_unlocked
        now = datetime.now(timezone.utc)
        return {
            "status": "pro_active" if active else "free",
            "is_pro": active,
            "tier": "pro" if active else "free",
            "source": "native_storekit" if self._has_native_pro_entitlement() else "local_demo",
            "environment": "app" if self._has_native_pro_entitlement() else "web_test",
            "product_id": "ming.pro.yearly" if active else None,
            "expires_at": (now + timedelta(days=1)).isoformat() if active else None,
            "needs_restore": False,
            "can_demo_unlock": self._demo_unlock_enabled(),
            "storekit_ready": False,
        }

    def _has_pro_entitlement(self) -> bool:
        return self._current_entitlement()["is_pro"]

    def _storekit_stub_entitlement(self) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "status": "pro_active",
            "is_pro": True,
            "tier": "pro",
            "source": "app_store_stub",
            "environment": "sandbox",
            "product_id": "ming.pro.yearly",
            "expires_at": (now + timedelta(days=365)).isoformat(),
            "needs_restore": False,
            "can_demo_unlock": False,
            "storekit_ready": False,
        }

    def _has_demo_pro_entitlement(self) -> bool:
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        return cookie.get("bazi_demo_pro") is not None and cookie["bazi_demo_pro"].value == "1"

    def _has_native_pro_entitlement(self) -> bool:
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        return cookie.get("bazi_native_pro") is not None and cookie["bazi_native_pro"].value == "1"

    def _demo_unlock_enabled(self) -> bool:
        return os.environ.get("BAZI_DEMO_UNLOCK") == "1"

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

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


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _build_and_validate(payload: dict) -> tuple[dict, dict]:
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
        annual_years=int(payload.get("annual_years", 12)),
        annual_start_year=int(payload.get("annual_start_year", datetime.now().year)),
        luck_cycles=int(payload.get("luck_cycles", 8)),
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
