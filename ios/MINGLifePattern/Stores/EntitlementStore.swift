import Foundation
import StoreKit

@MainActor
final class EntitlementStore: ObservableObject {
    @Published private(set) var entitlement: Entitlement = .free
    @Published private(set) var sessionToken: String?
    @Published private(set) var lastError: String?

    var isPro: Bool {
        entitlement.isPro
    }

    func apply(_ entitlement: Entitlement) {
        self.entitlement = entitlement
        if !entitlement.isPro {
            self.sessionToken = nil
        }
        self.lastError = nil
    }

    func apply(_ response: EntitlementResponse) {
        entitlement = response.entitlement
        sessionToken = response.entitlement.isPro ? response.sessionToken : nil
        lastError = nil
    }

    func setError(_ message: String) {
        lastError = message
    }

    func markEntitlementUnavailable(_ message: String) {
        entitlement = Entitlement(
            status: .needsRestore,
            isPro: false,
            tier: "free",
            source: "app_store",
            environment: "app",
            productID: nil,
            expiresAt: nil,
            needsRestore: true,
            storeKitReady: false
        )
        sessionToken = nil
        lastError = message
    }
}
