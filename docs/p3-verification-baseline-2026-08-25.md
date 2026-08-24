# P3 Verification Baseline

Date: 2026-08-25

## Automated Checks Passed

- JavaScript syntax:
  - `web/js/state-v20260826.js`
  - `web/js/storage-v20260826.js`
  - `web/js/api-v20260826.js`
  - `web/js/analytics-v20260826.js`
  - `web/js/locales-v20260826.js`
  - `web/js/app-v20260826.js`
- Locale JSON parse:
  - `web/locales/zh-CN.json`
  - `web/locales/en-US.json`
- Python unit tests: 32 tests passed.
- iOS Simulator build:
  - `xcodebuild -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -sdk iphonesimulator -configuration Debug build CODE_SIGNING_ALLOWED=NO`
  - Result: build succeeded.
- Web static accessibility audit:
  - high severity warnings: 0.
- Web token audit:
  - high severity warnings: 0.
- HTTP smoke:
  - `/app`: 200.
  - `/js/app-v20260826.js`: 200 with immutable cache.
  - `/js/analytics-v20260826.js`: 200 with immutable cache.
  - `/legal/privacy.html`: 200.
- `git diff --check`: passed.

## Manual Release Checks Still Required

- StoreKit Sandbox purchase and restore with real App Store Connect products.
- Subscription expiry, refund, revocation, renewal, and restore entitlement state.
- App Privacy labels in App Store Connect against the final production upload behavior.
- VoiceOver, Dynamic Type, landscape, and small-screen end-to-end testing.
- 50-100 US TestFlight testers and survey notes.
- Public HTTPS URLs for privacy, terms, support, and marketing.
