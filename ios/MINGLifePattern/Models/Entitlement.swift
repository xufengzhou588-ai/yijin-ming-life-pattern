import Foundation

struct Entitlement: Codable, Equatable {
    enum Status: String, Codable {
        case free
        case proActive = "pro_active"
        case expired
        case needsRestore = "needs_restore"
        case revoked
    }

    let status: Status
    let isPro: Bool
    let tier: String
    let source: String
    let environment: String
    let productID: String?
    let expiresAt: Date?
    let needsRestore: Bool
    let storeKitReady: Bool

    enum CodingKeys: String, CodingKey {
        case status
        case isPro = "is_pro"
        case tier
        case source
        case environment
        case productID = "product_id"
        case expiresAt = "expires_at"
        case needsRestore = "needs_restore"
        case storeKitReady = "storekit_ready"
    }

    static let free = Entitlement(
        status: .free,
        isPro: false,
        tier: "free",
        source: "local",
        environment: "app",
        productID: nil,
        expiresAt: nil,
        needsRestore: false,
        storeKitReady: true
    )
}

struct EntitlementResponse: Codable {
    let ok: Bool
    let entitlement: Entitlement
    let sessionToken: String?

    enum CodingKeys: String, CodingKey {
        case ok
        case entitlement
        case sessionToken = "session_token"
    }
}
