import http.client
import threading
import unittest
from pathlib import Path

import server


WEB_ROOT = Path("web")


class WebStaticStructureTests(unittest.TestCase):
    def test_index_is_shell_with_external_assets(self):
        html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<style>", html)
        self.assertNotIn("<script>", html)
        for asset in [
            "/styles/tokens-v20260824.css",
            "/styles/base-v20260824.css",
            "/styles/components-v20260824.css",
            "/styles/responsive-v20260824.css",
            "/js/state-v20260824.js",
            "/js/storage-v20260824.js",
            "/js/api-v20260824.js",
            "/js/analytics-v20260824.js",
            "/js/locales-v20260824.js",
            "/js/app-v20260824.js",
        ]:
            self.assertIn(asset, html)

    def test_primary_navigation_is_four_entry_model(self):
        html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        for target in ["today", "blueprint", "oracle", "me"]:
            self.assertIn(f'data-mobile-target="{target}"', html)
        self.assertNotIn('data-mobile-target="pro"', html)
        self.assertNotIn('data-mobile-target="overview"', html)
        self.assertNotIn('data-mobile-target="chart"', html)

    def test_locales_and_modules_are_split_from_app(self):
        app = (WEB_ROOT / "js" / "app-v20260824.js").read_text(encoding="utf-8")
        self.assertNotIn("const copy = {", app)
        self.assertIn("window.MINGApi.fetchJson", app)
        self.assertIn("window.MINGAnalytics.record", app)
        self.assertTrue((WEB_ROOT / "locales" / "zh-CN.json").exists())
        self.assertTrue((WEB_ROOT / "locales" / "en-US.json").exists())

    def test_versioned_static_assets_get_long_cache(self):
        httpd = server.ExclusiveThreadingHTTPServer(("127.0.0.1", 0), server.BaziHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=10)
            conn.request("GET", "/js/app-v20260824.js")
            response = conn.getresponse()
            response.read()
            conn.close()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.getheader("Cache-Control"), "public, max-age=31536000, immutable")
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
