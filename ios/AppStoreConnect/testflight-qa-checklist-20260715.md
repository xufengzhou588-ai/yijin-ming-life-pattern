# TestFlight QA Checklist — 2026-07-15

Goal: verify the first uploadable build as soon as Xcode 26+ signing/upload is available.

## Build Sanity

- App installs from TestFlight.
- App launches without crash.
- Version/build number matches App Store Connect.
- App icon appears correctly on the home screen.
- App name appears as `MING`.

## Reading Flow

- Open Reading tab.
- Birth-date input is usable.
- Birth-time input is usable.
- Birthplace input is usable.
- Generate a free life-pattern reading.
- Reading copy avoids guaranteed/fatalistic claims.
- Refresh/relaunch preserves only intended local state.

## Pro / StoreKit Flow

- Open Pro tab.
- Monthly product loads as `ming.pro.monthly`.
- Yearly product loads as `ming.pro.yearly`.
- Price and billing period come from StoreKit.
- Terms and Privacy links are visible.
- Purchase sandbox monthly subscription.
- Entitlement changes to Pro.
- Web reading unlocks Pro content through the native entitlement cookie.
- Kill and relaunch app; entitlement remains active.
- Restore Purchase works.
- Expired/no-purchase sandbox account shows a clear non-Pro state.

## Legal / Trust Flow

- Privacy Policy opens.
- Terms of Use opens.
- Support page opens.
- Copy states the app is for cultural exploration and personal reflection.
- Copy states the app is not medical, legal, financial, mental-health, safety, or emergency advice.

## Backend / Security Flow

- `BAZI_DEMO_UNLOCK` is not enabled in production.
- Demo unlock endpoints do not grant Pro unless explicitly enabled in local development.
- App Store transaction validation endpoint is reachable.
- Server logs do not store raw birth details or oracle questions unnecessarily.

## Review Readiness

- App Review notes are pasted.
- Privacy labels match actual production behavior.
- Screenshots match current UI.
- Subscription group and products are approved or ready for review.
- Public HTTPS URLs are live.

## Pass / Fail Notes

- Tester:
- Device:
- iOS version:
- Build:
- Result:
- Issues:

