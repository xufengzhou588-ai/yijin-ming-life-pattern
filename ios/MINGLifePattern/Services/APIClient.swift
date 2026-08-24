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

    func fetchEntitlement() async throws -> EntitlementResponse {
        let url = baseURL.appending(path: "/api/entitlement")
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw APIError.invalidResponse
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let payload = try decoder.decode(EntitlementResponse.self, from: data)
        guard payload.ok else { throw APIError.server("entitlement_unavailable") }
        return payload
    }

    func syncAppStoreTransaction(
        jwsRepresentation: String,
        transactionID: String,
        originalTransactionID: String,
        appAccountToken: UUID?,
        anonymousInstallID: UUID
    ) async throws -> EntitlementResponse {
        let url = baseURL.appending(path: "/api/app-store/transactions")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = AppStoreTransactionSyncRequest(
            signedTransaction: jwsRepresentation,
            transactionID: transactionID,
            originalTransactionID: originalTransactionID,
            appAccountToken: appAccountToken,
            anonymousInstallID: anonymousInstallID
        )
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        if !(200..<300).contains(http.statusCode) {
            if let errorPayload = try? decoder.decode(APIErrorResponse.self, from: data) {
                throw APIError.server(errorPayload.error)
            }
            throw APIError.invalidResponse
        }
        let payload = try decoder.decode(EntitlementResponse.self, from: data)
        guard payload.ok else { throw APIError.server("transaction_sync_failed") }
        return payload
    }
}

private struct AppStoreTransactionSyncRequest: Encodable {
    let signedTransaction: String
    let transactionID: String
    let originalTransactionID: String
    let appAccountToken: UUID?
    let anonymousInstallID: UUID

    enum CodingKeys: String, CodingKey {
        case signedTransaction = "signed_transaction"
        case transactionID = "transaction_id"
        case originalTransactionID = "original_transaction_id"
        case appAccountToken = "app_account_token"
        case anonymousInstallID = "anonymous_install_id"
    }
}

private struct APIErrorResponse: Decodable {
    let error: String
}
