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
        do {
            let result = try await product.purchase(options: [.appAccountToken(appAccountToken)])
            switch result {
            case .success(let verificationResult):
                let transaction = try checkVerified(verificationResult)
                let response = try await sync(transaction: transaction, verificationResult: verificationResult)
                entitlementStore?.apply(response)
                await transaction.finish()
                state = .purchased
            case .userCancelled, .pending:
                state = .idle
            @unknown default:
                state = .failed("Unknown purchase result.")
            }
        } catch {
            state = .failed("Purchase could not be completed.")
            entitlementStore?.setError(error.localizedDescription)
        }
    }

    func restorePurchases() async {
        state = .restoring
        do {
            try await AppStore.sync()
            await refreshCurrentEntitlements()
            state = entitlementStore?.isPro == true ? .purchased : .idle
        } catch {
            state = .failed("Restore could not be completed.")
            entitlementStore?.setError(error.localizedDescription)
        }
    }

    func refreshCurrentEntitlements() async {
        var foundPro = false
        for await result in Transaction.currentEntitlements {
            do {
                let transaction = try checkVerified(result)
                guard Self.productIDs.contains(transaction.productID) else { continue }
                foundPro = true
                let response = try await sync(transaction: transaction, verificationResult: result)
                entitlementStore?.apply(response)
            } catch {
                entitlementStore?.markEntitlementUnavailable(error.localizedDescription)
            }
        }
        if !foundPro {
            entitlementStore?.apply(.free)
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
            entitlementStore?.markEntitlementUnavailable(error.localizedDescription)
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
            anonymousInstallID: appAccountToken
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
}

private enum InstallationIdentity {
    private static let defaultsKey = "ming.appAccountToken.v1"

    static var appAccountToken: UUID {
        if let stored = UserDefaults.standard.string(forKey: defaultsKey),
           let uuid = UUID(uuidString: stored) {
            return uuid
        }
        let uuid = UUID()
        UserDefaults.standard.set(uuid.uuidString, forKey: defaultsKey)
        return uuid
    }
}
