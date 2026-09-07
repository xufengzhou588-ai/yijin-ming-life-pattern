# App Store Submission Packet v1

## App Identity

- App name: `MING · Life Pattern`
- Subtitle: `Ancient Chinese patterns, modern self-reflection`
- Primary category: Lifestyle
- Secondary category: Health & Fitness or Reference, to be decided after final positioning
- Content boundary: cultural exploration, journaling, and personal reflection

## Short Description Draft

MING translates Chinese Four Pillars and I Ching-inspired structure into modern
personal reflection: patterns, boundaries, monthly guidance, and guided oracle
readings without fatalistic predictions.

## Long Description Draft

MING is a traceable Chinese life-pattern system designed for modern users. Enter
your birth details to generate a structured reading that explains how you tend
to move, connect, build, decide, and respond to change.

Free features include a core life-pattern overview, structured chart output,
plain-language interpretation, Today card, daily seals, Muyu Reset, a simple
Oracle preview, and on-device history.

MING Pro adds Monthly Compass, complete Oracle and Journal, personalized
seven-day quests, weekly and monthly review history, more rituals and
soundscapes, deeper reports, and annual rhythm analysis.

MING is for cultural exploration and personal reflection. It is not medical,
legal, financial, mental-health, safety, or emergency advice, and it does not
guarantee future outcomes.

## Keywords Draft

I Ching, BaZi, Four Pillars, Chinese astrology, self reflection, journaling,
life pattern, personal growth, oracle, monthly guidance

## Screenshot Flow

1. Build your life pattern: simple birth-time and birthplace input.
2. Free reading: core archetype and multidimensional profile.
3. Traceable reasoning: evidence-backed structure without fatalistic claims.
4. Pro reports: career, wealth, relationship, annual, monthly.
5. Guided oracle: three-coin reflection and private journal.
6. Today loop: daily seal, Muyu Reset, small action, seven-day trail.
7. Privacy-first: save only when you opt in.

## Review Notes Draft

Use `ios/AppStoreConnect/review-notes-free-first.md` for the 1.0 free-first
submission.

MING's first App Store release is free. It does not include active In-App
Purchase, external payment, active subscriptions, StoreKit purchase, or Restore
Purchase. Pro surfaces preview planned future functionality only.

MING is an informational lifestyle app for cultural exploration and personal
reflection. It does not provide medical, legal, financial, mental-health, safety,
or emergency advice. It does not guarantee outcomes or make absolute predictions.

## Required URLs

Local draft pages currently exist for development:

- Privacy Policy: `/legal/privacy.html`
- Terms of Use: `/legal/terms.html`
- Support: `/legal/support.html`

Production App Store Connect will require public HTTPS URLs.

Prepared production URL targets:

- Marketing URL: `https://mingpattern.app/app`
- Privacy Policy: `https://mingpattern.app/legal/privacy`
- Terms of Use: `https://mingpattern.app/legal/terms`
- Support: `https://mingpattern.app/support`

## Prepared App Store Connect Files

- App metadata: `ios/AppStoreConnect/app-metadata-en-US.md`
- Privacy questionnaire draft: `ios/AppStoreConnect/privacy-questionnaire.md`
- Age-rating questionnaire draft: `ios/AppStoreConnect/age-rating-questionnaire.md`
- Subscription setup: `ios/AppStoreConnect/subscription-products.md`
- Review notes: `ios/AppStoreConnect/review-notes.md`
- Screenshot plan: `ios/AppStoreConnect/screenshot-plan.md`
- TestFlight QA: `ios/AppStoreConnect/testflight-qa-checklist-20260825.md`
- Xcode upload runbook: `ios/AppStoreConnect/xcode26-upload-runbook.md`
- Export options plist: `ios/AppStoreConnect/exportOptions-app-store-connect.plist`
- P3 paid release plan: `docs/p3-us-paid-release-2026-08-25.md`
- Analytics event dictionary: `docs/analytics-events-v1.md`
- P3 verification baseline: `docs/p3-verification-baseline-2026-08-25.md`
- US free App Store launch checklist:
  `docs/us-free-app-store-launch-2026-09-07.md`
- App Store preflight checkpoint:
  `docs/app-store-preflight-2026-08-26.md`
- P5-01 production persistence:
  `docs/p5-production-persistence-2026-08-25.md`
- P5-02 StoreKit Sandbox and submission checklist:
  `docs/p5-02-storekit-sandbox-app-store-submission-2026-08-25.md`
- P5-03 navigation, Paywall, and accessibility:
  `docs/p5-nav-paywall-a11y-2026-08-25.md`
- P5-04 anonymous funnel and TestFlight experiment:
  `docs/p5-anonymous-funnel-testflight-2026-08-25.md`

## Remaining Before Submission

- Build/archive on Xcode 26+ with valid Apple signing.
- Public HTTPS legal/support URLs.
- Final App icon and screenshots.
- App privacy questionnaire aligned to actual analytics/upload behavior.
- App Store Connect app record, price set to Free, and first availability set
  to United States.
- TestFlight smoke on a real iPhone.

Deferred to the paid v1.1 submission:

- StoreKit products in App Store Connect.
- Backend App Store Server API credentials and Apple root certificates deployed
  for `POST /api/app-store/transactions` and
  `POST /api/app-store/notifications`.
- StoreKit Sandbox purchase, restore, expiry, refund, and revocation QA.
- 50-100 US TestFlight paid-study testers and P3 study notes.
