# App Store Release Blockers — 2026-07-14

Latest free-first launch checklist:
`docs/us-free-app-store-launch-2026-09-07.md`.

Paid/P5 preflight evidence: `docs/app-store-preflight-2026-08-26.md`.

This file separates local engineering work from external App Store release dependencies.

## Locally Completed

- Xcode project exists and simulator build passes.
- iOS app has native tabs, native StoreKit paywall shell, legal links, and controlled web reading view.
- Local backend supports `/app`, privacy, terms, support, and production-safe demo-unlock defaults.
- Server-validated Pro entitlement can unlock the controlled web view through a
  signed short-lived `bazi_session` cookie backed by the persistent entitlement
  store.
- App icon asset exists at 1024×1024.
- Local verification script exists at `tools/mac_verify.sh`.
- App Store Connect copy, privacy draft, age-rating draft, product setup notes, screenshot plan, TestFlight QA checklist, and Xcode 26 upload runbook are prepared.

## External Blockers Before TestFlight

1. Apple Developer Program account and signing team.
2. Mac with Xcode 26+ for the final archive/upload.
3. App Store Connect app record for `MING · Life Pattern`.
4. Bundle ID registered as `app.mingpattern.life`.
5. StoreKit products created:
   - `ming.pro.monthly`
   - `ming.pro.yearly`
6. Public HTTPS hosting for:
   - app web experience;
   - privacy policy;
   - terms;
   - support page;
   - backend entitlement endpoint.
7. App Store Server API credentials configured on the production host, with
   `tools/verify_production_config.py` passing before release.
8. Screenshots captured from the final signed/TestFlight build.

## Tomorrow Test Goal

On 2026-07-15, run the local verification script first. If an Xcode 26+ upload machine and Apple signing are available, archive and upload to TestFlight, then execute `ios/AppStoreConnect/testflight-qa-checklist-20260715.md`.
