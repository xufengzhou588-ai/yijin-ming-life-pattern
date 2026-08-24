# P3 US Paid Release Plan

Date: 2026-08-25

## Goal

Prepare MING for US TestFlight and paid App Store release without changing the
product boundary: reflective, non-fatalistic, privacy-conscious, and not framed
as professional advice.

## Product Tiers

### Free

- Core life-pattern blueprint.
- Today card.
- Daily seal: Focus, Spark, Ground, Connect, Restore.
- Daily Muyu Reset.
- One seven-day pattern quest.
- Simple Oracle preview.
- On-device history.

### One-Time Purchases

Static or edition-based reports are better suited to one-time purchase:

- Complete Life Blueprint: test USD 9.99, 11.99, and 14.99.
- Year Ahead: test around USD 11.99 as an annual-edition purchase.
- Relationship Reflection: later single-purchase product after the first paid
  launch proves demand.

Implementation note: the current entitlement contract is subscription-shaped.
One-time purchases must not be exposed as buyable until the backend adds
non-subscription entitlement scopes.

### Pro Subscription

Ongoing value belongs in Pro:

- Monthly Compass.
- Complete Oracle and Journal.
- Personalized seven-day quests.
- Weekly and monthly history reviews.
- More rituals and soundscapes.
- Future cross-device sync.

Recommended price experiments:

- Monthly: USD 7.99, 8.99, 9.99.
- Yearly: USD 39.99, 49.99, 59.99.

Current control values remain `ming.pro.monthly` at USD 9.99 and
`ming.pro.yearly` at USD 59.99 until App Store Connect testing changes them.

## Charging Rules

- Do not sell luck, merit, random rewards, auto-tapping, leaderboards, or
  guaranteed outcomes.
- Static readings can be one-time purchases.
- Continuous interpretation, history, reviews, rituals, and sync can be
  subscriptions.
- Paywall copy must describe concrete value: reasoning depth, monthly review,
  Oracle journal, ritual customization, and private history.
- Pro gates must use backend entitlement. The WebView cannot self-declare Pro.

## Anonymous Analytics

Use `docs/analytics-events-v1.md` as the only event dictionary for P3.

Primary metrics:

- onboarding completion rate;
- D1, D7, D30;
- weekly Today use days;
- Muyu start-to-complete rate;
- seven-day task completion rate;
- paywall-to-purchase conversion;
- monthly subscription second-month retention;
- yearly refund rate.

Do not upload birth date/time, precise birthplace, name, Oracle raw questions,
report text, or journals.

## US Localization

- English copy should explain the product without requiring the user to know
  Bazi, stems, branches, ten gods, or hexagrams.
- Traditional vocabulary defaults to Chinese Roots / methodology sections.
- Muyu Reset should stand alone as: one sound, one breath, one intention.
- Keep Chinese cultural origin visible, but avoid literal translation as the
  default user experience.
- Avoid destiny, fortune, miracle, guaranteed wealth, guaranteed relationship,
  diagnosis, or professional-advice language.

## TestFlight Plan

Target 50-100 US testers split across:

- users unfamiliar with Bazi;
- users interested in mindfulness or journaling;
- users already familiar with astrology / I Ching;
- users willing to evaluate paid subscriptions.

Required study questions:

- Does `Muyu Reset` communicate its purpose without reading Chinese Roots?
- Is `Mindful Tap` clear as a tap/breath ritual?
- Do users understand what Bazi contributes?
- Do users trust the result and understand uncertainty?
- Would users return daily?
- Would users pay for monthly continuing value?

## Release Gate

- No default fake chart.
- Forged Pro cookies cannot unlock paid endpoints.
- StoreKit purchase and restore pass in Sandbox.
- Refund, revocation, expiry, renewal, and restore update entitlement.
- Core calculation boundary tests pass.
- VoiceOver, Dynamic Type, landscape, and small-screen flows are tested.
- Paid features shown in the release build are real, not Coming Soon or
  placeholder content.
- App Privacy details, support, terms, privacy, refund, and deletion
  instructions match the production implementation.

## Coordination

- Window 00 / current task: total control, architecture, ownership,
  integration, release gate.
- Window 01: backend entitlement and Apple validation.
- Window 02: calculation reliability and rule-version testing.
- Window 03: Web architecture, navigation, i18n, accessibility, performance.
- Window 04: Today retention, Muyu Reset, seven-day quest, retention events.
- Window 05: iOS shell, StoreKit2, WebView bridge, haptics, notifications.
- Window 06: monetization, US copy, event dictionary, TestFlight research,
  App Store metadata.

## Apple References

- App privacy overview: https://developer.apple.com/help/app-store-connect/manage-app-privacy/overview-of-app-privacy
- TestFlight overview: https://developer.apple.com/help/app-store-connect/test-a-beta-version/overview-of-testing-with-testflight
- In-app purchase testing overview: https://developer.apple.com/help/app-store-connect/test-in-app-purchases/overview-of-testing-in-app-purchases
- StoreKit sandbox testing: https://developer.apple.com/documentation/storekit/testing-in-app-purchases-with-sandbox
