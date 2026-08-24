import Foundation
import StoreKit

@MainActor
final class EntitlementStore: ObservableObject {
    @Published private(set) var entitlement: Entitlement = .free
    @Published private(set) var lastError: String?

    var isPro: Bool {
        entitlement.isPro
    }

    func apply(_ entitlement: Entitlement) {
        self.entitlement = entitlement
        self.lastError = nil
    }

    func apply(transaction: Transaction, environment: String) {
        let active = transaction.revocationDate == nil && (transaction.expirationDate ?? .distantFuture) > Date()
        entitlement = Entitlement(
            status: active ? .proActive : .expired,
            isPro: active,
            tier: active ? "pro" : "free",
            source: "app_store",
            environment: environment,
            productID: transaction.productID,
            expiresAt: transaction.expirationDate,
            needsRestore: !active,
            storeKitReady: true
        )
        lastError = nil
    }

    func setError(_ message: String) {
        lastError = message
    }
}
