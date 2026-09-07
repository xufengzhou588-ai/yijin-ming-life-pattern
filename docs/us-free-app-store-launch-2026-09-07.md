# US Free App Store Launch - 2026-09-07

Status: current release target. Ship MING 1.0 as a free United States App Store
release with no active In-App Purchase, no external payment, and no StoreKit
Sandbox requirement for this first submission.

## Release Configuration

- Branch/worktree: `app-store-prep-20260826` at
  `/Volumes/Data/AI 系统/Yijin-AppStorePrep`.
- Version: `1.0`.
- Build: `1`.
- Bundle ID: `app.mingpattern.life`.
- iOS build mode: `MING_PRO_MODE=free_first` in
  `ios/MINGLifePattern/Resources/Info.plist`.
- Web default mode: `/app` defaults to `free_first`.
- Paid mode for later testing: use `MING_PRO_MODE=storekit` or
  `/app?release=storekit`.

## Apple Source Checkpoint

Checked on 2026-09-07. These Apple pages returned HTTP 200:

- App Review Guidelines:
  <https://developer.apple.com/app-store/review/guidelines/>
- Submit an app:
  <https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/>
- Set a price:
  <https://developer.apple.com/help/app-store-connect/manage-app-pricing/set-a-price/>
- Set availability for an app:
  <https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/set-availability-for-an-app/>
- Manage app privacy:
  <https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/>
- Provide a privacy policy URL:
  <https://developer.apple.com/help/app-store-connect/manage-app-information/provide-a-privacy-policy-url/>

## App Store Connect Target

- Distribution: United States first.
- Price: Free.
- In-App Purchases: none in this 1.0 submission.
- App Privacy: use the current free-first privacy questionnaire after production
  analytics is frozen.
- Review notes: use `ios/AppStoreConnect/review-notes-free-first.md` or the
  synced `ios/AppStoreConnect/review-notes.md`.
- Metadata: use `ios/AppStoreConnect/app-metadata-free-first-en-US.md`.

## Engineering Definition of Done

- Free reading generation works.
- Pro surfaces are previews only.
- No purchase button appears in free-first native or web surfaces.
- No Restore Purchase button appears in free-first native or web surfaces.
- No demo unlock appears by default.
- Native StoreKit loading is skipped in the app startup path.
- Backend Pro endpoints still fail closed if called directly.
- Public web `/app` defaults to the free-first experience.
- StoreKit credentials are not required for `MING_PRO_MODE=free_first`
  production diagnostics.

## Local Validation - 2026-09-07

Commands run from `/Volumes/Data/AI 系统/Yijin-AppStorePrep`:

- `PYTHONPATH='/Volumes/Data/AI 系统/Yijin-AppStorePrep' /tmp/yijin-appstore-free-venv/bin/python -m pytest -q`
  - Result: 54 passed.
- `python3 -m py_compile server.py tests/test_nav_paywall_a11y.py`
  - Result: passed.
- `node --check web/js/app-v20260826.js && node --check web/js/locales-v20260826.js && node --check web/js/analytics-v20260826.js`
  - Result: passed.
- `plutil -lint ios/MINGLifePattern/Resources/Info.plist`
  - Result: passed.
- `git diff --check && git diff --cached --check`
  - Result: passed.
- `xcodebuild -quiet -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build`
  - Result: passed.
- `xcodebuild -quiet -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Release -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build`
  - Result: passed.
- `MING_PRO_MODE=free_first APP_STORE_ENVIRONMENT=production BAZI_SESSION_SECRET=free-first-release-session-secret-2026 BAZI_COOKIE_SECURE=1 BAZI_DEMO_UNLOCK= BAZI_STOREKIT_STUB= BAZI_ALLOW_INSECURE_STOREKIT_STUB= /tmp/yijin-appstore-free-venv/bin/python tools/verify_production_config.py`
  - Result: `production_ready=true`, `missing=[]`, `storekit_required=false`.
- `MING_PRO_MODE=storekit APP_STORE_ENVIRONMENT=production BAZI_SESSION_SECRET=short BAZI_COOKIE_SECURE=0 BAZI_DEMO_UNLOCK=1 /tmp/yijin-appstore-free-venv/bin/python tools/verify_production_config.py`
  - Result: failed as expected for the later paid mode.

Local HTTP smoke at `http://127.0.0.1:8787`:

- `/app`: 200 with security headers.
- `/api/system/status`: `pro_mode=free_first`, `storekit_required=false`.
- `/api/entitlement`: free entitlement, `storekit_ready=false`,
  `can_demo_unlock=false`.
- `POST /api/entitlement/demo-unlock`: 403 `demo_unlock_disabled`.

Playwright smoke:

- Viewports: 1440x900, 390x844, 320x640.
- Public `/app` defaulted to free-first with no `release` query parameter.
- Free reading generated.
- MING Pro preview opened from the Me/Pro surface.
- No native purchase button, Restore Purchase button, demo unlock, or dollar
  price appeared.
- Only the Back button appeared in the Pro preview action row.
- Minimum action target height was at least 44 px.
- No horizontal overflow.
- Back returned focus to the originating Pro card.
- Screenshots: `/tmp/yijin-free-appstore-smoke-20260907`.

## Production Environment for Free First

Required before final hosted verification:

```text
MING_PRO_MODE=free_first
APP_STORE_ENVIRONMENT=production
BAZI_SESSION_SECRET=<stable random secret, at least 32 characters>
BAZI_COOKIE_SECURE=1
BAZI_DEMO_UNLOCK=
BAZI_STOREKIT_STUB=
BAZI_ALLOW_INSECURE_STOREKIT_STUB=
```

Not required for the 1.0 free submission:

- `APP_STORE_ISSUER_ID`
- `APP_STORE_KEY_ID`
- `APP_STORE_PRIVATE_KEY` or `APP_STORE_PRIVATE_KEY_PATH`
- `APP_STORE_ROOT_CERT_PATHS`
- `APP_STORE_APP_APPLE_ID`
- subscription product records
- StoreKit Sandbox purchase/restore QA

Those return as blockers only when `MING_PRO_MODE=storekit`.

## Remaining External Operations

- Confirm Apple Developer team and signing identity.
- Create or confirm the App Store Connect app record for `MING · Life Pattern`.
- Confirm Bundle ID `app.mingpattern.life`.
- Set price to Free.
- Set availability to United States for the first release.
- Paste the free-first metadata, privacy URL, support URL, and review notes.
- Upload screenshots from the final signed build.
- Archive and upload with Xcode on a machine signed into the Apple Developer
  team.
- Run TestFlight smoke on at least one real iPhone before submitting to App
  Review.

## Later Paid Update

Do not submit subscription products with 1.0. For v1.1 paid Pro, switch
`MING_PRO_MODE=storekit`, configure App Store Server API credentials, create
`ming.pro.monthly` and `ming.pro.yearly`, and run the full StoreKit Sandbox and
TestFlight purchase/restore matrix.
