# Xcode 26 Upload Runbook

Status: final upload checklist for a Mac that meets Apple upload requirements.

## Why This Runbook Exists

This project currently compiles locally with Xcode 16.1 for simulator development. Apple upload requirements for new App Store builds require a newer Xcode toolchain, so the final archive/upload must be performed on a compatible Mac with Xcode 26+ and valid Apple Developer signing.

## Prerequisites

- Apple Developer Program membership.
- App Store Connect app record for `MING · Life Pattern`.
- Bundle ID: `app.mingpattern.life`.
- Xcode 26+ selected with `xcode-select`.
- Signing team configured in Xcode.
- Subscription products created:
  - `ming.pro.monthly`
  - `ming.pro.yearly`
- Public HTTPS URLs live:
  - `https://mingpattern.app/app`
  - `https://mingpattern.app/legal/privacy`
  - `https://mingpattern.app/legal/terms`
  - `https://mingpattern.app/support`

## Xcode UI Upload Path

1. Open `MINGLifePattern.xcodeproj`.
2. Select target `MINGLifePattern`.
3. Set Team under Signing & Capabilities.
4. Confirm Bundle Identifier is `app.mingpattern.life`.
5. Confirm Version and Build in `Info.plist`.
6. Select a generic iOS device destination.
7. Run `Product > Archive`.
8. In Organizer, choose `Distribute App`.
9. Select `App Store Connect`.
10. Upload symbols.
11. Let Xcode manage signing unless the team requires manual profiles.
12. Upload.

## Command-Line Archive Path

From the project root:

```bash
xcodebuild \
  -project MINGLifePattern.xcodeproj \
  -scheme MINGLifePattern \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath build/MINGLifePattern.xcarchive \
  clean archive
```

Then upload/export:

```bash
xcodebuild \
  -exportArchive \
  -archivePath build/MINGLifePattern.xcarchive \
  -exportPath build/AppStoreUpload \
  -exportOptionsPlist ios/AppStoreConnect/exportOptions-app-store-connect.plist
```

## Pre-Upload Verification

Run before archive:

```bash
bash tools/mac_verify.sh
```

Then manually verify on a simulator or device:

- launch app;
- generate a free reading;
- open Pro tab;
- products load from StoreKit sandbox;
- purchase sandbox subscription;
- restore purchase;
- web reading unlocks Pro through native entitlement;
- legal/support links open;
- no demo unlock endpoint works in production mode.

## Known Local Limitation

The local Intel Mac with Xcode 16.1 is useful for development builds and simulator compile checks. It should not be treated as the final App Store upload machine.
