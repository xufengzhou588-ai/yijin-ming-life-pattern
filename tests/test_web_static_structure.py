import http.client
import json
import threading
import unittest
from pathlib import Path

import server


WEB_ROOT = Path("web")
ASSET_VERSION = "v20260826"


class WebStaticStructureTests(unittest.TestCase):
    def test_index_is_shell_with_external_assets(self):
        html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<style>", html)
        self.assertNotIn("<script>", html)
        for asset in [
            f"/styles/tokens-{ASSET_VERSION}.css",
            f"/styles/base-{ASSET_VERSION}.css",
            f"/styles/components-{ASSET_VERSION}.css",
            f"/styles/responsive-{ASSET_VERSION}.css",
            f"/js/state-{ASSET_VERSION}.js",
            f"/js/storage-{ASSET_VERSION}.js",
            f"/js/api-{ASSET_VERSION}.js",
            f"/js/analytics-{ASSET_VERSION}.js",
            f"/js/locales-{ASSET_VERSION}.js",
            f"/js/app-{ASSET_VERSION}.js",
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
        app = (WEB_ROOT / "js" / f"app-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        self.assertNotIn("const copy = {", app)
        self.assertIn("window.MINGApi.fetchJson", app)
        self.assertIn("window.MINGAnalytics.record", app)
        self.assertTrue((WEB_ROOT / "locales" / "zh-CN.json").exists())
        self.assertTrue((WEB_ROOT / "locales" / "en-US.json").exists())

    def test_today_retention_loop_and_muyu_reset_are_present(self):
        app = (WEB_ROOT / "js" / f"app-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        state = (WEB_ROOT / "js" / f"state-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        locales = (WEB_ROOT / "js" / f"locales-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        zh = json.loads((WEB_ROOT / "locales" / "zh-CN.json").read_text(encoding="utf-8"))
        en = json.loads((WEB_ROOT / "locales" / "en-US.json").read_text(encoding="utf-8"))

        self.assertIn("dailyPreferences", state)
        self.assertIn("recentDailySignature", app)
        self.assertIn("data-muyu-sound", app)
        self.assertIn("data-muyu-haptics", app)
        self.assertIn("data-muyu-motion", app)
        self.assertIn("data-daily-pause", app)
        self.assertIn("data-daily-repair", app)
        self.assertIn("data-evening-status", app)
        self.assertIn("dailyActionChoices", locales)
        self.assertIn("Muyu Reset", locales)
        self.assertIn("Intention set", locales)
        self.assertIn("No merit, luck, auto-tapping, or leaderboards are sold.", locales)
        self.assertNotIn("dailyBoost.score", app)
        self.assertNotIn("高于常规基线", locales)
        self.assertNotIn("above baseline", locales)
        self.assertEqual([item["label"] for item in zh["dailyCheckinOptions"]], ["Focus", "Spark", "Ground", "Connect", "Restore"])
        self.assertEqual([item["label"] for item in en["dailyCheckinOptions"]], ["Focus", "Spark", "Ground", "Connect", "Restore"])
        self.assertEqual({item["key"] for item in en["dailyEveningStatuses"]}, {"completed", "adjusted", "skipped"})

    def test_p3_analytics_contract_and_paid_release_copy(self):
        app = (WEB_ROOT / "js" / f"app-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        analytics = (WEB_ROOT / "js" / f"analytics-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        locales = (WEB_ROOT / "js" / f"locales-{ASSET_VERSION}.js").read_text(encoding="utf-8")
        required_events = [
            "onboarding_started",
            "onboarding_completed",
            "reading_generated",
            "today_viewed",
            "seal_selected",
            "muyu_started",
            "muyu_completed",
            "quest_action_completed",
            "weekly_review_viewed",
            "oracle_started",
            "oracle_saved",
            "paywall_viewed",
            "purchase_started",
            "purchase_completed",
            "subscription_restored",
        ]
        forbidden_keys = [
            "birth_date",
            "birth_datetime",
            "birth_time",
            "country",
            "region",
            "city",
            "timezone",
            "longitude",
            "latitude",
            "question",
            "report",
            "journal",
        ]

        for event in required_events:
            self.assertIn(event, analytics)
        for key in forbidden_keys:
            self.assertIn(key, analytics)
        self.assertNotIn('trackProductEvent("reading_generated", {\n            language: currentLang,\n            country', app)
        self.assertNotIn("daily_checkin_collected", app)
        self.assertNotIn("muyu_reset_started", app)
        self.assertNotIn("oracle_cast_started", app)
        self.assertNotIn("oracle_reading_saved", app)
        self.assertNotIn("commercial-flow test only", locales)
        self.assertNotIn("商业化流程测试", locales)
        self.assertIn("Purchase and restore are handled through the App Store.", locales)

    def test_p3_release_docs_are_present(self):
        self.assertTrue(Path("docs/p3-us-paid-release-2026-08-25.md").exists())
        self.assertTrue(Path("docs/p3-verification-baseline-2026-08-25.md").exists())
        self.assertTrue(Path("docs/analytics-events-v1.md").exists())
        self.assertTrue(Path("ios/AppStoreConnect/testflight-qa-checklist-20260825.md").exists())
        self.assertTrue(Path("ios/MINGLifePattern/Services/AppAnalytics.swift").exists())

    def test_versioned_static_assets_get_long_cache(self):
        httpd = server.ExclusiveThreadingHTTPServer(("127.0.0.1", 0), server.BaziHandler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=10)
            conn.request("GET", f"/js/app-{ASSET_VERSION}.js")
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
