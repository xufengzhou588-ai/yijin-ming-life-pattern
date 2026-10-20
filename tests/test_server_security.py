import http.client
import json
import os
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import server


VALID_CHART = {
    "birth_datetime": "1990-05-17T08:30:00+08:00",
    "timezone": "Asia/Shanghai",
    "gender": "male",
    "country": "CN",
    "region": "Shanghai",
    "city": "Shanghai",
    "longitude": 121.4737,
    "latitude": 31.2304,
    "annual_years": 5,
    "annual_start_year": 2026,
    "luck_cycles": 4,
}


class ServerSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_patcher = patch.dict(
            os.environ,
            {"BAZI_ENTITLEMENT_DB_PATH": os.path.join(self.temp_dir.name, "entitlements.sqlite3")},
            clear=False,
        )
        self.env_patcher.start()
        server._RATE_BUCKETS.clear()
        server._ENTITLEMENTS.clear()
        server._ANALYTICS_EVENT_IDS.clear()
        self.httpd = server.ExclusiveThreadingHTTPServer(("127.0.0.1", 0), server.BaziHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        self.env_patcher.stop()
        self.temp_dir.cleanup()

    def get(self, path, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("GET", path, headers=headers or {})
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response.status, response.getheaders(), data

    def post(self, path, payload=None, headers=None, raw_body=None):
        body = raw_body if raw_body is not None else json.dumps(payload or {}).encode("utf-8")
        request_headers = {"Content-Type": "application/json", "Content-Length": str(len(body))}
        request_headers.update(headers or {})
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("POST", path, body=body, headers=request_headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response.status, response.getheaders(), data

    def get(self, path, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("GET", path, headers=headers or {})
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response.status, response.getheaders(), data

    def test_forged_native_pro_cookie_cannot_access_pro_endpoints(self):
        cases = [
            ("/api/pro/annual-report", {**VALID_CHART, "annual_report_years": 1}),
            ("/api/pro/report", {**VALID_CHART, "module": "career"}),
        ]
        for path, request in cases:
            with self.subTest(path=path):
                status, _, body = self.post(
                    path,
                    request,
                    headers={"Cookie": "bazi_native_pro=1"},
                )
                payload = json.loads(body)
                self.assertEqual(status, 403)
                self.assertEqual(payload["error"], "pro_required")

    def test_legacy_native_pro_cookie_is_not_an_entitlement_source(self):
        status, headers, body = self.get("/api/entitlement", headers={"Cookie": "bazi_native_pro=1"})
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertFalse(payload["entitlement"]["is_pro"])
        self.assertEqual(payload["entitlement"]["tier"], "free")
        self.assertEqual(dict(headers).get("X-Content-Type-Options"), "nosniff")

    def test_forged_bazi_session_cookie_cannot_access_pro_endpoints(self):
        claims = {
            "sub": "app:00000000-0000-0000-0000-000000000000",
            "source": "app_store",
            "product_id": "ming.pro.yearly",
            "iat": int(time.time()),
            "exp": int(time.time()) + server.PRO_SESSION_SECONDS,
        }
        forged = f"{server._base64url(json.dumps(claims).encode('utf-8'))}.not-a-valid-signature"
        status, _, body = self.post(
            "/api/pro/monthly-compass",
            VALID_CHART,
            headers={"Cookie": f"{server.SESSION_COOKIE}={forged}"},
        )
        payload = json.loads(body)
        self.assertEqual(status, 403)
        self.assertEqual(payload["error"], "pro_required")

    def test_persisted_pro_entitlement_survives_memory_cache_clear(self):
        record = server._store_entitlement(
            server.EntitlementRecord(
                subject="app:11111111-1111-1111-1111-111111111111",
                status="pro_active",
                is_pro=True,
                source="app_store",
                environment="sandbox",
                product_id="ming.pro.yearly",
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                transaction_id="1000000001",
                original_transaction_id="1000000000",
                app_account_token="11111111-1111-1111-1111-111111111111",
                anonymous_install_id="22222222-2222-2222-2222-222222222222",
            )
        )
        _, cookie = server._issue_session(record)
        server._ENTITLEMENTS.clear()

        status, _, body = self.get("/api/entitlement", headers={"Cookie": cookie.split(";", 1)[0]})
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertTrue(payload["entitlement"]["is_pro"])
        self.assertEqual(payload["entitlement"]["source"], "app_store")

    def test_expired_persisted_entitlement_requires_restore(self):
        record = server._store_entitlement(
            server.EntitlementRecord(
                subject="tx:2000000000",
                status="expired",
                is_pro=False,
                source="app_store",
                environment="sandbox",
                product_id="ming.pro.monthly",
                expires_at=datetime.now(timezone.utc) - timedelta(days=1),
                transaction_id="2000000001",
                original_transaction_id="2000000000",
            )
        )
        _, cookie = server._issue_session(record)
        server._ENTITLEMENTS.clear()

        status, _, body = self.get("/api/entitlement", headers={"Cookie": cookie.split(";", 1)[0]})
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertFalse(payload["entitlement"]["is_pro"])
        self.assertEqual(payload["entitlement"]["status"], "expired")
        self.assertTrue(payload["entitlement"]["needs_restore"])

    def test_unsupported_storekit_product_is_forbidden(self):
        class DecodedTransaction:
            productId = "ming.pro.fake"
            expiresDate = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp() * 1000)
            revocationDate = None
            environment = "sandbox"
            transactionId = "3000000001"
            originalTransactionId = "3000000000"
            appAccountToken = None

        with self.assertRaises(server.ClientInputError) as context:
            server._record_from_transaction(DecodedTransaction(), status=1)
        self.assertEqual(context.exception.status, 403)
        self.assertEqual(context.exception.error, "unsupported_product")

    def test_production_config_status_reports_missing_release_requirements(self):
        missing_production_env = {
            "MING_PRO_MODE": "storekit",
            "APP_STORE_ENVIRONMENT": "production",
            "APP_STORE_ISSUER_ID": "",
            "APP_STORE_KEY_ID": "",
            "APP_STORE_PRIVATE_KEY": "",
            "APP_STORE_PRIVATE_KEY_PATH": "",
            "APP_STORE_ROOT_CERT_PATHS": "",
            "APP_STORE_APP_APPLE_ID": "",
            "BAZI_SESSION_SECRET": "short",
            "BAZI_COOKIE_SECURE": "0",
            "BAZI_DEMO_UNLOCK": "1",
            "BAZI_STOREKIT_STUB": "",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "",
        }
        with patch.dict(os.environ, missing_production_env, clear=False):
            status, _, body = self.get("/api/system/status")
        payload = json.loads(body)
        missing = set(payload["deployment"]["missing"])
        self.assertEqual(status, 200)
        self.assertFalse(payload["deployment"]["production_ready"])
        self.assertIn("APP_STORE_ISSUER_ID", missing)
        self.assertIn("APP_STORE_APP_APPLE_ID", missing)
        self.assertIn("BAZI_SESSION_SECRET>=32", missing)
        self.assertIn("BAZI_COOKIE_SECURE=1", missing)
        self.assertIn("BAZI_DEMO_UNLOCK disabled", missing)

    def test_free_first_production_config_skips_storekit_requirements(self):
        free_first_env = {
            "MING_PRO_MODE": "free_first",
            "APP_STORE_ENVIRONMENT": "production",
            "APP_STORE_ISSUER_ID": "",
            "APP_STORE_KEY_ID": "",
            "APP_STORE_PRIVATE_KEY": "",
            "APP_STORE_PRIVATE_KEY_PATH": "",
            "APP_STORE_ROOT_CERT_PATHS": "",
            "APP_STORE_APP_APPLE_ID": "",
            "BAZI_SESSION_SECRET": "free-first-release-session-secret-2026",
            "BAZI_COOKIE_SECURE": "1",
            "BAZI_DEMO_UNLOCK": "",
            "BAZI_STOREKIT_STUB": "",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "",
            "BAZI_ENTITLEMENT_DB_PATH": "",
        }
        with patch.dict(os.environ, free_first_env, clear=False):
            status, _, body = self.get("/api/system/status")
        payload = json.loads(body)
        deployment = payload["deployment"]
        self.assertEqual(status, 200)
        self.assertTrue(deployment["production_ready"])
        self.assertEqual(deployment["missing"], [])
        self.assertEqual(deployment["pro_mode"], "free_first")
        self.assertFalse(deployment["storekit_required"])
        self.assertFalse(deployment["storekit_configured"])

    def test_request_body_size_limit(self):
        body = b'{"payload":"' + (b"x" * (server.MAX_JSON_BODY_BYTES + 1)) + b'"}'
        status, _, data = self.post("/api/generate", raw_body=body)
        payload = json.loads(data)
        self.assertEqual(status, 413)
        self.assertEqual(payload["error"], "request_body_too_large")

    def test_parameter_range_limit(self):
        request = {**VALID_CHART, "annual_years": 999}
        status, _, body = self.post("/api/generate", request)
        payload = json.loads(body)
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "invalid_request")
        self.assertNotIn("Traceback", body.decode("utf-8"))

    def test_server_address_uses_platform_port_for_hosted_deployments(self):
        with patch.dict(os.environ, {"PORT": "10000"}, clear=True):
            self.assertEqual(server._server_address(), ("0.0.0.0", 10000))

    def test_server_address_keeps_localhost_default_for_local_development(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(server._server_address(), ("127.0.0.1", 8787))

    def test_internal_exception_is_sanitized(self):
        with patch.object(server, "build_core_output", side_effect=RuntimeError("secret stack detail")):
            status, _, body = self.post("/api/generate", VALID_CHART)
        payload = json.loads(body)
        self.assertEqual(status, 500)
        self.assertEqual(payload["error"], "internal_error")
        self.assertNotIn("secret stack detail", body.decode("utf-8"))

    def test_app_store_validation_unconfigured_is_503_not_501(self):
        env_clear = {
            "APP_STORE_ISSUER_ID": "",
            "APP_STORE_KEY_ID": "",
            "APP_STORE_PRIVATE_KEY": "",
            "APP_STORE_PRIVATE_KEY_PATH": "",
            "APP_STORE_ROOT_CERT_PATHS": "",
            "APP_STORE_ENVIRONMENT": "sandbox",
            "APP_STORE_APP_APPLE_ID": "",
            "BAZI_STOREKIT_STUB": "",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "",
        }
        with patch.dict(os.environ, env_clear, clear=False):
            status, headers, body = self.post(
                "/api/app-store/transactions",
                {"signed_transaction": "aaa.bbb.ccc"},
            )
        payload = json.loads(body)
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "app_store_validation_not_configured")
        self.assertFalse(payload["entitlement"]["is_pro"])
        self.assertIn("Max-Age=0", dict(headers).get("Set-Cookie", ""))

    def test_storekit_stub_success_issues_server_session_for_sandbox_only(self):
        env = {
            "BAZI_STOREKIT_STUB": "1",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "1",
            "APP_STORE_ENVIRONMENT": "sandbox",
        }
        with patch.dict(os.environ, env, clear=False):
            status, headers, body = self.post(
                "/api/app-store/transactions",
                {
                    "signed_transaction": "aaa.bbb.ccc",
                    "app_account_token": "00000000-0000-4000-8000-000000000001",
                    "anonymous_install_id": "00000000-0000-4000-8000-000000000002",
                },
            )

        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertTrue(payload["entitlement"]["is_pro"])
        self.assertEqual(payload["entitlement"]["status"], "pro_active")
        self.assertEqual(payload["entitlement"]["product_id"], "ming.pro.yearly")
        self.assertEqual(payload["entitlement"]["environment"], "sandbox")
        self.assertIn("session_token", payload)
        cookie = dict(headers).get("Set-Cookie", "")
        self.assertIn("bazi_session=", cookie)

        status, _, body = self.post(
            "/api/pro/monthly-compass",
            {**VALID_CHART, "monthly_count": 1},
            headers={"Cookie": cookie.split(";", 1)[0]},
        )
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])

    def test_storekit_stub_is_blocked_in_production_environment(self):
        env = {
            "BAZI_STOREKIT_STUB": "1",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "1",
            "APP_STORE_ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, env, clear=False):
            status, headers, body = self.post(
                "/api/app-store/transactions",
                {"signed_transaction": "aaa.bbb.ccc"},
            )

        payload = json.loads(body)
        self.assertEqual(status, 503)
        self.assertFalse(payload["entitlement"]["is_pro"])
        self.assertIn("Max-Age=0", dict(headers).get("Set-Cookie", ""))

    def test_expired_storekit_entitlement_requires_restore_and_locks_pro(self):
        record = server._store_entitlement(
            server.EntitlementRecord(
                subject="app:00000000-0000-4000-8000-000000000003",
                status="expired",
                is_pro=False,
                source="app_store",
                environment="sandbox",
                product_id="ming.pro.monthly",
                expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
                original_transaction_id="100000000000001",
                app_account_token="00000000-0000-4000-8000-000000000003",
            )
        )
        _, cookie = server._issue_session(record)

        with patch.dict(os.environ, {"APP_STORE_ENVIRONMENT": "sandbox"}, clear=False):
            status, _, body = self.get("/api/entitlement", headers={"Cookie": cookie.split(";", 1)[0]})
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(payload["entitlement"]["status"], "expired")
        self.assertFalse(payload["entitlement"]["is_pro"])
        self.assertTrue(payload["entitlement"]["needs_restore"])
        self.assertIsNone(payload["entitlement"]["product_id"])

        status, _, body = self.post(
            "/api/pro/report",
            {**VALID_CHART, "module": "career"},
            headers={"Cookie": cookie.split(";", 1)[0]},
        )
        self.assertEqual(status, 403)
        self.assertEqual(json.loads(body)["error"], "pro_required")

    def test_invalid_or_cancelled_purchase_payload_does_not_issue_entitlement(self):
        status, headers, body = self.post(
            "/api/app-store/transactions",
            {"signed_transaction": "not-a-jws"},
        )
        payload = json.loads(body)
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "invalid_signed_transaction")
        self.assertEqual(dict(headers).get("Set-Cookie"), None)
        self.assertEqual(server._ENTITLEMENTS, {})

    def test_storekit_transaction_status_mapping(self):
        active = _FakeDecodedTransaction(
            product_id="ming.pro.monthly",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            status=1,
        )
        expired = _FakeDecodedTransaction(
            product_id="ming.pro.monthly",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            status=2,
        )
        revoked = _FakeDecodedTransaction(
            product_id="ming.pro.yearly",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            revocation_at=datetime.now(timezone.utc),
            status=5,
        )
        billing_retry = _FakeDecodedTransaction(
            product_id="ming.pro.yearly",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status=3,
        )

        self.assertEqual(server._record_from_transaction(active, status=1).to_public()["status"], "pro_active")
        self.assertEqual(server._record_from_transaction(expired, status=2).to_public()["status"], "expired")
        self.assertEqual(server._record_from_transaction(revoked, status=5).to_public()["status"], "revoked")
        self.assertEqual(server._record_from_transaction(billing_retry, status=3).to_public()["status"], "needs_restore")

    def test_unsupported_storekit_product_is_rejected(self):
        with self.assertRaises(server.ClientInputError) as context:
            server._record_from_transaction(_FakeDecodedTransaction(product_id="ming.fake.monthly"))
        self.assertEqual(context.exception.error, "unsupported_product")
        self.assertEqual(context.exception.status, 403)

    def test_signed_demo_session_is_required_when_demo_unlock_is_enabled(self):
        with patch.dict(os.environ, {"BAZI_DEMO_UNLOCK": "1"}, clear=False):
            status, headers, body = self.post("/api/entitlement/demo-unlock", {})
            self.assertEqual(status, 200)
            payload = json.loads(body)
            self.assertTrue(payload["entitlement"]["is_pro"])
            cookie = dict(headers).get("Set-Cookie", "")
            self.assertIn("bazi_session=", cookie)

            status, _, body = self.post(
                "/api/pro/annual-report",
                {**VALID_CHART, "annual_report_years": 1},
                headers={"Cookie": cookie.split(";", 1)[0]},
            )
            self.assertEqual(status, 200)
            self.assertTrue(json.loads(body)["ok"])

            forged = cookie.split(";", 1)[0] + "x"
            status, _, body = self.post(
                "/api/pro/annual-report",
                {**VALID_CHART, "annual_report_years": 1},
                headers={"Cookie": forged},
            )
            self.assertEqual(status, 403)
            self.assertEqual(json.loads(body)["error"], "pro_required")

    def test_anonymous_analytics_ingest_sanitizes_pii_and_dedupes(self):
        event = {
            "event_id": "11111111-1111-4111-8111-111111111111",
            "schema_version": "analytics-events-v2",
            "name": "first_open",
            "created_at": "2026-08-25T01:00:00Z",
            "anonymous_install_id": "22222222-2222-4222-8222-222222222222",
            "anonymous_session_id": "33333333-3333-4333-8333-333333333333",
            "sequence": 1,
            "release_channel": "testflight",
            "region_scope": "us_testflight",
            "experiment": {
                "key": "us_testflight_paywall_copy",
                "variant": "control",
                "bucket": 12,
            },
            "metadata": {
                "language": "en",
                "surface": "ios",
                "module": "pro_tab",
                "birth_date": "1990-05-17",
                "country": "US",
                "email": "tester@example.com",
                "question": "Will this text leak?",
            },
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"BAZI_ANALYTICS_DIR": directory, "BAZI_ANALYTICS_DISABLED": ""},
            clear=False,
        ):
            status, _, body = self.post("/api/analytics/events", {"schema_version": "analytics-events-v2", "events": [event, event]})
            payload = json.loads(body)
            self.assertEqual(status, 200)
            self.assertEqual(payload["accepted"], 1)

            stored_files = list(os.scandir(directory))
            self.assertEqual(len(stored_files), 1)
            with open(stored_files[0].path, encoding="utf-8") as handle:
                stored = json.loads(handle.read())
            self.assertEqual(stored["name"], "first_open")
            self.assertEqual(stored["anonymous_install_id"], event["anonymous_install_id"])
            self.assertEqual(stored["region_scope"], "us_testflight")
            self.assertEqual(stored["metadata"], {"language": "en", "surface": "ios", "module": "pro_tab"})
            serialized = json.dumps(stored)
            self.assertNotIn("1990-05-17", serialized)
            self.assertNotIn("tester@example.com", serialized)
            self.assertNotIn("Will this text leak?", serialized)

    def test_anonymous_analytics_disabled_is_non_blocking(self):
        event = {
            "event_id": "44444444-4444-4444-8444-444444444444",
            "schema_version": "analytics-events-v2",
            "name": "paywall_view",
            "anonymous_install_id": "55555555-5555-4555-8555-555555555555",
            "anonymous_session_id": "66666666-6666-4666-8666-666666666666",
            "sequence": 1,
            "release_channel": "testflight",
            "region_scope": "us_testflight",
            "metadata": {"surface": "native_pro"},
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"BAZI_ANALYTICS_DIR": directory, "BAZI_ANALYTICS_DISABLED": "1"},
            clear=False,
        ):
            status, _, body = self.post("/api/analytics/events", {"schema_version": "analytics-events-v2", "events": [event]})
            payload = json.loads(body)
            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["accepted"], 0)
            self.assertEqual(os.listdir(directory), [])


class _FakeDecodedTransaction:
    def __init__(
        self,
        *,
        product_id,
        expires_at=None,
        revocation_at=None,
        status=None,
    ):
        self.productId = product_id
        self.expiresDate = _millis(expires_at)
        self.revocationDate = _millis(revocation_at)
        self.environment = "Sandbox"
        self.transactionId = "100000000000002"
        self.originalTransactionId = "100000000000001"
        self.appAccountToken = "00000000-0000-4000-8000-000000000004"
        self.status = status


def _millis(value):
    if value is None:
        return None
    return int(value.timestamp() * 1000)


if __name__ == "__main__":
    unittest.main()
