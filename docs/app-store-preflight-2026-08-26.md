# App Store Preflight - 2026-08-26

Status: superseded for the immediate 1.0 launch by
`docs/us-free-app-store-launch-2026-09-07.md`. This file remains the paid/P5
preflight evidence. The immediate target is now a United States free-first App
Store release with no active In-App Purchase.

## Apple Source Checkpoint

Checked on 2026-08-26 in the Asia/Shanghai workspace. These Apple pages returned
HTTP 200 and are the current submission references used for this preflight:

- App Review Guidelines:
  <https://developer.apple.com/app-store/review/guidelines/>
- Submit an app:
  <https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/>
- Submit an In-App Purchase:
  <https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-in-app-purchase/>
- Manage app privacy:
  <https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/>
- Provide a privacy policy URL:
  <https://developer.apple.com/help/app-store-connect/manage-app-information/provide-a-privacy-policy-url/>
- Overview for configuring In-App Purchases:
  <https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/overview-for-configuring-in-app-purchases/>
- Generate keys for In-App Purchases:
  <https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/generate-keys-for-in-app-purchases/>
- Enter server URLs for App Store Server Notifications:
  <https://developer.apple.com/help/app-store-connect/configure-in-app-purchase-settings/enter-server-urls-for-app-store-server-notifications/>
- Overview of testing in Sandbox:
  <https://developer.apple.com/help/app-store-connect/test-in-app-purchases/overview-of-testing-in-sandbox/>
- Testing subscriptions and In-App Purchases in TestFlight:
  <https://developer.apple.com/help/app-store-connect/test-a-beta-version/testing-subscriptions-and-in-app-purchases-in-testflight/>

Submission mapping for MING:

- Backend services must be live and reachable during review.
- App Review Notes must explain the WKWebView, cultural-reflection positioning,
  Pro subscriptions, Restore Purchase, and any non-obvious gated flows.
- Privacy answers must match the final production analytics and backend storage
  behavior at upload time.
- In-App Purchase records and subscription products must exist in App Store
  Connect and be submitted with the app when required.
- StoreKit Sandbox and TestFlight subscription flows must pass before App Review.

## Integrated Engineering Scope

- P5-01 production persistence and entitlement fail-closed behavior.
- P5-02 StoreKit transaction sync, server validation stubs, App Store Server
  Notification endpoint, and submission packet updates.
- P5-03 native navigation, Paywall exit state, restore affordance, focus return,
  small-screen web Paywall checks, and a11y static tests.
- P5-04 anonymous first-party funnel events, local queue, upload endpoint,
  US TestFlight experiment assignment, and privacy data inventory updates.

The integration also fixed three merge regressions:

- Restore/no-entitlement copy now says "No active Pro subscription was found for
  this Apple ID."
- `APIClient.APIError` conforms directly to `LocalizedError`.
- `AppAnalytics.regionScope` no longer emits the iOS 16 `regionCode`
  deprecation warning.

## Validation Run

Commands run from `/Volumes/Data/AI 系统/Yijin-AppStorePrep`:

- `PYTHONPATH='/Volumes/Data/AI 系统/Yijin-AppStorePrep' /private/tmp/yijin-p5-03-venv/bin/python -m pytest -q`
  - Result: 52 passed.
- `python3 -m py_compile server.py tests/test_nav_paywall_a11y.py`
  - Result: passed.
- `node --check web/js/app-v20260826.js && node --check web/js/locales-v20260826.js && node --check web/js/analytics-v20260826.js`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `git diff --cached --check`
  - Result: passed.
- `xcodebuild -quiet -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build`
  - Result: passed with no output after the `Locale` deprecation fix.
- `/private/tmp/yijin-p5-03-venv/bin/python tools/verify_production_config.py`
  - Result: failed as expected because production credentials and release
    environment variables are not configured in this local workspace.

Local HTTP smoke at `http://127.0.0.1:8787`:

- `/app`: 200 with security headers.
- `/api/entitlement`: free entitlement, `storekit_ready=false`,
  `can_demo_unlock=false`.
- `POST /api/entitlement/demo-unlock`: 403 `demo_unlock_disabled`.
- Forged `bazi_native_pro=1` cookie against `POST /api/pro/report`: 403
  `pro_required`.
- `POST /api/analytics/events`: 200, one v2 event accepted.

Playwright smoke:

- Viewports: 1440x900, 390x844, 320x640.
- Paywall visible after switching to Me/Pro.
- No horizontal overflow.
- Paywall receives focus.
- Buttons are ordered as native App Store subscription, Restore Purchase, Back.
- Minimum Paywall button target height is at least 44 px.
- Back button removes the Paywall and returns focus to the original Pro card.
- Screenshots: `/tmp/yijin-appstoreprep-smoke-20260826`.

## Current Release Blockers

Production config gate currently reports these missing items:

- `APP_STORE_ENVIRONMENT=production`
- `APP_STORE_ISSUER_ID`
- `APP_STORE_KEY_ID`
- `APP_STORE_PRIVATE_KEY` or `APP_STORE_PRIVATE_KEY_PATH`
- `APP_STORE_ROOT_CERT_PATHS`
- `BAZI_COOKIE_SECURE=1`
- `BAZI_ENTITLEMENT_DB_PATH`
- `BAZI_SESSION_SECRET>=32`

App Store Connect blockers:

- Confirm Apple Developer team and signing identity.
- Confirm Bundle ID `app.mingpattern.life` is registered and matches Xcode.
- Create the App Store Connect app record.
- Create subscription products `ming.pro.monthly` and `ming.pro.yearly`.
- Confirm pricing, territories, tax category, subscription group, display names,
  descriptions, review screenshots, and localization.
- Configure App Store Server API key and production server notification URL.
- Fill final privacy answers from `ios/AppStoreConnect/privacy-questionnaire.md`
  after production analytics behavior is frozen.
- Publish public HTTPS URLs for privacy, terms, support, app web experience, and
  API.
- Capture final App Store screenshots from a signed build.
- Upload archive from the Apple signing machine and run TestFlight review.

QA blockers:

- StoreKit Sandbox purchase, cancel, pending, restore, expiry, refund, and
  revocation paths are still untested against real App Store Connect products.
- VoiceOver on device is still untested.
- Dynamic Type on device is still untested.
- Real small-device layout is still untested.
- US TestFlight experiment needs a real TestFlight build and testers.

## User Confirmations Needed

- Apple Developer account/team access and whether `app.mingpattern.life` is the
  final Bundle ID.
- Final production domains:
  `https://mingpattern.app`, `https://api.mingpattern.app`, privacy, terms, and
  support URLs.
- Final subscription prices and territories for monthly/yearly Pro.
- Whether anonymous first-party analytics remains enabled in production or only
  in TestFlight.
- Final App Store category, subtitle, keywords, support contact, and review
  note wording.
- Whether to merge this integration branch back to `main` now, or keep it as a
  staging branch until production credentials and App Store Connect setup are
  available.
