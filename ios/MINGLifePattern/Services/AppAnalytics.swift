import Foundation

@MainActor
enum AppAnalytics {
    struct RecordOptions {
        let oncePerInstall: Bool
        let throttleSeconds: TimeInterval?

        init(oncePerInstall: Bool = false, throttleSeconds: TimeInterval? = nil) {
            self.oncePerInstall = oncePerInstall
            self.throttleSeconds = throttleSeconds
        }
    }

    private struct ExperimentAssignment: Codable {
        let key: String
        let variant: String
        let bucket: Int
    }

    private struct StoredEvent: Codable {
        let eventID: String
        let name: String
        let schemaVersion: String
        let anonymousInstallID: String
        let anonymousSessionID: String
        let sequence: Int
        let releaseChannel: String
        let regionScope: String
        let experiment: ExperimentAssignment
        let metadata: [String: String]
        let createdAt: Date

        enum CodingKeys: String, CodingKey {
            case eventID = "event_id"
            case name
            case schemaVersion = "schema_version"
            case anonymousInstallID = "anonymous_install_id"
            case anonymousSessionID = "anonymous_session_id"
            case sequence
            case releaseChannel = "release_channel"
            case regionScope = "region_scope"
            case experiment
            case metadata
            case createdAt = "created_at"
        }
    }

    private struct UploadEnvelope: Encodable {
        let schemaVersion: String
        let events: [StoredEvent]

        enum CodingKeys: String, CodingKey {
            case schemaVersion = "schema_version"
            case events
        }
    }

    private static let storageKey = "ming.productEvents.v1"
    private static let sequenceKey = "ming.analytics.sequence.v1"
    private static let sentMarkerPrefix = "ming.analytics.sentMarker."
    private static let throttlePrefix = "ming.analytics.throttle."
    private static let schemaVersion = "analytics-events-v2"
    private static let runtimeSessionID = UUID()
    private static let uploadLimit = 25
    private static let queueLimit = 200
    private static let allowedEvents: Set<String> = [
        "first_open",
        "onboarding_started",
        "onboarding_completed",
        "free_entitlement",
        "reading_generated",
        "today_viewed",
        "seal_selected",
        "muyu_started",
        "muyu_completed",
        "quest_action_completed",
        "weekly_review_viewed",
        "oracle_started",
        "oracle_saved",
        "paywall_view",
        "purchase_start",
        "purchase_success",
        "purchase_failure",
        "purchase_cancel",
        "restore",
        "pro_gate_denied",
        "experiment_exposure"
    ]
    private static let allowedMetadataKeys: Set<String> = [
        "action_key",
        "app_build",
        "cancel_reason",
        "duration_seconds",
        "entitlement_status",
        "entitlement_tier",
        "error_code",
        "experiment_key",
        "failure_stage",
        "language",
        "module",
        "plan_id",
        "placement",
        "product_id",
        "quest_id",
        "reason",
        "review_period",
        "seal_key",
        "source",
        "status",
        "storekit_environment",
        "surface",
        "time_accuracy",
        "true_solar_time",
        "week_index",
        "variant"
    ]
    private static let forbiddenMetadataKeys: Set<String> = [
        "birth_date",
        "birth_datetime",
        "birth_time",
        "body",
        "city",
        "content",
        "country",
        "display_name",
        "email",
        "journal",
        "latitude",
        "longitude",
        "name",
        "payload",
        "question",
        "region",
        "report",
        "result",
        "text",
        "timezone"
    ]
    private static let defaultThrottleSeconds: [String: TimeInterval] = [
        "paywall_view": 30,
        "pro_gate_denied": 30,
        "experiment_exposure": 300,
        "restore": 30
    ]

    @discardableResult
    static func record(_ name: String, metadata: [String: String] = [:], options: RecordOptions = RecordOptions()) -> Bool {
        guard allowedEvents.contains(name), !isDisabled else { return false }
        let sanitized = sanitize(metadata)
        let fingerprint = "\(name):\(sanitized.sorted { $0.key < $1.key })"
        if options.oncePerInstall && hasAlreadyRecorded(fingerprint) {
            return false
        }
        if isThrottled(name: name, fingerprint: fingerprint, options: options) {
            return false
        }

        let event = StoredEvent(
            eventID: UUID().uuidString.lowercased(),
            name: name,
            schemaVersion: schemaVersion,
            anonymousInstallID: InstallationIdentity.analyticsInstallID.uuidString.lowercased(),
            anonymousSessionID: anonymousSessionID.uuidString.lowercased(),
            sequence: nextSequence(),
            releaseChannel: releaseChannel,
            regionScope: regionScope,
            experiment: experimentAssignment(),
            metadata: sanitized,
            createdAt: Date()
        )
        var current = loadEvents()
        current.append(event)
        saveEvents(Array(current.suffix(queueLimit)))
        flush()
        return true
    }

    private static var isDisabled: Bool {
        ProcessInfo.processInfo.environment["MING_ANALYTICS_DISABLED"] == "1"
    }

    private static var anonymousSessionID: UUID {
        runtimeSessionID
    }

    private static var releaseChannel: String {
        if let override = ProcessInfo.processInfo.environment["MING_RELEASE_CHANNEL"],
           ["testflight", "app_store", "local"].contains(override) {
            return override
        }
        if let receiptName = Bundle.main.appStoreReceiptURL?.lastPathComponent,
           receiptName == "sandboxReceipt" {
            return "testflight"
        }
        return "app_store"
    }

    private static var regionScope: String {
        guard releaseChannel == "testflight" else { return "not_testflight" }
        let regionCode: String
        if #available(iOS 16.0, *) {
            regionCode = Locale.current.region?.identifier ?? ""
        } else {
            regionCode = Locale.current.regionCode ?? ""
        }
        return regionCode.uppercased() == "US" ? "us_testflight" : "non_us_testflight"
    }

    private static func experimentAssignment(key: String = "us_testflight_paywall_copy") -> ExperimentAssignment {
        let bucket = stableBucket("\(InstallationIdentity.analyticsInstallID.uuidString):\(key)")
        return ExperimentAssignment(
            key: key,
            variant: bucket < 50 ? "control" : "value_stack",
            bucket: bucket
        )
    }

    private static func sanitize(_ metadata: [String: String]) -> [String: String] {
        metadata.reduce(into: [String: String]()) { partial, entry in
            guard allowedMetadataKeys.contains(entry.key), !forbiddenMetadataKeys.contains(entry.key) else { return }
            let value = entry.value.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !value.isEmpty, value.count <= 96 else { return }
            guard !value.contains("@"), value.range(of: #"\b\d{4}-\d{2}-\d{2}\b"#, options: .regularExpression) == nil else { return }
            partial[entry.key] = value
        }
    }

    private static func hasAlreadyRecorded(_ fingerprint: String) -> Bool {
        let key = sentMarkerPrefix + String(stableHash(fingerprint))
        if UserDefaults.standard.bool(forKey: key) {
            return true
        }
        UserDefaults.standard.set(true, forKey: key)
        return false
    }

    private static func isThrottled(name: String, fingerprint: String, options: RecordOptions) -> Bool {
        let seconds = options.throttleSeconds ?? defaultThrottleSeconds[name] ?? 0
        guard seconds > 0 else { return false }
        let key = throttlePrefix + String(stableHash(fingerprint))
        let now = Date().timeIntervalSince1970
        let previous = UserDefaults.standard.double(forKey: key)
        if now - previous < seconds {
            return true
        }
        UserDefaults.standard.set(now, forKey: key)
        return false
    }

    private static func nextSequence() -> Int {
        let next = UserDefaults.standard.integer(forKey: sequenceKey) + 1
        UserDefaults.standard.set(next, forKey: sequenceKey)
        return next
    }

    private static func loadEvents() -> [StoredEvent] {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else { return [] }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return (try? decoder.decode([StoredEvent].self, from: data)) ?? []
    }

    private static func saveEvents(_ events: [StoredEvent]) {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        if let data = try? encoder.encode(events) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }

    private static func flush() {
        let batch = Array(loadEvents().prefix(uploadLimit))
        guard !batch.isEmpty else { return }
        Task {
            do {
                let url = AppEnvironment.apiBaseURL.appending(path: "/api/analytics/events")
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                let encoder = JSONEncoder()
                encoder.dateEncodingStrategy = .iso8601
                request.httpBody = try encoder.encode(UploadEnvelope(schemaVersion: schemaVersion, events: batch))

                let (_, response) = try await URLSession.shared.data(for: request)
                guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else { return }
                let sentIDs = Set(batch.map(\.eventID))
                saveEvents(loadEvents().filter { !sentIDs.contains($0.eventID) })
            } catch {
                return
            }
        }
    }

    private static func stableBucket(_ value: String) -> Int {
        Int(stableHash(value) % 100)
    }

    private static func stableHash(_ value: String) -> UInt32 {
        var hash: UInt32 = 2_166_136_261
        for scalar in value.unicodeScalars {
            hash ^= UInt32(scalar.value)
            hash = hash &* 16_777_619
        }
        return hash
    }
}
