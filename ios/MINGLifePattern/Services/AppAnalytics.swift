import Foundation

enum AppAnalytics {
    private struct StoredEvent: Codable {
        let name: String
        let schemaVersion: String
        let metadata: [String: String]
        let createdAt: Date

        enum CodingKeys: String, CodingKey {
            case name
            case schemaVersion = "schema_version"
            case metadata
            case createdAt = "created_at"
        }
    }

    private static let storageKey = "ming.productEvents.v1"
    private static let schemaVersion = "analytics-events-v1"
    private static let allowedEvents: Set<String> = [
        "onboarding_started",
        "onboarding_completed",
        "reading_generated",
        "today_viewed",
        "seal_selected",
        "muyu_started",
        "muyu_completed",
        "quest_action_completed",
        "weekly_review_viewed",
        "oracle_started",
        "oracle_saved",
        "paywall_viewed",
        "purchase_started",
        "purchase_completed",
        "subscription_restored"
    ]
    private static let allowedMetadataKeys: Set<String> = [
        "entitlement_status",
        "plan_id",
        "product_id",
        "source",
        "status",
        "surface"
    ]

    static func record(_ name: String, metadata: [String: String] = [:]) {
        guard allowedEvents.contains(name) else { return }
        let sanitized = metadata.reduce(into: [String: String]()) { partial, entry in
            guard allowedMetadataKeys.contains(entry.key) else { return }
            let value = entry.value.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !value.isEmpty else { return }
            partial[entry.key] = String(value.prefix(96))
        }
        let event = StoredEvent(
            name: name,
            schemaVersion: schemaVersion,
            metadata: sanitized,
            createdAt: Date()
        )
        let decoder = JSONDecoder()
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
        let currentData = UserDefaults.standard.data(forKey: storageKey)
        let current = currentData.flatMap { try? decoder.decode([StoredEvent].self, from: $0) } ?? []
        let next = Array((current + [event]).suffix(50))
        if let data = try? encoder.encode(next) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
}
