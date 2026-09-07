# P5-02 StoreKit Sandbox and App Store Submission

Date: 2026-08-25

## Scope

Complete the P5-02 release gate for StoreKit Sandbox validation and App Store
submission preparation.

Current repository baseline:

- Branch: `p5-02-storekit-submission`
- Baseline HEAD: `3e81ad1 Prepare P3 US paid release`
- P4 work is not present as a separate local commit or acceptance packet in
  this worktree. CloudKit, Widget, Relationship Reflection, and similar P4/P6
  items remain future scope for this task.

## Product and Entitlement Contract

The release build must use only these auto-renewable subscription products:

| StoreKit product ID | App entitlement | Feature tier |
| --- | --- | --- |
| `ming.pro.monthly` | `pro_active` while active | `pro` |
| `ming.pro.yearly` | `pro_active` while active | `pro` |

Implementation checkpoints:

- iOS allowlist: `StoreKitManager.productIDs`
- Backend allowlist: `ALLOWED_PRODUCT_IDS`
- Backend sync endpoint: `POST /api/app-store/transactions`
- Backend notification endpoint: `POST /api/app-store/notifications`
- Session handoff to WebView: signed `bazi_session`; legacy
  `bazi_native_pro` is cleared.
- Demo unlock and insecure StoreKit stub are not acceptable for TestFlight or
  App Review evidence.

## StoreKit Flow Acceptance

| Flow | Required result |
| --- | --- |
| Product load | Monthly and yearly products load from StoreKit with price and billing period. |
| Purchase success | App sends `transaction.jwsRepresentation` to backend; Pro unlocks only after backend returns `pro_active`. |
| Restore success | `AppStore.sync()` runs, current entitlements are synchronized, and Pro unlocks only after backend confirmation. |
| User cancels purchase | App shows cancelled state and no entitlement/session is issued. |
| Pending purchase | App shows pending state and keeps Pro locked until Apple completes the transaction. |
| Backend unavailable | App shows validation unavailable and keeps Pro locked. |
| No active subscription | Restore reports no active subscription for the Apple ID and keeps Pro locked. |
| Expired subscription | Public entitlement is `expired`, `is_pro=false`, `needs_restore=true`; Pro endpoints return 403. |
| Revoked/refunded subscription | Public entitlement is `revoked`, `is_pro=false`, `needs_restore=true`; Pro endpoints return 403. |
| Unsupported product | Backend returns 403 and does not issue a session. |

## Sandbox QA Prerequisites

Real Sandbox/TestFlight evidence requires external Apple state that is not
available in this worktree:

- App Store Connect app record for bundle ID `app.mingpattern.life`.
- Subscription group `MING Pro`.
- Active products `ming.pro.monthly` and `ming.pro.yearly`.
- Sandbox Apple Accounts in App Store Connect.
- Signed iOS build with a valid Apple Developer Team.
- Backend deployed over HTTPS with App Store Server API credentials:
  - `APP_STORE_ISSUER_ID`
  - `APP_STORE_KEY_ID`
  - `APP_STORE_PRIVATE_KEY` or `APP_STORE_PRIVATE_KEY_PATH`
  - `APP_STORE_BUNDLE_ID=app.mingpattern.life`
  - `APP_STORE_ENVIRONMENT=sandbox`
  - `APP_STORE_ROOT_CERT_PATHS`
- `BAZI_STOREKIT_STUB` and `BAZI_ALLOW_INSECURE_STOREKIT_STUB` unset for any
  Sandbox/TestFlight evidence.

Local Xcode StoreKit configuration is useful for UI and state-machine checks,
but it is not a substitute for App Store Connect Sandbox/TestFlight evidence.

Apple references:

- StoreKit Sandbox testing:
  `https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-sandbox`
- App Store Connect in-app purchase testing:
  `https://developer.apple.com/help/app-store-connect/test-in-app-purchases/overview-of-testing-in-sandbox`
- Sandbox Apple Account setup:
  `https://developer.apple.com/help/app-store-connect/test-in-app-purchases/create-a-sandbox-apple-account`
- TestFlight in-app purchase testing:
  `https://developer.apple.com/help/app-store-connect/test-a-beta-version/testing-subscriptions-and-in-app-purchases-in-testflight`
- App privacy overview:
  `https://developer.apple.com/help/app-store-connect/manage-app-privacy/overview-of-app-privacy`

## Sandbox Evidence Template

Use one row per test case. Attach screenshots or logs beside this checklist.

| Field | Value |
| --- | --- |
| Tester |  |
| Sandbox Apple Account |  |
| Device / simulator |  |
| iOS version |  |
| App version / build |  |
| Xcode version |  |
| Backend URL |  |
| `APP_STORE_ENVIRONMENT` | `sandbox` |
| Products loaded from ASC | monthly / yearly |
| Server validation mode | real Apple validation only |

| Case | Steps | Expected | Actual | Evidence |
| --- | --- | --- | --- | --- |
| Product load | Open Pro tab. | Both product IDs load with StoreKit price and period. | Blocked: ASC products not available in this workspace. |  |
| Purchase monthly | Buy `ming.pro.monthly` with sandbox account. | Backend returns `pro_active`, WebView receives `bazi_session`, Pro endpoint 200. | Blocked: ASC products, signed build, and Apple validation credentials unavailable. |  |
| Purchase yearly | Buy `ming.pro.yearly` with sandbox account. | Same as monthly, product ID yearly. | Blocked: same as above. |  |
| Restore after reinstall | Delete/reinstall app, sign into same sandbox account, tap Restore Purchase. | Pro restores only after backend sync. | Blocked: same as above. |  |
| Cancel purchase | Start purchase and cancel Apple sheet. | App shows cancelled state; no Pro session. | Not run: needs simulator/device purchase sheet. |  |
| Pending purchase | Use Ask to Buy or StoreKit test state to force pending. | App shows pending; Pro remains locked. | Not run: requires Sandbox family/Ask to Buy or local StoreKit session. |  |
| Backend unavailable | Point app at backend without Apple credentials and attempt sync. | Validation unavailable; Pro remains locked; cookie cleared. | Covered by Python test `test_app_store_validation_unconfigured_is_503_not_501`. | Test output |
| Expired subscription | Advance sandbox renewal/expiry or use server notification. | Entitlement `expired`, Pro endpoint 403. | Covered at backend mapping level by Python tests; real Sandbox not run. | Test output |
| Revoked/refunded | Trigger refund/revoke notification or server status. | Entitlement `revoked`, Pro endpoint 403. | Covered at backend mapping level by Python tests; real Sandbox not run. | Test output |
| Unsupported product | Send transaction for unknown product. | Backend 403, no session. | Covered by Python test `test_unsupported_storekit_product_is_rejected`. | Test output |

## App Store Submission Checklist

Bundle and build:

- Bundle ID is `app.mingpattern.life`.
- Display name is `MING`.
- Version/build currently resolve to `1.0 (1)`.
- Minimum deployment target is iOS 17.0.
- `MING_PRO_MODE` is `storekit`.
- `DEVELOPMENT_TEAM` is still empty in the Xcode project and must be set before
  signing/archive.
- Build/archive must be performed on the required current Xcode/App Store
  upload environment.

Runtime URLs:

- `https://mingpattern.app/app`
- `https://api.mingpattern.app`
- `https://mingpattern.app/legal/privacy`
- `https://mingpattern.app/legal/terms`
- `https://mingpattern.app/support`
- `https://mingpattern.app/legal/methodology`

Before submission, verify all URLs return production HTTPS content from a device
outside the developer network.

Subscription metadata:

- Subscription group: `MING Pro`
- Product IDs: `ming.pro.monthly`, `ming.pro.yearly`
- Product type: auto-renewable subscriptions
- Launch intro offer: none
- Paywall must show product name, StoreKit price/period, Restore Purchase,
  Terms, Privacy, Support, and no external payment language.

Privacy:

- No tracking unless the production build adds third-party tracking.
- No third-party advertising.
- Birth details and oracle/journal text must not be sent to analytics.
- Purchase/entitlement information is used for app functionality.
- Privacy labels must be rechecked against production logging and analytics
  before upload.

Review notes:

- Explain that MING is cultural reflection/journaling and not professional
  advice.
- Explain that Pro is sold only through Apple auto-renewable subscriptions.
- Provide sandbox tester credentials only through App Review Information after
  the products are active.
- Do not provide a production bypass or non-IAP unlock.

Screenshots and metadata:

- Capture screenshots from the final signed build, not the mock/demo web build.
- Include first reading, Today loop, Pro paywall with live StoreKit price, Trust
  links, and privacy/deletion support.
- Do not show Coming Soon Pro in the paid release build.
- Metadata must avoid destiny, fortune, miracle, guaranteed wealth,
  guaranteed relationship, diagnosis, or professional-advice language.

## Current Status

Completed in this worktree:

- StoreKit UI now distinguishes purchased, restored, cancelled, pending, no
  active subscription, and failed validation states.
- Paywall now shows Terms, Privacy, and Support links directly on the Pro
  screen.
- Backend tests cover sandbox stub success, production stub rejection,
  unconfigured validation failure, expired/no-Pro entitlement, invalid
  transaction payload, StoreKit status mapping, and unsupported products.
- Submission docs now identify real Sandbox blockers instead of treating local
  StoreKit/demo paths as release evidence.

Not completed because external state is missing:

- Real Sandbox monthly/yearly purchase.
- Real restore after reinstall with a sandbox account.
- Real cancellation/pending Apple purchase sheet run.
- Real expiry/refund/revocation through App Store Server Notifications or ASC
  subscription status.
- App Store Connect product screenshots and approval state.
- Production HTTPS and signing/upload verification.

Local checks on 2026-08-25:

- No App Store Server environment variables were present in the shell.
- No `.storekit` configuration file exists in this worktree.
- `curl -L -I --max-time 15 https://mingpattern.app/app` failed with
  `Could not resolve host: mingpattern.app`; the production domain is not ready
  from this environment.
- Xcode installed locally is 16.1, which is enough for a local no-sign build
  check but not enough for the Xcode 26+ upload gate recorded in the existing
  release runbooks.
