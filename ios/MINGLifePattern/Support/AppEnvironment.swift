import Foundation

enum AppEnvironment {
    enum ProMode: String {
        case freeFirst = "free_first"
        case storeKit = "storekit"
    }

    static var webAppURL: URL {
        urlFromInfoDictionary(
            key: "MING_WEB_APP_URL",
            fallback: "https://mingpattern.app/app"
        )
    }

    static var apiBaseURL: URL {
        urlFromInfoDictionary(
            key: "MING_API_BASE_URL",
            fallback: "https://api.mingpattern.app"
        )
    }

    static var privacyURL: URL {
        urlFromInfoDictionary(
            key: "MING_PRIVACY_URL",
            fallback: "https://mingpattern.app/legal/privacy"
        )
    }

    static var termsURL: URL {
        urlFromInfoDictionary(
            key: "MING_TERMS_URL",
            fallback: "https://mingpattern.app/legal/terms"
        )
    }

    static var supportURL: URL {
        urlFromInfoDictionary(
            key: "MING_SUPPORT_URL",
            fallback: "https://mingpattern.app/support"
        )
    }

    static var methodologyURL: URL {
        urlFromInfoDictionary(
            key: "MING_METHODOLOGY_URL",
            fallback: "https://mingpattern.app/legal/methodology"
        )
    }

    static var proMode: ProMode {
        if let environmentValue = ProcessInfo.processInfo.environment["MING_PRO_MODE"],
           let mode = ProMode(rawValue: environmentValue) {
            return mode
        }
        if let rawValue = Bundle.main.object(forInfoDictionaryKey: "MING_PRO_MODE") as? String,
           let mode = ProMode(rawValue: rawValue) {
            return mode
        }
        return .storeKit
    }

    static var isFreeFirstRelease: Bool {
        proMode == .freeFirst
    }

    private static func urlFromInfoDictionary(key: String, fallback: String) -> URL {
        if let environmentValue = ProcessInfo.processInfo.environment[key],
           let environmentURL = URL(string: environmentValue) {
            return environmentURL
        }
        let rawValue = Bundle.main.object(forInfoDictionaryKey: key) as? String
        return URL(string: rawValue ?? fallback) ?? URL(string: fallback)!
    }
}
