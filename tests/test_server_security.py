import http.client
import json
import os
import threading
import unittest
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
        server._RATE_BUCKETS.clear()
        server._ENTITLEMENTS.clear()
        self.httpd = server.ExclusiveThreadingHTTPServer(("127.0.0.1", 0), server.BaziHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)

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
            "BAZI_STOREKIT_STUB": "",
            "BAZI_ALLOW_INSECURE_STOREKIT_STUB": "",
        }
        with patch.dict(os.environ, env_clear, clear=False):
            status, _, body = self.post(
                "/api/app-store/transactions",
                {"signed_transaction": "aaa.bbb.ccc"},
            )
        payload = json.loads(body)
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "app_store_validation_not_configured")
        self.assertFalse(payload["entitlement"]["is_pro"])

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


if __name__ == "__main__":
    unittest.main()
