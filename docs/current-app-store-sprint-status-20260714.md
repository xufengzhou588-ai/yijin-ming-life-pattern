# Current App Store Sprint Status - 2026-07-14

## Build Status

- Xcode selected: `/Applications/Xcode.app/Contents/Developer`
- Local Xcode version: Xcode 16.1, build 16B40
- iOS Simulator runtime installed: iOS 18.1
- Xcode project exists: `MINGLifePattern.xcodeproj`
- iOS simulator Debug build: passing
- Python/backend tests: passing, `12 passed`

## Implemented in This Sprint

- Created a usable Xcode project around the existing SwiftUI shell.
- Added a complete app `Info.plist` with display name, bundle values, ATS local-networking allowance, launch screen, and orientation keys.
- Added an AppIcon asset catalog with a 1024x1024 icon generated from the product header art using a square crop.
- Added local debug environment support so the iOS shell can point to `http://127.0.0.1:8787`.
- Added native-to-web Pro entitlement bridge using a `bazi_native_pro` cookie after StoreKit verifies an active purchase.
- Disabled demo Pro unlock by default; it is now only available when `BAZI_DEMO_UNLOCK=1`.
- Added clean URL aliases for App Store URLs:
  - `/app`
  - `/legal/privacy`
  - `/legal/terms`
  - `/legal/support`
  - `/support`
- Added `HEAD` support for URL checks.
- Adjusted `jsonschema` to `4.25.1` so the project works with macOS system Python 3.9.
- Added repeatable Mac verification scripts:
  - `tools/mac_verify.sh`
  - `tools/start_mac_local_server.sh`
- Added an App Store Connect preparation packet:
  - `ios/AppStoreConnect/app-metadata-en-US.md`
  - `ios/AppStoreConnect/privacy-questionnaire.md`
  - `ios/AppStoreConnect/age-rating-questionnaire.md`
  - `ios/AppStoreConnect/subscription-products.md`
  - `ios/AppStoreConnect/review-notes.md`
  - `ios/AppStoreConnect/screenshot-plan.md`
  - `ios/AppStoreConnect/testflight-qa-checklist-20260715.md`
  - `ios/AppStoreConnect/xcode26-upload-runbook.md`
  - `ios/AppStoreConnect/exportOptions-app-store-connect.plist`
- Added a sprint packaging script:
  - `tools/package_appstore_sprint.sh`
- Added a release-blocker tracker:
  - `docs/app-store-release-blockers-20260714.md`

## Current Constraints

- Xcode 16.1 can build and test locally, but cannot upload new App Store Connect builds under Apple's 2026 upload requirements.
- Final TestFlight/App Store upload needs Xcode 26+ on macOS 15.6+.
- This Mac is useful for development; it is not the final upload machine.
- Simulator visual launch was attempted, but first-boot migration stalled in LaunchServices on this Intel Mac. The app build itself passes.

## Remaining Before TestFlight Upload

1. Build/archive on a machine with Xcode 26+.
2. Add Apple Developer Team ID and signing.
3. Create App Store Connect app record for bundle ID `app.mingpattern.life`.
4. Create subscription group `MING Pro`.
5. Create products:
   - `ming.pro.monthly`
   - `ming.pro.yearly`
6. Replace production placeholder URLs if the final domain differs:
   - `https://mingpattern.app/app`
   - `https://api.mingpattern.app`
   - `https://mingpattern.app/legal/privacy`
   - `https://mingpattern.app/legal/terms`
   - `https://mingpattern.app/support`
7. Host the web app, API, legal pages, and support page on public HTTPS.
8. Capture App Store screenshots.
9. Complete App Store privacy questionnaire.
10. Upload TestFlight build and run purchase/restore QA.

## Tomorrow Test Plan - 2026-07-15

1. Run local verification:

   ```bash
   cd "/Volumes/Data/AI 系统/Yijin"
   bash tools/mac_verify.sh
   ```

2. If an Xcode 26+ machine and Apple signing are available, follow:

   ```text
   ios/AppStoreConnect/xcode26-upload-runbook.md
   ```

3. After the build is available in TestFlight, run:

   ```text
   ios/AppStoreConnect/testflight-qa-checklist-20260715.md
   ```

## Important Risk

The current native purchase flow preserves locally verified StoreKit entitlement in the app. Backend App Store Server API validation is still not fully wired because Apple issuer/key/team credentials are not present in this workspace. For a fast TestFlight submission this can be acceptable for app-side entitlement testing, but production should validate signed transactions server-side before relying on backend-gated Pro content.

## Local Verification

Run:

```bash
cd "/Volumes/Data/AI 系统/Yijin"
bash tools/mac_verify.sh
```

Start the local backend:

```bash
cd "/Volumes/Data/AI 系统/Yijin"
bash tools/start_mac_local_server.sh
```

For Xcode GUI local debugging, use the `MINGLifePattern` scheme. It contains local URL environment variables for the Debug launch action.
