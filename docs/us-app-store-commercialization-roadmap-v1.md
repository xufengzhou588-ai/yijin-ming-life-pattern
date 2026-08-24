# US App Store Commercialization Roadmap v1

## Goal

Ship `MING · Life Pattern` as a commercially viable US App Store product:
clear to Western users, culturally distinctive, privacy-conscious, and safe
for paid personal-reflection use.

This roadmap is ordered by release risk, not by visual excitement. Each stage
should leave the product more reviewable, testable, and monetizable.

## Stage 1 - Trust and Launch Foundation

Purpose: make the current web prototype ready for external testing and future
App Store review.

Deliverables:

- Product boundary copy in both English and Chinese:
  - cultural exploration and personal reflection;
  - not medical, legal, financial, mental-health, or safety advice;
  - no guaranteed prediction language;
  - birth details and saved charts explained clearly.
- Pro entitlement model documented:
  - free reading;
  - paid deep reports;
  - paid oracle reflection;
  - paid monthly/annual guidance.
- Product analytics kept lightweight and non-sensitive during testing.
- Privacy policy draft and data inventory prepared before TestFlight.

Acceptance:

- A user can explain what the app does without saying "it predicts my fate."
- A reviewer can see why the app is informational and reflective.
- No screen implies guaranteed wealth, marriage, disaster, diagnosis, or
  investment outcome.

## Stage 2 - Paid MVP Packaging

Purpose: make Pro feel worth paying for before real StoreKit is connected.

Deliverables:

- One coherent paywall explaining the value difference between free and Pro.
- Pro modules:
  - complete life-pattern report;
  - career, wealth, and relationship deep reports;
  - annual rhythm report;
  - monthly compass;
  - guided I Ching oracle and private journal.
- Export and saved history remain device-first until account architecture is
  approved.

Acceptance:

- Free mode gives enough recognition to create trust.
- Pro preview makes the missing value specific.
- Paid language is concrete: "deeper reasoning, practical boundaries,
  action plan, and traceable basis" rather than "unlock secrets."

## Stage 3 - iOS App Shell and StoreKit

Purpose: move from web demo to App Store-ready iOS product.

Deliverables:

- iOS app shell with mobile-native navigation.
- StoreKit products:
  - monthly subscription;
  - yearly subscription;
  - optional one-time report purchase if needed.
- Server-side receipt validation or App Store Server API integration.
- Anonymous local identity at minimum; Apple sign-in only if cloud sync is
  introduced.
- Entitlements enforced by backend, not only frontend state.

Acceptance:

- Pro access survives app restart.
- Subscription restore works.
- The app does not sell external digital content outside Apple IAP.
- Paywall, restore, terms, and privacy links are visible before purchase.

## Stage 4 - US Localization and Cultural Translation

Purpose: make Chinese metaphysics understandable without flattening it into a
generic horoscope app.

Deliverables:

- English-first copy reviewed for cultural translation, not literal
  translation.
- Traditional terms moved into optional "Chinese Roots" sections.
- Humor used only to soften terminology, never to mock the user or their
  reading.
- App Store screenshots explain:
  - traceable calculation;
  - modern strategy language;
  - Pro reports;
  - oracle reflection;
  - privacy and non-fatalistic stance.

Acceptance:

- A US user can understand the free result without knowing Bazi, stems,
  branches, ten gods, or hexagrams.
- The product feels mystical, but the advice feels usable.
- The copy does not look like a machine-translated Chinese app.

## Stage 5 - Reliability and Calibration

Purpose: protect long-term credibility.

Deliverables:

- Regression fixtures for solar-term boundary cases.
- Timezone and civil-time policy documented.
- Location dataset expanded and tested.
- Trait engine weights reviewed against expert cases.
- Evidence trace retained for every important modern conclusion.

Acceptance:

- Core chart output is reproducible.
- Important claims can point to evidence.
- The app can explain uncertainty when input time is approximate.

## Stage 6 - TestFlight and Launch

Purpose: validate market demand before public release.

Deliverables:

- 20-50 US beta testers.
- App Privacy details filled from the data inventory.
- Terms, privacy policy, support URL, and account deletion path if accounts
  exist.
- TestFlight survey focused on:
  - clarity;
  - perceived personalization;
  - willingness to pay;
  - confusion points;
  - trust concerns.

Acceptance:

- Test users understand the product promise.
- Pro conversion intent is measurable.
- Review-risk wording is removed before App Review submission.

## Current Next Step

Complete Stage 3: turn the scaffold into a buildable Xcode/TestFlight app.

1. Create the Xcode project and import `ios/MINGLifePattern/`.
2. Create StoreKit products in App Store Connect or local StoreKit config.
3. Implement real App Store Server API validation.
4. Replace placeholder HTTPS URLs with production legal/support/API URLs.
5. Build TestFlight candidate and run sandbox purchase/restore tests.
