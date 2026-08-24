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
and plain-language interpretation.

MING Pro adds deeper reports, monthly guidance, annual rhythm analysis, and a
guided three-coin I Ching oracle with a private journal.

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
6. Privacy-first: save only when you opt in.

## Review Notes Draft

MING is an informational lifestyle app for cultural exploration and personal
reflection. It does not provide medical, legal, financial, mental-health, safety,
or emergency advice. It does not guarantee outcomes or make absolute predictions.

Pro access is sold through App Store auto-renewable subscriptions. Restore
Purchase is available on the Pro paywall.

If a reviewer needs Pro access, provide a sandbox account or review instructions
after StoreKit is connected.

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
- TestFlight QA: `ios/AppStoreConnect/testflight-qa-checklist-20260715.md`
- Xcode upload runbook: `ios/AppStoreConnect/xcode26-upload-runbook.md`
- Export options plist: `ios/AppStoreConnect/exportOptions-app-store-connect.plist`

## Remaining Before Submission

- Build/archive on Xcode 26+ with valid Apple signing.
- StoreKit products in App Store Connect.
- Backend App Store Server API validation behind `POST /api/app-store/transactions`.
- Public HTTPS legal/support URLs.
- Final App icon and screenshots.
- App privacy questionnaire.
- TestFlight build and QA.
