import Foundation
import StoreKit

@MainActor
final class StoreKitManager: ObservableObject {
    enum PurchaseState: Equatable {
        case idle
        case loading
        case purchasing
        case restoring
        case purchased
        case restored
        case cancelled
        case pending
        case noActiveSubscription
        case failed(String)
    }

    static let productIDs: Set<String> = [
        "ming.pro.monthly",
        "ming.pro.yearly"
    ]

    @Published private(set) var products: [Product] = []
    @Published private(set) var state: PurchaseState = .idle

    private let apiClient = APIClient()
    private let appAccountToken = InstallationIdentity.appAccountToken
    private var transactionUpdatesTask: Task<Void, Never>?
    private weak var entitlementStore: EntitlementStore?

    deinit {
        transactionUpdatesTask?.cancel()
    }

    func start(entitlementStore: EntitlementStore) async {
        self.entitlementStore = entitlementStore
        listenForTransactionUpdates()
        await loadProducts()
        await refreshCurrentEntitlements()
    }

    func loadProducts() async {
        state = .loading
        do {
            products = try await Product.products(for: Self.productIDs)
                .sorted { productPriority($0.id) < productPriority($1.id) }
            state = .idle
        } catch {
            state = .failed("Products could not be loaded.")
            entitlementStore?.setError(error.localizedDescription)
        }
    }

    func purchase(_ product: Product) async {
        state = .purchasing
        AppAnalytics.record("purchase_start", metadata: [
            "product_id": product.id,
            "source": "storekit"
        ])
        do {
            let result = try await product.purchase(options: [.appAccountToken(appAccountToken)])
            switch result {
            case .success(let verificationResult):
                let transaction = try checkVerified(verificationResult)
                let response = try await sync(transaction: transaction, verificationResult: verificationResult)
                entitlementStore?.apply(response)
                await transaction.finish()
                state = .purchased
                AppAnalytics.record("purchase_success", metadata: [
                    "product_id": product.id,
                    "entitlement_status": response.entitlement.status.rawValue,
                    "source": "storekit"
                ])
            case .userCancelled:
                AppAnalytics.record("purchase_cancel", metadata: [
                    "product_id": product.id,
                    "source": "storekit",
                    "cancel_reason": "user_cancelled"
                ])
                state = .cancelled
            case .pending:
                AppAnalytics.record("purchase_failure", metadata: [
                    "product_id": product.id,
                    "source": "storekit",
                    "failure_stage": "purchase",
                    "error_code": "pending_approval"
                ])
                state = .pending
            @unknown default:
                AppAnalytics.record("purchase_failure", metadata: [
                    "product_id": product.id,
                    "source": "storekit",
                    "failure_stage": "purchase",
                    "error_code": "unknown_result"
                ])
                state = .failed("Unknown purchase result.")
            }
        } catch {
            let message = userFacingMessage(for: error)
            AppAnalytics.record("purchase_failure", metadata: [
                "product_id": product.id,
                "source": "storekit",
                "failure_stage": "purchase",
                "error_code": "storekit_error"
            ])
            state = .failed(message)
            entitlementStore?.setError(message)
        }
    }

    func restorePurchases() async {
        state = .restoring
        AppAnalytics.record("restore", metadata: [
            "source": "storekit",
            "status": "started"
        ])
        do {
            try await AppStore.sync()
            let entitlement = await refreshCurrentEntitlements()
            if entitlementStore?.isPro == true {
                state = .restored
            } else if entitlement.status == .expired || entitlement.status == .revoked || entitlement.status == .needsRestore {
                state = .failed(statusMessage(for: entitlement))
            } else {
                state = .noActiveSubscription
            }
            AppAnalytics.record("restore", metadata: [
                "entitlement_status": entitlementStore?.entitlement.status.rawValue ?? Entitlement.Status.free.rawValue,
                "source": "storekit",
                "status": "success"
            ])
        } catch {
            let message = userFacingMessage(for: error)
            AppAnalytics.record("restore", metadata: [
                "source": "storekit",
                "status": "failure",
                "error_code": "storekit_error"
            ])
            state = .failed(message)
            entitlementStore?.setError(message)
        }
    }

    @discardableResult
    func refreshCurrentEntitlements() async -> Entitlement {
        var foundPro = false
        var syncFailed = false
        for await result in Transaction.currentEntitlements {
            do {
                let transaction = try checkVerified(result)
                guard Self.productIDs.contains(transaction.productID) else { continue }
                foundPro = true
                let response = try await sync(transaction: transaction, verificationResult: result)
                entitlementStore?.apply(response)
            } catch {
                syncFailed = true
                entitlementStore?.markEntitlementUnavailable(userFacingMessage(for: error))
            }
        }
        if foundPro || syncFailed {
            return entitlementStore?.entitlement ?? .free
        }
        do {
            let response = try await apiClient.fetchEntitlement()
            entitlementStore?.apply(response)
            return response.entitlement
        } catch {
            entitlementStore?.apply(.free)
            AppAnalytics.record("free_entitlement", metadata: [
                "entitlement_status": Entitlement.Status.free.rawValue,
                "entitlement_tier": "free",
                "source": "storekit"
            ], options: .init(throttleSeconds: 300))
            return .free
        }
    }

    private func listenForTransactionUpdates() {
        transactionUpdatesTask?.cancel()
        transactionUpdatesTask = Task { [weak self] in
            for await result in Transaction.updates {
                await self?.handle(transactionUpdate: result)
            }
        }
    }

    private func handle(transactionUpdate result: VerificationResult<Transaction>) async {
        do {
            let transaction = try checkVerified(result)
            guard Self.productIDs.contains(transaction.productID) else { return }
            let response = try await sync(transaction: transaction, verificationResult: result)
            entitlementStore?.apply(response)
            await transaction.finish()
        } catch {
            entitlementStore?.markEntitlementUnavailable(userFacingMessage(for: error))
        }
    }

    private func sync(
        transaction: Transaction,
        verificationResult: VerificationResult<Transaction>
    ) async throws -> EntitlementResponse {
        try await apiClient.syncAppStoreTransaction(
            jwsRepresentation: verificationResult.jwsRepresentation,
            transactionID: String(transaction.id),
            originalTransactionID: String(transaction.originalID),
            appAccountToken: transaction.appAccountToken ?? appAccountToken,
            anonymousInstallID: InstallationIdentity.analyticsInstallID
        )
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .verified(let safe):
            return safe
        case .unverified:
            throw StoreKitError.unknown
        }
    }

    private func productPriority(_ id: String) -> Int {
        id == "ming.pro.yearly" ? 0 : 1
    }

    private func userFacingMessage(for error: Error) -> String {
        if let localized = (error as? LocalizedError)?.errorDescription, !localized.isEmpty {
            return localized
        }
        return error.localizedDescription
    }

    private func statusMessage(for entitlement: Entitlement) -> String {
        switch entitlement.status {
        case .expired:
            return "No active Pro subscription was found. Your previous subscription appears expired."
        case .revoked:
            return "No active Pro subscription was found. This subscription is no longer active."
        case .needsRestore:
            if !entitlement.storeKitReady {
                return "App Store validation is temporarily unavailable. Please try again later."
            }
            return "No active Pro subscription was found for this Apple ID."
        case .free:
            return "No active Pro subscription was found for this Apple ID."
        case .proActive:
            return "Subscription entitlement is active."
        }
    }
}

enum InstallationIdentity {
    private static let defaultsKey = "ming.appAccountToken.v1"
    private static let analyticsDefaultsKey = "ming.analytics.installId.v1"

    static var appAccountToken: UUID {
        storedUUID(forKey: defaultsKey)
    }

    static var analyticsInstallID: UUID {
        storedUUID(forKey: analyticsDefaultsKey)
    }

    private static func storedUUID(forKey key: String) -> UUID {
        if let stored = UserDefaults.standard.string(forKey: key),
           let uuid = UUID(uuidString: stored) {
            return uuid
        }
        let uuid = UUID()
        UserDefaults.standard.set(uuid.uuidString, forKey: key)
        return uuid
    }
}
