# P5 Production Persistence

Date: 2026-08-25

## Scope

This pass covers `P5-01 production deployment and persistent Pro entitlement`.
The current branch is based on `3e81ad1 Prepare P3 US paid release`; there is
no independent P4 completion commit or P4 acceptance record in this worktree.
CloudKit, Widget, Relationship Reflection, and other P4/future items remain
future scope unless a separate P4 branch is merged back first.

## Entitlement Source

- App Store signed transactions are validated on the backend through
  `POST /api/app-store/transactions`.
- Active, expired, revoked, and restore-needed states are normalized into
  `EntitlementRecord`.
- Records are persisted in SQLite at `BAZI_ENTITLEMENT_DB_PATH`.
- The persistent record is indexed by the canonical subject plus available
  aliases: app account token, original transaction ID, transaction ID, and
  anonymous install ID.
- The `bazi_session` cookie is a short-lived signed subject pointer. It cannot
  grant Pro unless the backend can find an active persisted entitlement record.
- The old `bazi_native_pro=1` cookie is ignored by the backend and is actively
  cleared by the iOS WebView bridge.
- Local demo unlock remains disabled by default and requires
  `BAZI_DEMO_UNLOCK=1`. StoreKit stub unlock requires both
  `BAZI_STOREKIT_STUB=1` and `BAZI_ALLOW_INSECURE_STOREKIT_STUB=1`, and is
  disabled in production.

## Production Configuration

Required environment:

```text
APP_STORE_ISSUER_ID
APP_STORE_KEY_ID
APP_STORE_PRIVATE_KEY or APP_STORE_PRIVATE_KEY_PATH
APP_STORE_ROOT_CERT_PATHS
APP_STORE_BUNDLE_ID
APP_STORE_APP_APPLE_ID
APP_STORE_ENVIRONMENT=production
BAZI_ENTITLEMENT_DB_PATH
BAZI_SESSION_SECRET
BAZI_COOKIE_SECURE=1
```

Production readiness can be checked with:

```bash
python tools/verify_production_config.py
```

The same deployment object is exposed by `GET /api/system/status`. The check
fails closed and reports missing keys instead of silently enabling Pro.

Expected public targets remain:

- Web app: `https://mingpattern.app/app`
- API: `https://api.mingpattern.app`
- Privacy: `https://mingpattern.app/legal/privacy`
- Terms: `https://mingpattern.app/legal/terms`
- Support: `https://mingpattern.app/support`

Responses now include common security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Strict-Transport-Security` when production mode or `BAZI_HSTS=1` is enabled

## Automated Coverage

Updated tests cover:

- Forged `bazi_native_pro=1` does not unlock entitlement.
- Forged `bazi_session` payload does not access Pro endpoints.
- Persisted Pro entitlement still works after in-memory cache is cleared.
- Expired persisted entitlement returns Free with `needs_restore`.
- Unsupported StoreKit product IDs return 403.
- Missing production configuration is diagnosable through `/api/system/status`.
- Existing body limit, input validation, sanitized errors, unconfigured StoreKit
  503, and signed demo session checks still pass.

## Remaining Manual Gates

These require external state and are not completed by this local branch:

- StoreKit Sandbox purchase and restore against real App Store Connect
  products.
- Subscription expiry, refund, revocation, renewal, and restore notification
  QA against Apple's sandbox/production servers.
- VoiceOver, Dynamic Type, physical small-screen, and landscape QA.
- Public HTTPS deployment, DNS, TLS, reverse proxy, and persistence volume
  verification on the production host.
- App Store Connect privacy labels and review metadata checked against the
  deployed production build.
