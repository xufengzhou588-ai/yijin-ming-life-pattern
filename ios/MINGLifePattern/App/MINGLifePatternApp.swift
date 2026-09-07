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
                    AppAnalytics.record("first_open", metadata: [
                        "surface": "ios"
                    ], options: .init(oncePerInstall: true))
                    AppAnalytics.record("experiment_exposure", metadata: [
                        "experiment_key": "us_testflight_paywall_copy",
                        "variant": "assigned",
                        "surface": "app_start"
                    ], options: .init(throttleSeconds: 300))
                    if !AppEnvironment.isFreeFirstRelease {
                        await storeKitManager.start(entitlementStore: entitlementStore)
                    } else {
                        AppAnalytics.record("free_entitlement", metadata: [
                            "entitlement_status": Entitlement.Status.free.rawValue,
                            "entitlement_tier": "free",
                            "source": "free_first"
                        ], options: .init(throttleSeconds: 300))
                    }
                }
        }
    }
}
