import StoreKit
import SwiftUI

struct ProSubscriptionView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var entitlementStore: EntitlementStore
    @EnvironmentObject private var storeKitManager: StoreKitManager

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                entitlementBanner
                benefits
                if AppEnvironment.isFreeFirstRelease {
                    comingSoonSection
                } else {
                    productList
                    storeKitStatus
                    restoreSection
                }
                legalLinks
                boundaryCopy
            }
            .padding(20)
        }
        .background(Color.black.ignoresSafeArea())
        .foregroundStyle(.white)
        .navigationTitle("MING Pro")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button("Done") {
                    dismiss()
                }
                .accessibilityLabel(AppEnvironment.isFreeFirstRelease ? "Close MING Pro preview" : "Close MING Pro paywall")
                .accessibilityHint("Returns to the reading screen.")
            }
        }
        .task {
            if !AppEnvironment.isFreeFirstRelease && storeKitManager.products.isEmpty {
                await storeKitManager.loadProducts()
            }
        }
        .onAppear {
            AppAnalytics.record("paywall_view", metadata: [
                "surface": "native_pro",
                "module": "pro_sheet"
            ], options: .init(throttleSeconds: 30))
            AppAnalytics.record("experiment_exposure", metadata: [
                "experiment_key": "us_testflight_paywall_copy",
                "variant": "assigned",
                "surface": "native_pro"
            ], options: .init(throttleSeconds: 300))
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Unlock your complete life blueprint")
                .font(.title2.weight(.bold))
                .fixedSize(horizontal: false, vertical: true)
            Text(AppEnvironment.isFreeFirstRelease ? "Pro reports are being polished for the next release." : "Monthly Compass, complete Oracle and Journal, review history, deeper reports, and ritual soundscapes.")
                .foregroundStyle(secondaryText)
                .fixedSize(horizontal: false, vertical: true)
        }
        .accessibilityElement(children: .combine)
    }

    private var entitlementBanner: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: entitlementStore.isPro ? "checkmark.seal.fill" : "lock.fill")
                .foregroundStyle(entitlementStore.isPro ? .green : .yellow)
                .font(.title3)
                .accessibilityHidden(true)
            VStack(alignment: .leading) {
                Text(entitlementTitle)
                    .font(.headline)
                Text(statusDetail)
                    .font(.footnote)
                    .foregroundStyle(secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer()
        }
        .padding()
        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(entitlementStore.isPro ? "Pro Active" : "Free Reading"). \(statusDetail)")
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
                .foregroundStyle(secondaryText)
                .fixedSize(horizontal: false, vertical: true)
            Text("No purchase is available in this version.")
                .font(.footnote.weight(.bold))
                .foregroundStyle(.cyan)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        .accessibilityElement(children: .combine)
    }

    private var productList: some View {
        VStack(alignment: .leading, spacing: 10) {
            if storeKitManager.state == .loading {
                ProgressView("Loading subscriptions...")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .accessibilityLabel("Loading App Store subscriptions")
            } else if storeKitManager.products.isEmpty {
                subscriptionsUnavailable
            } else {
                ForEach(storeKitManager.products, id: \.id) { product in
                    purchaseButton(for: product)
                }
            }
        }
    }

    private var storeKitStatus: some View {
        Group {
            if let message = storeKitStatusMessage {
                Label(message.text, systemImage: message.systemImage)
                    .font(.footnote)
                    .foregroundStyle(message.color)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
                    .background(.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 10))
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(message.text)
            }
        }
    }

    private var restoreSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Button {
                Task { await storeKitManager.restorePurchases() }
            } label: {
                HStack {
                    if storeKitManager.state == .restoring {
                        ProgressView()
                            .accessibilityHidden(true)
                    }
                    Label(storeKitManager.state == .restoring ? "Restoring..." : "Restore Purchase", systemImage: "arrow.clockwise")
                }
                .frame(maxWidth: .infinity, minHeight: 44)
            }
            .buttonStyle(.bordered)
            .disabled(isStoreKitBusy)
            .accessibilityHint("Checks the App Store for an active Pro subscription and returns to the free state if none is found.")

            if let error = entitlementStore.lastError {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.orange)
                    .fixedSize(horizontal: false, vertical: true)
                    .accessibilityLabel("Purchase status: \(error)")
            }
        }
    }

    private var legalLinks: some View {
        HStack(spacing: 14) {
            Link("Terms", destination: AppEnvironment.termsURL)
            Link("Privacy", destination: AppEnvironment.privacyURL)
            Link("Support", destination: AppEnvironment.supportURL)
        }
        .font(.footnote)
        .foregroundStyle(.cyan)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var boundaryCopy: some View {
        Text("MING is for cultural exploration and personal reflection. It is not medical, legal, financial, mental-health, safety, or emergency advice.")
            .font(.footnote)
            .foregroundStyle(secondaryText)
            .fixedSize(horizontal: false, vertical: true)
    }

    private var subscriptionsUnavailable: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Subscriptions unavailable", systemImage: "exclamationmark.triangle")
                .font(.headline)
            Text("Products are not loaded yet. In local testing, attach a StoreKit configuration or create matching products in App Store Connect.")
                .font(.footnote)
                .foregroundStyle(secondaryText)
                .fixedSize(horizontal: false, vertical: true)
            Button("Retry") {
                Task { await storeKitManager.loadProducts() }
            }
            .buttonStyle(.bordered)
            .frame(minHeight: 44)
            .accessibilityHint("Attempts to load Pro monthly and yearly subscriptions again.")
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        .accessibilityElement(children: .combine)
    }

    private var secondaryText: Color {
        Color.white.opacity(0.76)
    }

    private func purchaseButton(for product: Product) -> some View {
        Button {
            Task { await storeKitManager.purchase(product) }
        } label: {
            VStack(alignment: .leading, spacing: 6) {
                Text(product.displayName)
                    .font(.headline)
                    .fixedSize(horizontal: false, vertical: true)
                Text(product.description)
                    .font(.footnote)
                    .foregroundStyle(secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
                HStack(alignment: .firstTextBaseline, spacing: 6) {
                    Text(product.displayPrice)
                        .font(.headline)
                        .foregroundStyle(.white)
                    let billingPeriod = billingPeriodText(for: product)
                    if !billingPeriod.isEmpty {
                        Text(billingPeriod)
                            .font(.caption)
                            .foregroundStyle(secondaryText)
                    }
                }
                .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, minHeight: 56, alignment: .leading)
            .padding()
            .background(.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        }
        .buttonStyle(.plain)
        .disabled(isStoreKitBusy)
        .accessibilityLabel("\(product.displayName), \(product.displayPrice)")
        .accessibilityHint("Purchases this subscription through the App Store.")
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
        switch entitlementStore.entitlement.status {
        case .expired:
            return "Your previous subscription appears expired. Renew through the App Store to unlock Pro."
        case .revoked:
            return "This subscription is no longer active. Restore or purchase through the App Store."
        case .needsRestore:
            if !entitlementStore.entitlement.storeKitReady {
                return "App Store validation is temporarily unavailable. Pro remains locked."
            }
            return "Restore Purchase checks this Apple ID for an active subscription."
        case .free, .proActive:
            break
        }
        return "Upgrade to unlock Pro reports and guided oracle features."
    }

    private var entitlementTitle: String {
        if entitlementStore.isPro {
            return "Pro Active"
        }
        switch entitlementStore.entitlement.status {
        case .expired:
            return "Subscription Expired"
        case .revoked:
            return "Subscription Inactive"
        case .needsRestore:
            return "Restore Needed"
        case .free, .proActive:
            return "Free Reading"
        }
    }

    private var isStoreKitBusy: Bool {
        storeKitManager.state == .loading || storeKitManager.state == .purchasing || storeKitManager.state == .restoring
    }

    private var storeKitStatusMessage: (text: String, systemImage: String, color: Color)? {
        switch storeKitManager.state {
        case .purchased:
            return ("Purchase verified. Pro is active.", "checkmark.seal.fill", .green)
        case .restored:
            return ("Purchase restored. Pro is active.", "checkmark.seal.fill", .green)
        case .cancelled:
            return ("Purchase cancelled. Nothing was charged.", "xmark.circle", .secondary)
        case .pending:
            return ("Purchase pending. Pro unlocks after Apple completes approval.", "clock", .yellow)
        case .noActiveSubscription:
            return ("No active Pro subscription was found for this Apple ID.", "exclamationmark.circle", .yellow)
        case .failed(let message):
            return (message, "exclamationmark.triangle", .orange)
        case .idle, .loading, .purchasing, .restoring:
            return nil
        }
    }

    private func billingPeriodText(for product: Product) -> String {
        guard let period = product.subscription?.subscriptionPeriod else {
            return ""
        }
        return "/ \(periodText(period))"
    }

    private func periodText(_ period: Product.SubscriptionPeriod) -> String {
        let unit: String
        switch period.unit {
        case .day:
            unit = period.value == 1 ? "day" : "days"
        case .week:
            unit = period.value == 1 ? "week" : "weeks"
        case .month:
            unit = period.value == 1 ? "month" : "months"
        case .year:
            unit = period.value == 1 ? "year" : "years"
        @unknown default:
            unit = period.value == 1 ? "period" : "periods"
        }
        return period.value == 1 ? unit : "\(period.value) \(unit)"
    }

    private func benefit(_ title: String, _ body: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "sparkle")
                .foregroundStyle(.cyan)
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.bold))
                    .fixedSize(horizontal: false, vertical: true)
                Text(body)
                    .font(.footnote)
                    .foregroundStyle(secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
        .accessibilityElement(children: .combine)
    }
}
