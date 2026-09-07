# App Store Server Validation v1

## Goal

Replace local demo Pro access with App Store verified subscription access.

The iOS app sends StoreKit2 signed transaction data to:

```text
POST /api/app-store/transactions
```

The backend validates the transaction with Apple, normalizes the result, and
returns the entitlement shape already used by the web prototype and iOS shell.

## Request

```json
{
  "signed_transaction": "<StoreKit2 transaction.jwsRepresentation>",
  "transaction_id": "<StoreKit2 transaction id>",
  "original_transaction_id": "<StoreKit2 original transaction id>",
  "app_account_token": "<UUID>",
  "anonymous_install_id": "<UUID>"
}
```

## Success Response

```json
{
  "ok": true,
  "entitlement": {
    "status": "pro_active",
    "is_pro": true,
    "tier": "pro",
    "source": "app_store",
    "environment": "production",
    "product_id": "ming.pro.yearly",
    "expires_at": "2027-06-30T00:00:00Z",
    "needs_restore": false,
    "can_demo_unlock": false,
    "storekit_ready": true
  }
}
```

## Error Response

```json
{
  "ok": false,
  "error": "app_store_validation_not_configured"
}
```

## Required Apple Credentials

Before production validation, prepare:

- App Store Connect issuer ID.
- Key ID.
- Private key `.p8`.
- Bundle ID.
- App Apple ID.
- Apple root certificates for App Store Server Library verification.

## Backend Environment Variables

Required production variables:

```text
APP_STORE_ISSUER_ID=
APP_STORE_KEY_ID=
APP_STORE_PRIVATE_KEY_PATH=
APP_STORE_ROOT_CERT_PATHS=
APP_STORE_BUNDLE_ID=app.mingpattern.life
APP_STORE_APP_APPLE_ID=
APP_STORE_ENVIRONMENT=production
BAZI_ENTITLEMENT_DB_PATH=/absolute/path/to/entitlements.sqlite3
BAZI_SESSION_SECRET=<stable random secret, at least 32 characters>
BAZI_COOKIE_SECURE=1
```

`APP_STORE_PRIVATE_KEY` may be used instead of `APP_STORE_PRIVATE_KEY_PATH`
when the deploy platform stores multiline secrets directly.

## Validation Rules

1. Verify the signed transaction with Apple or App Store Server API.
2. Accept only product IDs in:
   - `ming.pro.monthly`
   - `ming.pro.yearly`
3. Reject revoked transactions.
4. Treat expired subscriptions as `expired`.
5. Treat no matching active transaction as `free` or `needs_restore`.
6. Never unlock Pro from frontend state alone.

## Persistence and Session Rules

- `server.py` persists entitlement records in SQLite at
  `BAZI_ENTITLEMENT_DB_PATH`.
- The canonical record is aliased by app account token, original transaction
  ID, transaction ID, and anonymous install ID when available.
- The `bazi_session` cookie is signed and short-lived. It contains a subject
  pointer, not an entitlement grant.
- Pro endpoints re-read the server-side entitlement record before serving paid
  content.
- Expired, revoked, missing, or unreadable records fail closed to Free or
  `needs_restore`.

## Diagnostics

Run this in the production environment before release:

```bash
python tools/verify_production_config.py
```

The script prints the same `deployment` object exposed by
`GET /api/system/status` and exits nonzero until all production requirements are
present.

## Local Stub Status

For local UI testing only:

```bash
BAZI_STOREKIT_STUB=1 BAZI_ALLOW_INSECURE_STOREKIT_STUB=1 APP_STORE_ENVIRONMENT=sandbox \
python server.py
```

This returns a sandbox-like Pro entitlement. The stub is disabled when
`APP_STORE_ENVIRONMENT=production`; do not use it for TestFlight or production.

## Current Implementation Status

`server.py` includes production-shaped handlers for:

- `POST /api/app-store/transactions`
- `POST /api/app-store/notifications`

The handlers load App Store Server API and signed-data-verifier configuration
from environment variables, validate StoreKit signed transaction JWS payloads,
normalize subscription states into the app entitlement contract, and reject
unsupported product IDs.

Real Apple validation still requires credentials and Apple root certificates in
the runtime environment. Without those values, the endpoint returns
`app_store_validation_not_configured`, clears any existing Pro session cookie,
and returns a non-Pro entitlement.

For local UI testing only:

```powershell
$env:BAZI_ALLOW_INSECURE_STOREKIT_STUB="1"
$env:BAZI_STOREKIT_STUB="1"
python server.py
```

This returns a sandbox-like Pro entitlement only when
`APP_STORE_ENVIRONMENT` is not `production`. Do not use the stub for TestFlight,
App Review, or production.

See `docs/p5-02-storekit-sandbox-app-store-submission-2026-08-25.md` for the
current Sandbox QA and submission checklist.
