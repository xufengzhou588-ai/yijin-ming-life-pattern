# TestFlight QA Checklist — 2026-08-25

Goal: validate the 1.0 United States free-first App Store candidate before App
Review. This checklist intentionally excludes active In-App Purchase testing.

## Build Sanity

- App installs from TestFlight.
- App launches without crash.
- Version/build number matches App Store Connect.
- App icon appears correctly.
- App name appears as `MING`.
- Release build uses `MING_PRO_MODE=free_first`.
- Public `/app` defaults to the free-first experience.

## First-Run and Reading

- No default fake chart appears before user input.
- Onboarding explains product purpose, birth data, time accuracy, privacy, and generation.
- Birth-date input is usable.
- Birth-time input supports unknown or approximate time.
- Birthplace input is usable.
- Generate a free life-pattern reading.
- Editing birth data requires confirmation and does not silently overwrite old history.
- Reading copy avoids guaranteed/fatalistic claims.

## Today Retention

- App relaunch defaults to Today after setup.
- User can understand today's focus within 5 seconds.
- User can select Focus, Spark, Ground, Connect, or Restore.
- User can complete Muyu Reset without tutorial.
- User can choose one small action.
- Evening mark supports completed, adjusted, and skipped.
- Skipping does not show failure or punishment language.
- Seven-day trail and monthly review update from local records.

## Muyu Reset / Mindful Tap Study

- US tester understands `Muyu Reset` without opening Chinese Roots.
- `Mindful Tap` feels like one sound, one breath, one intention.
- 30-second and 60-second durations both work.
- Sound can be disabled.
- Haptics can be disabled.
- Motion respects reduced motion.
- Completion copy is `Intention set` / "You made space before acting."
- No merit score, luck currency, auto-tapping, or leaderboard appears.

## Pro Preview / No Purchase Flow

- MING Pro opens as a planned-feature preview.
- Pro cards show planned future value without active purchase claims.
- No monthly product loads.
- No yearly product loads.
- No price or billing period appears.
- No purchase button appears.
- No Restore Purchase button appears.
- No demo unlock button appears.
- Terms, Privacy, Support, and methodology links are visible.
- Direct Pro endpoint calls still return 403 without a server-verified
  entitlement.

StoreKit purchase, restore, cancellation, pending, refund, revocation, expiry,
and renewal testing is deferred to the v1.1 paid update. Record that later
evidence in `docs/p5-02-storekit-sandbox-app-store-submission-2026-08-25.md`.

## Anonymous Analytics

- Events follow `docs/analytics-events-v1.md` with current schema `analytics-events-v2`.
- `first_open`, `experiment_exposure`, and `free_entitlement` appear for a fresh install.
- `anonymous_install_id` remains stable across relaunch; `anonymous_session_id` changes only by session/app process.
- `experiment.key` is `us_testflight_paywall_copy` and variant is stable for the install.
- US readout filters use `release_channel=testflight` and `region_scope=us_testflight`.
- `onboarding_started` and `onboarding_completed` do not include birth details.
- `reading_generated` does not include birth date, birth time, country, region, city, timezone, longitude, or latitude.
- Oracle raw questions and journal text are not sent to analytics.
- Locked Pro attempts produce `pro_gate_denied` and `paywall_view`.
- StoreKit purchase and restore events do not appear in the free-first flow.
- Offline, disabled, or failed analytics upload does not block onboarding,
  reading, planned-Pro preview, or locked Pro gate checks.
- Server JSONL rows contain no IP address, user agent, birth fields, precise location, Oracle question, report text, or journal text.

## Accessibility and Device Matrix

- VoiceOver can complete onboarding.
- VoiceOver can generate a reading.
- VoiceOver can complete daily seal selection, Muyu Reset, small action, and evening mark.
- VoiceOver can dismiss the MING Pro preview.
- Dynamic Type does not clip Pro preview, Today, or legal text.
- Reduced Motion removes nonessential animation.
- Landscape layout remains usable.
- 320, 390, 768, 1024, and 1440 px widths have no obvious overflow.

## US Localization Study

Ask each tester:

- Could you explain what Bazi contributes after the first reading?
- Did any English copy feel literally translated or unclear?
- Did you trust the result? Why or why not?
- Did uncertainty around birth time make sense?
- Would you return tomorrow? Why or why not?
- Which planned Pro feature sounded most useful: Monthly Compass, Oracle
  Journal, review history, or ritual soundscapes?
- Would you consider a paid Pro update later? Why or why not?

## Legal / Trust Flow

- Privacy Policy opens from the app.
- Terms of Use opens from the app.
- Support page opens from the app.
- Refund/support instructions are clear.
- Data deletion instructions are clear for local saved data.
- Copy states the app is for cultural exploration and personal reflection.
- Copy states the app is not medical, legal, financial, mental-health, safety, or emergency advice.

## App Store Connect Readiness

- App Privacy details match the production implementation.
- App price is Free.
- First availability is United States.
- No In-App Purchase products are submitted with 1.0.
- Public HTTPS URLs are live.
- Screenshots match the current UI.
- Review notes explain the non-fatalistic boundary and no-purchase free-first
  release.

## Pass / Fail Notes

- Tester:
- Device:
- iOS version:
- Build:
- Result:
- Issues:
