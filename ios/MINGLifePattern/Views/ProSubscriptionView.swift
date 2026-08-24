import StoreKit
import SwiftUI

struct ProSubscriptionView: View {
    @EnvironmentObject private var entitlementStore: EntitlementStore
    @EnvironmentObject private var storeKitManager: StoreKitManager

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    header
                    entitlementBanner
                    benefits
                    if AppEnvironment.isFreeFirstRelease {
                        comingSoonSection
                    } else {
                        productList
                        restoreSection
                    }
                    boundaryCopy
                }
                .padding(20)
            }
            .background(Color.black.ignoresSafeArea())
            .foregroundStyle(.white)
            .navigationTitle("MING Pro")
            .task {
                if !AppEnvironment.isFreeFirstRelease && storeKitManager.products.isEmpty {
                    await storeKitManager.loadProducts()
                }
            }
            .onAppear {
                AppAnalytics.record("paywall_viewed", metadata: [
                    "surface": "native_pro"
                ])
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Unlock your complete life blueprint")
                .font(.title2.bold())
            Text(AppEnvironment.isFreeFirstRelease ? "Pro reports are being polished for the next release." : "Monthly Compass, complete Oracle and Journal, review history, deeper reports, and ritual soundscapes.")
                .foregroundStyle(.secondary)
        }
    }

    private var entitlementBanner: some View {
        HStack {
            Image(systemName: entitlementStore.isPro ? "checkmark.seal.fill" : "lock.fill")
                .foregroundStyle(entitlementStore.isPro ? .green : .yellow)
            VStack(alignment: .leading) {
                Text(entitlementStore.isPro ? "Pro Active" : "Free Reading")
                    .font(.headline)
                Text(statusDetail)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Spacer()
        }
        .padding()
        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
    }

    private var benefits: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(AppEnvironment.isFreeFirstRelease ? "Planned for Pro" : "Included with Pro")
                .font(.headline)
            benefit("Complete Life Blueprint", "Career, money, relationship, and annual rhythm reports.")
            benefit("Monthly Compass", "One focus, one boundary, one experiment, one reflection prompt.")
            benefit("Oracle and Journal", "Complete three-coin reading with private on-device history.")
            benefit("Ritual Soundscapes", "More Muyu tones, soundscapes, and personalized ritual sets.")
        }
    }

    private var comingSoonSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Pro is coming soon", systemImage: "sparkles.rectangle.stack")
                .font(.headline)
            Text("The first App Store release focuses on the free reading experience. Paid Pro subscriptions will be enabled in a later update after StoreKit products are ready.")
                .font(.footnote)
                .foregroundStyle(.secondary)
            Text("No purchase is available in this version.")
                .font(.footnote.bold())
                .foregroundStyle(.cyan)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
    }

    private var productList: some View {
        VStack(spacing: 10) {
            if storeKitManager.state == .loading {
                ProgressView("Loading subscriptions...")
                    .frame(maxWidth: .infinity)
                    .padding()
            } else if storeKitManager.products.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Label("Subscriptions unavailable", systemImage: "exclamationmark.triangle")
                        .font(.headline)
                    Text("Products are not loaded yet. In local testing, attach a StoreKit configuration or create matching products in App Store Connect.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    Button("Retry") {
                        Task { await storeKitManager.loadProducts() }
                    }
                    .buttonStyle(.bordered)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
            } else {
                ForEach(storeKitManager.products, id: \.id) { product in
                    Button {
                        Task { await storeKitManager.purchase(product) }
                    } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(product.displayName)
                                    .font(.headline)
                                Text(product.description)
                                    .font(.footnote)
                                    .foregroundStyle(.secondary)
                            }
                            Spacer()
                            Text(product.displayPrice)
                                .font(.headline)
                        }
                        .padding()
                        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
                    }
                    .buttonStyle(.plain)
                    .disabled(storeKitManager.state == .purchasing)
                }
            }
        }
    }

    private var restoreSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Button {
                Task { await storeKitManager.restorePurchases() }
            } label: {
                Label("Restore Purchase", systemImage: "arrow.clockwise")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)

            if let error = entitlementStore.lastError {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.orange)
            }
        }
    }

    private var boundaryCopy: some View {
        Text("MING is for cultural exploration and personal reflection. It is not medical, legal, financial, mental-health, safety, or emergency advice.")
            .font(.footnote)
            .foregroundStyle(.secondary)
    }

    private var statusDetail: String {
        if entitlementStore.isPro {
            if let expiresAt = entitlementStore.entitlement.expiresAt {
                return "Renews or expires: \(expiresAt.formatted(date: .abbreviated, time: .omitted))"
            }
            return "Subscription entitlement is active."
        }
        if AppEnvironment.isFreeFirstRelease {
            return "Free launch mode: Pro is previewed as a future update."
        }
        return "Upgrade to unlock Pro reports and guided oracle features."
    }

    private func benefit(_ title: String, _ body: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "sparkle")
                .foregroundStyle(.cyan)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.bold())
                Text(body)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 10))
    }
}
