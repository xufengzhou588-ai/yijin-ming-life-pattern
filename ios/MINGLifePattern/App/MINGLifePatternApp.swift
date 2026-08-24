import SwiftUI

@main
struct MINGLifePatternApp: App {
    @StateObject private var entitlementStore = EntitlementStore()
    @StateObject private var storeKitManager = StoreKitManager()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(entitlementStore)
                .environmentObject(storeKitManager)
                .task {
                    if !AppEnvironment.isFreeFirstRelease {
                        await storeKitManager.start(entitlementStore: entitlementStore)
                    }
                }
        }
    }
}
