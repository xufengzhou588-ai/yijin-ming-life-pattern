# MING iOS Shell

This folder contains the SwiftUI source skeleton for the App Store version of
`MING · Life Pattern`.

The first release strategy is a native iOS shell with:

- SwiftUI tab navigation;
- WKWebView for the existing life-pattern experience;
- native StoreKit2 Pro purchase and restore flow;
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
10. Add StoreKit products from `ios/StoreKit/storekit-products-local.md` or create a `.storekit` file in Xcode.

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

## StoreKit Product IDs

- `ming.pro.monthly`
- `ming.pro.yearly`

The app source uses these IDs in `StoreKitManager.productIDs`.

## App Store Boundary

MING Pro sells digital interpretation content. It must use App Store IAP.
Do not add external payment links or external purchase language.

## Current Gap

The Python backend exposes a production-shaped entitlement object, but it does
not yet validate App Store signed transactions. Implement
`POST /api/app-store/transactions` before TestFlight payment testing.
