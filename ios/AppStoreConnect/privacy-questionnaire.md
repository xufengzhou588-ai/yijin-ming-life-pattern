# App Privacy Questionnaire Draft

Status: draft for App Store Connect privacy labels. Final answers must match the production server and analytics configuration at upload time.

## Current Launch Assumption

The v1 app:

- does not include third-party advertising;
- does not use data for tracking across apps or websites;
- does not sell or share birth data;
- does not require account signup;
- does not include active In-App Purchase, external payment, or active
  subscriptions in the 1.0 free-first submission;
- sends reading inputs to the first-party backend only to calculate the requested reading;
- does not intentionally retain birth details or oracle questions server-side by default.

## Tracking

Answer: `No`

Reason: no third-party ad tracking, no cross-app tracking, and no data broker sharing.

## Data Linked to the User

Expected answer for the 1.0 free-first submission: no data linked to the user,
because there is no account signup and no active In-App Purchase.

Use the following only in the later paid update if the production backend stores
or links the entitlement to a user or device record:

- Purchases: app functionality
- Identifiers: app functionality

Do not mark these as tracking.

## Data Not Linked to the User

Expected categories if the hosted backend processes but does not retain reading inputs:

- Other Data / Product Interaction Data: app functionality
- User Content, if oracle questions or journal notes are sent to the server

Purpose:

- App Functionality

Do not mark as:

- Third-Party Advertising
- Developer's Advertising or Marketing
- Analytics, unless analytics is actually enabled
- Product Personalization, unless recommendations are stored/profiled beyond the requested reading

## Sensitive Data Notes

Birth date, birth time, birthplace, and optional gender/name are highly personal even when not formally classified as App Store “Sensitive Info.” Treat them conservatively:

- explain why they are requested;
- avoid sending them to analytics;
- avoid saving them unless the user chooses;
- provide a privacy policy statement that server processing is for generating the requested reading.

## Analytics

P5 updates the first-party anonymous event dictionary in
`docs/analytics-events-v1.md` to `analytics-events-v2`. The current
implementation stores a capped local queue and may upload sanitized events to
MING's first-party `/api/analytics/events` endpoint. Before upload, update the
labels if analytics remains enabled for production:

- anonymous install/session identifiers;
- product interaction events;
- crash logs;
- performance diagnostics;
- birth-input completion funnels.

Analytics must not include raw birth details, precise birthplace, country,
region, city, timezone, oracle questions, journal text, or generated reading
text. The current P5 implementation does not use a third-party analytics SDK.

Allowed P5 events are categorical only. For the 1.0 free-first submission this
means first open, experiment exposure, onboarding, free entitlement, reading
generation, Today view, seal selection, Muyu start/complete, seven-day task
completion, weekly review view, Oracle start/save, planned-Pro view, and Pro
gate denial. Purchase and restore events are reserved for the later StoreKit
update.

Do not include:

- birth date or birth time;
- country, region, city, timezone, longitude, latitude, or precise birthplace;
- name or nickname;
- raw Oracle question;
- report body, reading JSON, or journal text.

## Privacy Policy Copy Alignment

The privacy policy should say:

- what birth details are used for;
- whether readings are stored locally or server-side;
- how Pro entitlement is verified;
- that the 1.0 build has no active purchase or subscription;
- how users can contact support;
- that MING does not sell personal data;
- that MING does not use personal data for third-party advertising tracking.
