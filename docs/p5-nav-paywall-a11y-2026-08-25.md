# P5-03 Navigation, Paywall, And Accessibility Evidence

Date: 2026-08-25
Worktree: `/Volumes/Data/AI 系统/Yijin-P5-03`
Branch: `p5-03-nav-paywall-a11y`
Baseline: `3e81ad1 Prepare P3 US paid release`

## Scope

This pass keeps CloudKit, Widget, and Relationship Reflection out of scope because the current baseline has no independent P4 acceptance package and still marks those surfaces as future work.

## Implemented

- Replaced the native three-tab shell with a reading-first `NavigationStack`.
- Moved Trust into a leading toolbar link and MING Pro into a trailing toolbar action.
- Presents Pro in a dismissible sheet with its own `NavigationStack`, visible `Done` action, and accessible labels/hints.
- Adds a WKWebView `mingStoreKit` bridge so web paywall actions can open native purchase or restore flows in the iOS shell.
- Clears the legacy `bazi_native_pro` cookie in the WKWebView path and keeps web Pro access tied to server entitlement.
- Hides the mobile section bar until the first reading exists, then restores it for Today, Blueprint, Oracle, and Me.
- Adds mobile pane IDs, `aria-controls`, localized mobile nav labels, paywall focus handoff, and return-focus behavior.
- Sets paywall and Pro controls to at least 44 px touch targets and allows long labels to wrap on small screens.
- Keeps App Store purchase/restore text inside the native StoreKit/App Store boundary.

## Verification

- `PYTHONPATH='/Volumes/Data/AI 系统/Yijin-P5-03' /private/tmp/yijin-p5-03-venv/bin/python -m pytest -q` -> 37 passed.
- `python3 -m py_compile server.py tests/test_nav_paywall_a11y.py` -> passed.
- `node --check web/js/app-v20260826.js && node --check web/js/locales-v20260826.js` -> passed.
- `git diff --check` -> passed.
- `xcodebuild -quiet -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Debug -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build` -> passed.
- HTTP smoke: `/app` returned 200 and `/api/entitlement` returned free entitlement with demo unlock disabled.
- Playwright Chromium local checks against `http://127.0.0.1:8787/app?release=paid`:
  - 1440x900 desktop: generated reading, opened paywall, confirmed no horizontal overflow, paywall focus, 44 px actions, and return focus.
  - 390x844 mobile: initial bottom nav hidden; generated bottom nav visible; Me pane opens Pro options; paywall focus and return focus pass; no horizontal overflow.
  - 320x640 mobile: same flow passed; App Store subscription button wraps to 48 px high.
  - 768x1024 tablet: initial render nonblank with no horizontal overflow.
  - Bottom safe-area check at 390x844 and 320x640 confirmed paywall actions and legal links can scroll above the fixed mobile nav.

Screenshots were captured under `/tmp/yijin-p5-03-screens-1787671300` and `/tmp/yijin-p5-03-screens-1787671500`.

## Remaining External Gaps

- VoiceOver hardware/device pass.
- Dynamic Type on real iPhone.
- Real small-screen iPhone QA.
- StoreKit Sandbox purchase, restore, cancellation, pending, expiration, refund, and revoke states.
- Production domain, HTTPS, and App Store Connect metadata review.
