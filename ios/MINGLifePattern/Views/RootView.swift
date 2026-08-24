import SwiftUI

struct RootView: View {
    var body: some View {
        TabView {
            MINGWebView(url: AppEnvironment.webAppURL)
                .tabItem {
                    Label("Reading", systemImage: "sparkles")
                }

            ProSubscriptionView()
                .tabItem {
                    Label("Pro", systemImage: "crown")
                }

            LegalLinksView()
                .tabItem {
                    Label("Trust", systemImage: "checkmark.shield")
                }
        }
        .tint(.cyan)
    }
}
