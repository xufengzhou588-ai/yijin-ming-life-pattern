# MING iOS Shell

This folder contains the SwiftUI source skeleton for the App Store version of
`MING · Life Pattern`.

The first release strategy is a native iOS shell with:

- SwiftUI navigation;
- WKWebView for the existing life-pattern experience;
- free-first MING Pro preview with no active purchase or Restore Purchase flow;
- native Trust screen for privacy, terms, and support;
- production-shaped entitlement models matching the Python backend.

## Create the Xcode Project

1. Open Xcode on macOS.
2. Create a new iOS App project.
3. Product name: `MINGLifePattern`.
4. Interface: SwiftUI.
5. Language: Swift.
6. Minimum deployment target: iOS 17.0 for the first sprint.
7. Bundle ID target: `app.mingpattern.life`.
8. Copy the files under `ios/MINGLifePattern/` into the Xcode target.
9. Add `ios/MINGLifePattern/Resources/Info.plist` values to the target Info settings.
10. Confirm `MING_PRO_MODE` is `free_first` for the 1.0 App Store submission.

## Required Runtime URLs

For TestFlight and App Review these must become public HTTPS endpoints:

- `MING_WEB_APP_URL`
- `MING_API_BASE_URL`
- `MING_PRIVACY_URL`
- `MING_TERMS_URL`
- `MING_SUPPORT_URL`

The current defaults are placeholders:

- `https://mingpattern.app/app`
- `https://api.mingpattern.app`
- `https://mingpattern.app/legal/privacy`
- `https://mingpattern.app/legal/terms`
- `https://mingpattern.app/support`

## Later StoreKit Product IDs

- `ming.pro.monthly`
- `ming.pro.yearly`

The app source uses these IDs in `StoreKitManager.productIDs`, but StoreKit is
not started when `MING_PRO_MODE=free_first`.

## App Store Boundary

MING 1.0 is free. It must not show purchase, Restore Purchase, external payment
links, or external purchase language.

The later paid MING Pro update sells digital interpretation content and must use
App Store IAP.

## Current StoreKit Status

The Python backend exposes `POST /api/app-store/transactions` and
`POST /api/app-store/notifications` for App Store signed transaction and server
notification validation.

Real Sandbox/TestFlight testing still requires App Store Connect products,
sandbox tester accounts, Apple signing, public HTTPS runtime URLs, and App
Store Server API credentials configured on the backend. Do not use the local
demo unlock or insecure StoreKit stub as App Review evidence.

Use `docs/p5-02-storekit-sandbox-app-store-submission-2026-08-25.md` for the
later paid Sandbox QA checklist, evidence template, and remaining submission
blockers.
