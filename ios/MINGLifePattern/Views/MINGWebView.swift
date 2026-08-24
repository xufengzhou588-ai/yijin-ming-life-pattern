import SwiftUI
import UIKit
import WebKit

struct MINGWebView: UIViewRepresentable {
    @EnvironmentObject private var entitlementStore: EntitlementStore

    let url: URL

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.navigationDelegate = context.coordinator
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        context.coordinator.applyNativeProCookie(
            isPro: entitlementStore.isPro,
            url: url,
            webView: webView
        )

        guard webView.url == nil else { return }
        webView.load(URLRequest(url: url))
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        private var lastAppliedIsPro: Bool?

        func applyNativeProCookie(isPro: Bool, url: URL, webView: WKWebView) {
            guard lastAppliedIsPro != isPro else { return }
            lastAppliedIsPro = isPro

            guard let host = url.host else { return }
            var properties: [HTTPCookiePropertyKey: Any] = [
                .domain: host,
                .path: "/",
                .name: "bazi_native_pro",
                .value: isPro ? "1" : "",
                .expires: isPro ? Date().addingTimeInterval(60 * 60 * 24 * 30) : Date(timeIntervalSince1970: 0)
            ]
            if url.scheme == "https" {
                properties[.secure] = "TRUE"
            }

            guard let cookie = HTTPCookie(properties: properties) else { return }
            webView.configuration.websiteDataStore.httpCookieStore.setCookie(cookie) {
                if webView.url != nil {
                    webView.reload()
                }
            }
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
            return .allow
        }
    }
}
