import SwiftUI
import UIKit
import WebKit

struct MINGWebView: UIViewRepresentable {
    @EnvironmentObject private var entitlementStore: EntitlementStore

    let url: URL
    let onOpenProPaywall: () -> Void
    let onRestorePurchases: () -> Void

    init(
        url: URL,
        onOpenProPaywall: @escaping () -> Void = {},
        onRestorePurchases: @escaping () -> Void = {}
    ) {
        self.url = url
        self.onOpenProPaywall = onOpenProPaywall
        self.onRestorePurchases = onRestorePurchases
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        configuration.userContentController.add(context.coordinator, name: Coordinator.messageHandlerName)

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .automatic
        webView.navigationDelegate = context.coordinator
        webView.accessibilityLabel = "MING reading workspace"
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        context.coordinator.onOpenProPaywall = onOpenProPaywall
        context.coordinator.onRestorePurchases = onRestorePurchases
        context.coordinator.applySessionCookie(
            sessionToken: entitlementStore.sessionToken,
            url: url,
            webView: webView
        )

        guard webView.url == nil else { return }
        webView.load(URLRequest(url: url))
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(
            onOpenProPaywall: onOpenProPaywall,
            onRestorePurchases: onRestorePurchases
        )
    }

    static func dismantleUIView(_ webView: WKWebView, coordinator: Coordinator) {
        webView.configuration.userContentController.removeScriptMessageHandler(forName: Coordinator.messageHandlerName)
    }

    final class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
        static let messageHandlerName = "mingStoreKit"

        var onOpenProPaywall: () -> Void
        var onRestorePurchases: () -> Void

        private var lastAppliedSessionToken: String?
        private var didClearLegacyProCookie = false

        init(
            onOpenProPaywall: @escaping () -> Void,
            onRestorePurchases: @escaping () -> Void
        ) {
            self.onOpenProPaywall = onOpenProPaywall
            self.onRestorePurchases = onRestorePurchases
        }

        func applySessionCookie(sessionToken: String?, url: URL, webView: WKWebView) {
            let token = sessionToken ?? ""
            guard lastAppliedSessionToken != token || !didClearLegacyProCookie else { return }
            lastAppliedSessionToken = token
            didClearLegacyProCookie = true

            guard let host = url.host else { return }
            let cookies = [
                makeCookie(name: "bazi_native_pro", value: "", host: host, url: url, expires: Date(timeIntervalSince1970: 0)),
                makeCookie(
                    name: "bazi_session",
                    value: token,
                    host: host,
                    url: url,
                    expires: token.isEmpty ? Date(timeIntervalSince1970: 0) : Date().addingTimeInterval(60 * 30)
                )
            ].compactMap { $0 }

            let group = DispatchGroup()
            for cookie in cookies {
                group.enter()
                webView.configuration.websiteDataStore.httpCookieStore.setCookie(cookie) {
                    group.leave()
                }
            }
            group.notify(queue: .main) {
                if webView.url != nil {
                    webView.reload()
                }
            }
        }

        private func makeCookie(name: String, value: String, host: String, url: URL, expires: Date) -> HTTPCookie? {
            var properties: [HTTPCookiePropertyKey: Any] = [
                .domain: host,
                .path: "/",
                .name: name,
                .value: value,
                .expires: expires
            ]
            if url.scheme == "https" {
                properties[.secure] = "TRUE"
            }
            return HTTPCookie(properties: properties)
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationAction: WKNavigationAction
        ) async -> WKNavigationActionPolicy {
            guard let targetURL = navigationAction.request.url else { return .cancel }
            if targetURL.scheme == "mailto" {
                UIApplication.shared.open(targetURL, options: [:], completionHandler: nil)
                return .cancel
            }
            if navigationAction.targetFrame == nil {
                webView.load(URLRequest(url: targetURL))
                return .cancel
            }
            return .allow
        }

        func userContentController(
            _ userContentController: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            guard message.name == Self.messageHandlerName,
                  let body = message.body as? [String: Any],
                  let action = body["action"] as? String else {
                return
            }

            Task { @MainActor in
                switch action {
                case "open_paywall":
                    onOpenProPaywall()
                case "restore_purchase":
                    onRestorePurchases()
                default:
                    break
                }
            }
        }
    }
}
