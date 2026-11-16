# App Review Response - Guidelines 4.3 and 4.2.6

Date: 2026-11-16

Submission ID: `6af8bac2-12ce-4e4e-8a72-29c547f948b3`

This response is intended for the App Review message thread. It answers the
nine questions from the reviewer directly and does not rely on App Store
marketing copy.

## Response To App Review

Thank you for the detailed questions. MING Life Pattern is an original,
standalone product developed and published by our own team. It was not created
from a commercial app template or app-generation service, and it is not a
reskinned version of another app. The details below describe the product and
its implementation.

### 1. What the app does and the problem it solves

MING helps a user turn Chinese Four Pillars (BaZi) structures into a traceable
personal-reflection workflow. The user enters birth date, time, and place. The
app calculates the chart deterministically, including timezone, solar-term,
longitude, and true-solar-time evidence. It then separates the result into
behavior dimensions instead of presenting one fixed fortune verdict.

The result is used in three practical workflows:

- a Blueprint that shows the calculated pillars, plain-language dimensions,
  confidence, and supporting evidence;
- a Today loop that turns the chart and current date into one focus, one small
  action, a 30- or 60-second mindful Muyu reset, and an evening reflection;
- an I Ching-inspired reflection flow whose coin outcomes are random but whose
  line mapping and interpretation structure are deterministic and reviewable.

The primary problem is that traditional chart tools are usually either dense
calculators that assume specialist knowledge or untraceable fortune feeds.
MING makes the calculation understandable, shows why a statement appears, and
turns it into a small reflection or experiment without promising an outcome.

### 2. Intended user

The intended user is an English-speaking adult interested in Chinese cultural
systems and structured self-reflection but who does not already understand
specialist BaZi terminology. This includes Chinese-diaspora users who want a
modern English interpretation and culturally curious users who want to inspect
the method rather than receive an unexplained prediction.

The app is not intended for professional fortune tellers, medical or mental
health use, financial decisions, minors, or users seeking guaranteed future
outcomes. Traditional terms are secondary to plain-language behavior and
reflection prompts.

### 3. Market need or gap

MING's gap is traceability plus an ongoing reflection loop. The product does
not stop at displaying a chart or generating generic horoscope text.

- Chart generation is deterministic and versioned. The calculation records
  timezone and true-solar-time adjustments and is covered by 104 golden
  fixtures, including solar-term minute boundaries, Zi-hour policy, US DST,
  historical China offsets, leap day, and approximate birth time.
- Ten behavior dimensions keep supporting and conflicting signals separate.
  Each dimension carries confidence, positive and negative factors, and
  references to the calculated evidence.
- The Today experience combines long-term chart structure, the current date
  pillar, and recent local activity. It produces a focus and a small action,
  followed by a non-competitive mindful reset and evening mark. There are no
  luck points, leaderboards, auto-tapping, or punishment for a missed day.
- Saved Oracle questions are device-only. Repeating the same saved question
  within 24 hours returns the earlier result instead of encouraging repeated
  casting until the user receives a preferred answer.

These rules, calculation models, product flows, English interpretation, and
visual assets were created specifically for MING. They are not supplied by an
app builder or content marketplace.

### 4. Beta testing and feedback applied

Before the first submission, testing consisted of private pre-release product
evaluation, automated regression and security testing, simulator builds, HTTP
production checks, and responsive-layout checks. We did not run a large public
beta cohort before the first submission, and we do not want to overstate the
size of the test group.

Examples of feedback applied during pre-release testing:

- Pre-release evaluation found it confusing to see a sample chart before entering personal
  information. The sample result was removed from first launch, and onboarding
  now explains what birth data is needed before generation.
- Exact birth time is not known by every user. We added unknown and approximate
  time handling and lower-confidence treatment where the hour pillar matters.
- Literal traditional terminology was difficult for English readers. The
  default presentation was rewritten in plain behavioral language, with
  traditional terminology moved into an optional Chinese Roots layer.
- A one-time reading did not provide a reason to return. We added the Today
  loop, five action seals, mindful reset, one-small-action step, evening mark,
  seven-day trail, pause, and non-punitive repair behavior.
- Pre-release reviewers wanted to understand why a conclusion appeared. We added visible
  confidence and evidence summaries rather than presenting a black-box result.

We will continue TestFlight testing, especially VoiceOver, Dynamic Type,
small-screen layout, and cold-start behavior, before any later paid update.

### 5. Standalone product or suite

MING is a standalone product. It is not part of a reskinned suite.

The only other consumer app under this developer account is Couple Flight
Chess. That app is a multiplayer/couple party board game. It uses a
React/TypeScript/Capacitor game codebase with dice, board movement, partner
rooms, task cards, character voices, and game artwork. MING uses a separate
SwiftUI application, a controlled first-party reading surface, a Python
calculation service, original BaZi/I Ching rule models, and different assets.
The products have different audiences, categories, data models, navigation,
content, and user goals.

### 6. Why it is not a feature of another app on the account

MING cannot reasonably be delivered as an in-app purchase or content addition
inside Couple Flight Chess. Couple Flight Chess is a relationship party game
whose core session is a shared board match. MING is a private personal
reflection tool based on birth inputs, deterministic calculation evidence,
daily records, and an optional device-only journal. Combining them would be
confusing for both audiences, would mix unrelated personal data with game
state, and would not preserve either product's purpose.

### 7. Code, frameworks, or assets shared with another app on the account

MING does not share significant product code, content, or assets with Couple
Flight Chess. The repositories and build systems are independent:

- MING: SwiftUI, WKWebView limited to first-party MING content, vanilla
  JavaScript/CSS, Python, JSON Schema, and a deterministic calculation engine.
- Couple Flight Chess: React, TypeScript, Vite, Capacitor, game-state hooks,
  board-game components, multiplayer room logic, and separate image/audio
  assets.

Normal platform concepts such as an iOS project, HTTPS networking, App Store
signing, and accessibility APIs are the only general similarities.

### 8. Shared codebase, SDK, or content library with third-party apps

The app does not share a product codebase, proprietary SDK, branded content
library, or template with any third-party app. It is not generated by a
white-label service and is not sold as a reusable app template.

It uses standard third-party/open-source technical libraries only:

- `sxtwl` for calendar and stem-branch calculations;
- `jsonschema` for validating versioned output contracts;
- Apple's App Store Server Library and `cryptography` for later StoreKit server
  verification support.

MING adds its own calculation policy, true-solar-time evidence, trait engine,
annual/monthly/oracle rule models, schemas, test fixtures, interpretation
content, daily loop, journaling rules, UI, illustrations, audio, and privacy
boundaries around those libraries.

### 9. Client, partner, or third-party ownership

No. MING was not created for a client, partner, or third party. The app's
concept, product scope, written content, branding, rule models, visual assets,
and source code are owned and maintained by the developer submitting the app.
No outside content provider asked us to submit an app on its behalf.

For additional implementation evidence, the project history is available in
the developer-owned source repository:

`https://github.com/xufengzhou588-ai/yijin-ming-life-pattern`

We respectfully request reconsideration under guidelines 4.3(a), 4.3(b), and
4.2.6. We are happy to provide a screen recording, calculation example, source
history, or more detail about any component if needed.

## Submission Rule

Do not submit a replacement binary while this clarification is pending. The
reviewer's instruction explicitly says to reply instead of resubmitting when
the app already meets the guidelines. If App Review requests a changed binary,
prepare Build 3 and describe the exact reviewer-requested changes in the next
submission notes.
