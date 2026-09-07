import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class NavPaywallA11yTests(unittest.TestCase):
    def test_native_shell_uses_contextual_paywall_not_primary_pro_tab(self):
        root_view = read_text("ios/MINGLifePattern/Views/RootView.swift")

        self.assertNotIn("TabView", root_view)
        self.assertNotIn('Label("Pro"', root_view)
        self.assertIn("MINGWebView(", root_view)
        self.assertIn("onOpenProPaywall", root_view)
        self.assertIn("onRestorePurchases", root_view)
        self.assertIn(".sheet(isPresented: $isShowingProPaywall)", root_view)
        self.assertRegex(root_view, re.compile(r"\.sheet\(isPresented: \$isShowingProPaywall\)\s*\{\s*NavigationStack\s*\{\s*ProSubscriptionView\(\)", re.S))
        self.assertIn("NavigationLink", root_view)
        self.assertIn("LegalLinksView()", root_view)
        self.assertIn("Open MING Pro preview", root_view)
        self.assertIn("Open Trust and safety", root_view)

    def test_native_paywall_has_exit_state_and_accessible_touch_targets(self):
        paywall = read_text("ios/MINGLifePattern/Views/ProSubscriptionView.swift")
        storekit = read_text("ios/MINGLifePattern/Services/StoreKitManager.swift")
        api_client = read_text("ios/MINGLifePattern/Services/APIClient.swift")

        self.assertIn("@Environment(\\.dismiss)", paywall)
        self.assertIn('Button("Done")', paywall)
        self.assertIn("Close MING Pro preview", paywall)
        self.assertIn("fixedSize(horizontal: false, vertical: true)", paywall)
        self.assertIn("minHeight: 44", paywall)
        self.assertIn("accessibilityElement(children: .combine)", paywall)
        self.assertIn("No active Pro subscription was found for this Apple ID.", storekit)
        self.assertIn("enum APIError: LocalizedError", api_client)

    def test_free_first_release_is_the_app_store_default(self):
        info = read_text("ios/MINGLifePattern/Resources/Info.plist")
        environment = read_text("ios/MINGLifePattern/Support/AppEnvironment.swift")
        app = read_text("web/js/app-v20260826.js")

        self.assertRegex(info, re.compile(r"<key>MING_PRO_MODE</key>\s*<string>free_first</string>"))
        self.assertIn("return .freeFirst", environment)
        self.assertIn('get("release") || "free_first"', app)
        self.assertIn("if (isFreeFirstRelease) return;", app)

    def test_native_webview_exposes_storekit_bridge_without_legacy_pro_cookie(self):
        webview = read_text("ios/MINGLifePattern/Views/MINGWebView.swift")
        environment = read_text("ios/MINGLifePattern/Support/AppEnvironment.swift")

        self.assertIn("WKScriptMessageHandler", webview)
        self.assertIn('messageHandlerName = "mingStoreKit"', webview)
        self.assertIn('"open_paywall"', webview)
        self.assertIn('"restore_purchase"', webview)
        self.assertIn("removeScriptMessageHandler", webview)
        self.assertIn('makeCookie(name: "bazi_native_pro", value: ""', webview)
        self.assertIn("urlWithReleaseMode", environment)
        self.assertIn('URLQueryItem(name: "release", value: ProMode.freeFirst.rawValue)', environment)

    def test_web_paywall_focus_restore_and_native_storekit_actions_are_present(self):
        app = read_text("web/js/app-v20260826.js")
        html = read_text("web/index.html")

        self.assertIn("postNativeStoreKit", app)
        self.assertIn('"open_paywall"', app)
        self.assertIn('"restore_purchase"', app)
        self.assertIn('id="open-native-paywall"', app)
        self.assertIn('id="pro-paywall-back"', app)
        self.assertLess(app.index('id="open-native-paywall"'), app.index('id="pro-paywall-back"'))
        self.assertLess(app.index('id="restore-pro-purchase"'), app.index('id="pro-paywall-back"'))
        self.assertIn('tabindex="-1" aria-labelledby="pro-paywall-title"', app)
        self.assertIn("focusRegion(paywall);\n        window.requestAnimationFrame(() => focusRegion(paywall));", app)
        self.assertIn("focusRegion(paywall)", app)
        self.assertIn("proPaywallReturnFocus.focus", app)
        self.assertIn("scrollBlockIntoView", app)
        for target in ["today", "blueprint", "oracle", "me"]:
            self.assertIn(f'id="mobile-pane-{target}"', html)
            self.assertIn(f'aria-controls="mobile-pane-{target}"', html)

    def test_web_mobile_and_paywall_copy_have_accessible_labels(self):
        zh = json.loads(read_text("web/locales/zh-CN.json"))
        en = json.loads(read_text("web/locales/en-US.json"))
        css = read_text("web/styles/components-v20260826.css")
        responsive = read_text("web/styles/responsive-v20260826.css")

        for locale in [zh, en]:
            for key in [
                "mobileNavTodayAria",
                "mobileNavBlueprintAria",
                "mobileNavOracleAria",
                "mobileNavMeAria",
                "proPaywallBack",
                "proOpenNativePaywall",
                "proNativePaywallOpened",
                "proNativePaywallUnavailable",
                "proRestoreStarted",
            ]:
                self.assertIn(key, locale)

        self.assertRegex(css, re.compile(r"\.premium-button\s*\{[^}]*min-height:\s*44px", re.S))
        self.assertRegex(css, re.compile(r"\.pro-access-actions button\s*\{[^}]*min-height:\s*44px", re.S))
        self.assertIn("white-space: normal;", responsive)
        self.assertIn("overflow-wrap: anywhere;", responsive)


if __name__ == "__main__":
    unittest.main()
