# TestFlight QA Checklist — 2026-08-25

Goal: validate the P3 US paid-release candidate with 50-100 US testers.

## Build Sanity

- App installs from TestFlight.
- App launches without crash.
- Version/build number matches App Store Connect.
- App icon appears correctly.
- App name appears as `MING`.
- Release build is not launched with `MING_PRO_MODE=free_first`.

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

## Pro / StoreKit Flow

- Monthly product loads as `ming.pro.monthly`.
- Yearly product loads as `ming.pro.yearly`.
- Price and billing period come from StoreKit.
- Paywall does not say Coming Soon in the release build.
- Terms, Privacy, Support, and methodology links are visible.
- Purchase sandbox monthly subscription.
- Purchase sandbox yearly subscription if practical.
- App sends StoreKit signed transaction to backend.
- Entitlement changes to Pro only after backend response.
- WebView receives server session cookie, not a self-declared Pro flag.
- Kill and relaunch app; entitlement remains correct.
- Restore Purchase works.
- Expired/no-purchase sandbox account shows a clear non-Pro state.
- Refund, revocation, expiry, renewal, and restore are verified through backend entitlement state before public release.

## Anonymous Analytics

- Events follow `docs/analytics-events-v1.md`.
- `onboarding_started` and `onboarding_completed` do not include birth details.
- `reading_generated` does not include birth date, birth time, country, region, city, timezone, longitude, or latitude.
- Oracle raw questions and journal text are not sent to analytics.
- StoreKit records only purchase/restore event names and product/entitlement status.

## Accessibility and Device Matrix

- VoiceOver can complete onboarding.
- VoiceOver can generate a reading.
- VoiceOver can complete daily seal selection, Muyu Reset, small action, and evening mark.
- VoiceOver can restore purchase.
- Dynamic Type does not clip paywall, Today, or legal text.
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
- Would you pay for Monthly Compass, Oracle Journal, review history, or ritual soundscapes?
- Which price felt acceptable: USD 7.99, 8.99, or 9.99 monthly?
- Which yearly price felt acceptable: USD 39.99, 49.99, or 59.99?

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
- Subscription group and products are approved or ready for review.
- Public HTTPS URLs are live.
- Screenshots match the current UI.
- Review notes explain the non-fatalistic boundary and StoreKit flow.

## Pass / Fail Notes

- Tester:
- Device:
- iOS version:
- Build:
- Result:
- Issues:
