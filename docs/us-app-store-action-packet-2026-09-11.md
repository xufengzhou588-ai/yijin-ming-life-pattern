# MING US App Store Action Packet - 2026-09-11

Status: current working packet for preparing the new MING / Yijing iOS app for
a United States free-first App Store release.

Latest recheck: 2026-10-10.

This packet is for the new MING app, not the existing `Couple Flight Chess`
submission shown in App Store Connect.

Do not create a new Xcode project for MING. Use the existing project:

```text
/Volumes/Data/AI 系统/Yijin/MINGLifePattern.xcodeproj
```

Create a new App Store Connect app record only if MING is not already listed in
App Store Connect.

## Current Local Evidence

- Repository: `/Volumes/Data/AI 系统/Yijin`
- Branch: `main`
- Commit: `b74f070`
- Tag on HEAD: `appstore-us-free-v1.0-rc1`
- Working tree: has release-prep changes after this packet was created:
  `.gitignore`, `MINGLifePattern.xcodeproj/project.pbxproj`,
  `.github/workflows/ios-app-store.yml`, and this release documentation.
- Version: `1.0`
- Build: `1`
- Bundle ID: `app.mingpattern.life`
- App display name: `MING`
- App Store name draft: `MING · Life Pattern`
- Release mode: `MING_PRO_MODE=free_first`
- Apple Developer Team selected in Xcode on 2026-09-14:
  `WQ8RHQUVQQ`
- App icon: `ios/MINGLifePattern/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`, 1024 x 1024
- iPhone device check on 2026-09-17:
  `ZXF`, iOS `26.6.2`, UDID `00008120-001C11410E93C01E`.
  The Mac recognizes the device, but Xcode 16.1 reports it as
  `connected (no DDI)`, so this local Xcode cannot build/run on that iPhone.
- GitHub Actions Xcode 26 workflow added on 2026-10-10:
  `.github/workflows/ios-app-store.yml`.
  Current local repository has no Git remote, so the repo must be pushed to
  GitHub before this workflow can be used.

## Validation Run Today

Run from `/Volumes/Data/AI 系统/Yijin` on 2026-09-11:

```text
PYTHONPATH='/Volumes/Data/AI 系统/Yijin' /tmp/yijin-appstore-free-venv/bin/python -m pytest -q
```

Result:

```text
54 passed
```

Re-run on 2026-10-10:

```text
PYTHONPATH='/Volumes/Data/AI 系统/Yijin' /tmp/yijin-appstore-free-venv/bin/python -m pytest -q
```

Result:

```text
54 passed
```

```text
MING_PRO_MODE=free_first APP_STORE_ENVIRONMENT=production BAZI_SESSION_SECRET=free-first-release-session-secret-2026 BAZI_COOKIE_SECURE=1 BAZI_DEMO_UNLOCK= BAZI_STOREKIT_STUB= BAZI_ALLOW_INSECURE_STOREKIT_STUB= /tmp/yijin-appstore-free-venv/bin/python tools/verify_production_config.py
```

Result:

```text
production_ready=true
missing=[]
storekit_required=false
```

Local HTTP smoke at `http://127.0.0.1:8787`:

- `/app`: 200
- `/api/entitlement`: free entitlement, `storekit_ready=false`
- `POST /api/entitlement/demo-unlock`: 403 `demo_unlock_disabled`

Local Release simulator build:

```text
xcodebuild -quiet -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Release -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build
```

Result: passed.

Generic iOS signed Release build without provisioning updates:

```text
xcodebuild -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Release -destination 'generic/platform=iOS' build
```

Result on 2026-09-14: failed because no local iOS provisioning profile matched
`app.mingpattern.life`. Xcode reported that automatic signing can generate one
when provisioning updates are allowed.

Real iPhone Debug build with provisioning updates:

```text
xcodebuild -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Debug -destination 'id=00008120-001C11410E93C01E' -allowProvisioningUpdates build
```

Result on 2026-09-17: failed before build because the device was unavailable:
`Device is busy (Waiting to reconnect to ZXF)`. `devicectl` then reported the
device as `connected (no DDI)`. Installed local Xcode is 16.1 with iOS 18.1 SDK,
which does not contain the developer support needed for the attached iOS 26.6.2
device.

## Current Blockers Before App Review

1. Public production domains do not resolve from this machine:

```text
https://mingpattern.app/app
https://mingpattern.app/legal/privacy
https://mingpattern.app/legal/terms
https://mingpattern.app/support
https://api.mingpattern.app/api/system/status
```

`curl` result today: `Could not resolve host`.

2. Xcode signing team is now selected in the project:

```text
DEVELOPMENT_TEAM = WQ8RHQUVQQ;
```

The remaining signing gap is provisioning profile creation for
`app.mingpattern.life`. Use Xcode automatic signing in the UI, or run an
`xcodebuild` command with `-allowProvisioningUpdates` after confirming that it
may create or update Apple Developer signing assets.

3. This Mac currently reports:

```text
Xcode 16.1
Build version 16B40
iPhoneOS18.1.sdk
```

Use a current App Store upload-capable Xcode on the final archive/upload
machine. Apple currently requires App Store uploads to be built with Xcode 26
or later and the iOS 26 SDK. This is also required to build or run on the
attached iOS 26.6.2 iPhone.

4. Real iPhone TestFlight smoke has not been recorded for this 1.0 free-first
submission.

5. App Store screenshots still need to be captured from the final signed build.

6. No Git remote is configured yet. The Xcode 26 GitHub Actions upload path
   requires pushing this repository to GitHub and adding the App Store Connect
   API key secrets.

## Apple Official Links

Verified HTTP 200 on 2026-09-11:

- Create App Store Connect app record:
  <https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/>
- Upload builds:
  <https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/>
- Set price:
  <https://developer.apple.com/help/app-store-connect/manage-app-pricing/set-a-price/>
- Set United States availability:
  <https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/set-availability-for-an-app/>
- Manage App Privacy:
  <https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/>
- Submit to App Review:
  <https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/>
- App Review Guidelines:
  <https://developer.apple.com/app-store/review/guidelines/>

## App Store Connect Values To Enter

Use App Store Connect: <https://appstoreconnect.apple.com/apps>

If the MING app record does not exist yet:

- Platform: `iOS`
- App name: `MING · Life Pattern`
- Primary language: `English (U.S.)`
- Bundle ID: `app.mingpattern.life`
- SKU: `MING-LIFE-PATTERN-IOS`
- User access: use full access unless the account policy requires limited app access

Pricing and availability:

- Price: `Free`
- Availability: `United States` only for the first release
- In-App Purchases: none for version `1.0`
- Subscriptions: none for version `1.0`

Categories:

- Primary category: `Lifestyle`
- Secondary category: `Reference`

Version:

- Version: `1.0`
- Build: select the uploaded build matching this repo state
- Release option: manual release after approval unless you want automatic release
- If any uploaded build is rejected, invalid, or superseded, increment
  `CURRENT_PROJECT_VERSION` before uploading again. Do not reuse a build number
  for the same version.

## Copy/Paste Metadata

Promotional text:

```text
Explore Eastern pattern wisdom through calm, traceable self-reflection.
```

Subtitle:

```text
Eastern patterns, modern self-reflection
```

Keywords, within the 100-character limit:

```text
I Ching,BaZi,Four Pillars,self reflection,journal,life pattern
```

Description:

```text
MING turns Chinese Four Pillars and I Ching-inspired structure into a modern self-reflection experience.

Enter your birth details to generate a structured life-pattern reading that explores how you tend to move, connect, build, decide, and respond to change. MING emphasizes traceable reasoning, plain-language interpretation, and practical reflection rather than fixed prediction.

Free launch features include:

- A core life-pattern overview
- Structured chart output
- Plain-language interpretation
- Timing and annual rhythm references
- Privacy-first local review
- Clear boundaries around what the reading can and cannot decide for you

MING is for cultural exploration, journaling, and personal reflection. It is not medical, legal, financial, mental-health, safety, or emergency advice, and it does not promise future outcomes.

Pro reports, monthly guidance, guided oracle reflection, and subscription access are planned for a later update.
```

Review notes:

```text
MING's first App Store release is free.

This build does not include active In-App Purchase, external payment, or active subscriptions. The Pro tab and Pro sections preview planned future functionality only. No purchase, restore purchase, or test unlock flow is available in this free-first build.

MING is an informational lifestyle app for cultural exploration and personal reflection. It translates Chinese Four Pillars and I Ching-inspired structures into modern language. It does not provide medical, legal, financial, mental-health, safety, or emergency advice. It does not promise outcomes or make fixed predictions.

Reviewer instructions:

1. Open the app.
2. Use the Reading tab to generate a free life-pattern reading.
3. Open the Pro tab to view planned future Pro features.
4. Confirm no purchase is available in this version.
5. Use Trust to open Privacy Policy, Terms, and Support.
```

URLs:

```text
Marketing URL: https://mingpattern.app/app
Privacy Policy URL: https://mingpattern.app/legal/privacy
Support URL: https://mingpattern.app/support
Terms of Use: https://mingpattern.app/legal/terms
```

Do not paste these URLs until DNS and hosting are live.

## App Privacy Draft

Final answers must match production hosting and logging. Current expected
free-first answers:

- Tracking: `No`
- Third-party advertising: `No`
- Data used to track users across apps and websites: `No`
- Active purchases or subscriptions in 1.0: `No`
- Account signup required: `No`

Expected data use if production only processes readings and stores sanitized
first-party analytics:

- Birth details / chart inputs: used for App Functionality
- Product interaction events: App Functionality and Analytics, not linked to the user
- Diagnostics, if enabled: App Functionality and Analytics, not linked to the user

Do not declare:

- third-party advertising;
- data broker sharing;
- raw birth date/time/place in analytics;
- oracle question text or generated reading text in analytics;
- purchases for the 1.0 free-first submission.
- crash data, diagnostics, or analytics as tracking unless the app actually
  tracks users across apps or websites and implements the required ATT flow.

User confirmation needed before final privacy labels:

- Does the production server retain raw birth details?
- Does the production server retain oracle questions or journal text?
- Is first-party analytics enabled in production?
- Are crash logs or diagnostics collected through Apple or another service?

## Age Rating Draft

Expected answer set:

- Violence, sexual content, profanity, horror, medical/treatment information,
  alcohol/tobacco/drug references, gambling, contests: `None` / `No`
- Unrestricted web access: `No`

Rationale: the app uses a controlled `WKWebView` for its own web experience and
legal/support pages; it is not a general-purpose browser.

## Screenshot Plan

Capture after the final signed build can open the live production URLs.

Minimum required set:

- 6.7-inch iPhone display
- 6.1-inch iPhone display

Recommended sequence:

1. Reading input screen
2. Generated free life-pattern overview
3. Structured chart or reasoning section
4. Pro preview, with no purchase button
5. Oracle/reflection area if visible in final build
6. Trust/legal/support screen

Do not show localhost, debug controls, demo unlock, external payment language,
or active subscription pricing in 1.0 screenshots.

## Review Video Plan

Prepare a short real-device recording before submission or be ready to attach it
in Resolution Center:

1. Launch MING.
2. Generate a free life-pattern reading.
3. Open the Pro preview and show that there is no purchase, restore, or demo
   unlock flow in version 1.0.
4. Open Privacy Policy, Terms, and Support links.
5. Mention the tested device model and iOS version in App Review Notes.

## User Steps Needed

1. Confirm or create the Apple Developer Bundle ID:
   `app.mingpattern.life`.
   Status on 2026-09-14: user reported this is complete.

2. In Xcode, select the Apple Developer Team for target `MINGLifePattern`.
   Keep automatic signing unless your account policy requires manual profiles.
   Do this in the existing MING project, not by creating a new Xcode project.
   Status on 2026-09-14: complete; Team ID is `WQ8RHQUVQQ`.

3. In App Store Connect, create a new app record for MING if it does not exist.
   Do not reuse the `Couple Flight Chess` app record.

4. Let Xcode create the provisioning profile:

- UI path: open the MING target, keep `Automatically manage signing` enabled,
  and fix any red signing issue shown by Xcode.
- CLI path, only after explicit confirmation:

```text
xcodebuild -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Release -destination 'generic/platform=iOS' -allowProvisioningUpdates build
```

5. Deploy the production web/API service and configure DNS so these resolve:

```text
mingpattern.app
api.mingpattern.app
```

Production environment for free-first:

```text
MING_PRO_MODE=free_first
APP_STORE_ENVIRONMENT=production
BAZI_SESSION_SECRET=<stable random secret, at least 32 characters>
BAZI_COOKIE_SECURE=1
BAZI_DEMO_UNLOCK=
BAZI_STOREKIT_STUB=
BAZI_ALLOW_INSECURE_STOREKIT_STUB=
```

6. After DNS is live, run or ask Codex to run:

```text
curl -L -I https://mingpattern.app/app
curl -L -I https://mingpattern.app/legal/privacy
curl -L -I https://mingpattern.app/legal/terms
curl -L -I https://mingpattern.app/support
curl -s https://api.mingpattern.app/api/system/status
```

7. Archive and upload the iOS build from an upload-capable Xcode 26+ machine.
   Preferred cloud path: use `.github/workflows/ios-app-store.yml` after the
   repository is pushed to GitHub and the App Store Connect API secrets are set.

8. In App Store Connect, create/select the MING app record and paste the values
   above.

9. Fill copyright:

```text
Copyright: 2026 <your legal name or company>
```

10. Fill support contact information:

```text
Support email: support@mingpattern.app
Phone: <optional business support phone, if you want to provide one>
Address: <business address if your account requires it>
```

11. Run TestFlight on a real iPhone:

- first launch;
- generate a free reading;
- open Pro preview and confirm no purchase/restore/demo unlock;
- open Privacy Policy, Terms, Support, and Methodology links;
- test small-screen readability and Dynamic Type;
- test VoiceOver focus on primary controls.

12. Submit to App Review after screenshots, privacy labels, pricing, and
    availability are complete.

## Do Not Submit In Version 1.0

- Subscription products
- Paid pricing
- External payment links
- StoreKit Sandbox evidence as a release blocker
- Demo unlock controls
- Pro claims that imply active paid access in this build

## Existing Supporting Files

- `ios/AppStoreConnect/app-metadata-free-first-en-US.md`
- `ios/AppStoreConnect/review-notes-free-first.md`
- `ios/AppStoreConnect/privacy-questionnaire.md`
- `ios/AppStoreConnect/age-rating-questionnaire.md`
- `ios/AppStoreConnect/screenshot-plan.md`
- `ios/AppStoreConnect/xcode26-upload-runbook.md`
- `docs/us-free-app-store-launch-2026-09-07.md`
