import SwiftUI

struct RootView: View {
    @EnvironmentObject private var storeKitManager: StoreKitManager
    @State private var isShowingProPaywall = false

    var body: some View {
        NavigationStack {
            MINGWebView(
                url: AppEnvironment.webAppURL,
                onOpenProPaywall: {
                    isShowingProPaywall = true
                },
                onRestorePurchases: {
                    isShowingProPaywall = true
                    guard !AppEnvironment.isFreeFirstRelease else { return }
                    Task {
                        await storeKitManager.restorePurchases()
                    }
                }
            )
            .navigationTitle("MING")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink {
                        LegalLinksView()
                    } label: {
                        Label("Trust", systemImage: "checkmark.shield")
                    }
                    .accessibilityLabel("Open Trust and safety")
                    .accessibilityHint("Shows privacy, terms, support, and product boundaries.")
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        isShowingProPaywall = true
                    } label: {
                        Label("MING Pro", systemImage: "crown")
                    }
                    .accessibilityLabel(AppEnvironment.isFreeFirstRelease ? "Open MING Pro preview" : "Open MING Pro paywall")
                    .accessibilityHint(AppEnvironment.isFreeFirstRelease ? "Shows planned Pro benefits for a later update." : "Shows Pro benefits, subscription status, purchase, and restore options.")
                }
            }
            .sheet(isPresented: $isShowingProPaywall) {
                NavigationStack {
                    ProSubscriptionView()
                }
            }
        }
        .tint(.cyan)
    }
}
