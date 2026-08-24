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
  "signed_transaction": "<StoreKit2 transaction.jwsRepresentation>"
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
- Shared secret only if legacy receipt validation remains necessary.

## Backend Environment Variables

Proposed names:

```text
APP_STORE_ISSUER_ID=
APP_STORE_KEY_ID=
APP_STORE_PRIVATE_KEY_PATH=
APP_STORE_BUNDLE_ID=app.mingpattern.life
APP_STORE_ENVIRONMENT=sandbox|production
```

## Validation Rules

1. Verify the signed transaction with Apple or App Store Server API.
2. Accept only product IDs in:
   - `ming.pro.monthly`
   - `ming.pro.yearly`
3. Reject revoked transactions.
4. Treat expired subscriptions as `expired`.
5. Treat no matching active transaction as `free` or `needs_restore`.
6. Never unlock Pro from frontend state alone.

## Current Prototype Status

`server.py` now includes `POST /api/app-store/transactions`, but real Apple
validation is not implemented yet.

For local UI testing only:

```powershell
$env:BAZI_STOREKIT_STUB="1"
python server.py
```

This returns a sandbox-like Pro entitlement. Do not use the stub for TestFlight
or production.
