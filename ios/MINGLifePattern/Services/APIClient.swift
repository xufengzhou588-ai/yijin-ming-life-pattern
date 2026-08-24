import Foundation

struct APIClient {
    enum APIError: Error {
        case invalidResponse
        case server(String)
    }

    let baseURL: URL

    init(baseURL: URL = AppEnvironment.apiBaseURL) {
        self.baseURL = baseURL
    }

    func fetchEntitlement() async throws -> Entitlement {
        let url = baseURL.appending(path: "/api/entitlement")
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw APIError.invalidResponse
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(EntitlementResponse.self, from: data)
        guard payload.ok else { throw APIError.server("entitlement_unavailable") }
        return payload.entitlement
    }

    func syncAppStoreTransaction(jwsRepresentation: String) async throws -> Entitlement {
        let url = baseURL.appending(path: "/api/app-store/transactions")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(["signed_transaction": jwsRepresentation])

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw APIError.invalidResponse
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(EntitlementResponse.self, from: data)
        guard payload.ok else { throw APIError.server("transaction_sync_failed") }
        return payload.entitlement
    }
}
