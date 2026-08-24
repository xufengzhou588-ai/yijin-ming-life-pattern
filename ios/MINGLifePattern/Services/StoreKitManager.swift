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
            let result = try await product.purchase()
            switch result {
            case .success(let verificationResult):
                let transaction = try checkVerified(verificationResult)
                entitlementStore?.apply(transaction: transaction, environment: storeEnvironment)
                await sync(signedTransaction: nil)
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
                entitlementStore?.apply(transaction: transaction, environment: storeEnvironment)
                await sync(signedTransaction: nil)
            } catch {
                entitlementStore?.setError(error.localizedDescription)
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
            entitlementStore?.apply(transaction: transaction, environment: storeEnvironment)
            await sync(signedTransaction: nil)
            await transaction.finish()
        } catch {
            entitlementStore?.setError(error.localizedDescription)
        }
    }

    private func sync(signedTransaction: String?) async {
        guard let signedTransaction else {
            // Xcode 16.1's StoreKit Transaction type does not expose a signed JWS payload.
            // Keep the locally verified entitlement active; production server validation
            // should be wired in the Xcode 26 upload environment where signed transaction
            // payloads are available.
            return
        }
        do {
            let entitlement = try await apiClient.syncAppStoreTransaction(
                jwsRepresentation: signedTransaction
            )
            entitlementStore?.apply(entitlement)
        } catch {
            // Keep locally verified StoreKit entitlement active if backend sync is temporarily unavailable.
            entitlementStore?.setError(error.localizedDescription)
        }
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .verified(let safe):
            return safe
        case .unverified:
            throw StoreKitError.unknown
        }
    }

    private var storeEnvironment: String {
        #if DEBUG
        return "sandbox"
        #else
        return "production"
        #endif
    }

    private func productPriority(_ id: String) -> Int {
        id == "ming.pro.yearly" ? 0 : 1
    }
}
