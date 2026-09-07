# P5-04 Anonymous Funnel and US TestFlight Experiment

Date: 2026-08-25
Branch: `p5-04-analytics-testflight`
Baseline: `3e81ad1 Prepare P3 US paid release`

## Scope

P5-04 adds a privacy-friendly anonymous funnel for first open, onboarding, free
use, paywall, purchase, restore, and Pro gate denial. It does not depend on
CloudKit, Widget, Relationship Reflection, or any P4/future work.

Implemented paths:

- Web: `web/js/analytics-v20260826.js` and trigger points in
  `web/js/app-v20260826.js`.
- iOS: `ios/MINGLifePattern/Services/AppAnalytics.swift`,
  `StoreKitManager.swift`, `ProSubscriptionView.swift`, and app startup.
- Server: `/api/analytics/events` in `server.py`.
- Contract: `docs/analytics-events-v1.md` with current schema
  `analytics-events-v2`.

## Anonymous Schema

Every accepted v2 event contains:

- `event_id`: random UUID for dedupe.
- `schema_version`: `analytics-events-v2`.
- `name`: allowed event name.
- `created_at`: client timestamp.
- `received_at`: server timestamp after upload.
- `anonymous_install_id`: random UUID stored locally per install/browser.
- `anonymous_session_id`: random UUID for the browser tab session or iOS app
  process.
- `sequence`: local monotonic counter.
- `release_channel`: `testflight`, `app_store`, `web`, `local`, or `unknown`.
- `region_scope`: `us_testflight`, `non_us_testflight`, `not_testflight`, or
  `unknown`.
- `experiment`: key, variant, and bucket.
- `metadata`: categorical allowlist only.

Forbidden fields include birth date/time, birthplace, timezone, country,
region, city, longitude, latitude, name, email, Oracle question, journal text,
generated report text, and raw payloads.

## Experiment

Experiment key: `us_testflight_paywall_copy`

Assignment:

- Stable hash of `anonymous_install_id` plus experiment key.
- `control`: bucket 0-49.
- `value_stack`: bucket 50-99.

Behavior:

- Web paywall `control`: standard plan-first order.
- Web paywall `value_stack`: included Pro value appears before plan cards.
- Native iOS records the same assignment and paywall exposure; StoreKit purchase
  events can be read by the same anonymous install ID.

Readout population:

- App Store Connect external testers assigned to the United States group.
- Analytics filter: `release_channel=testflight`,
  `region_scope=us_testflight`, and experiment key
  `us_testflight_paywall_copy`.
- Do not infer or store exact location. If in doubt, classify as
  `non_us_testflight` or `unknown` and exclude from the US readout.

## Funnel Events

Core P5 events:

- `first_open`
- `experiment_exposure`
- `onboarding_started`
- `onboarding_completed`
- `free_entitlement`
- `reading_generated`
- `paywall_view`
- `pro_gate_denied`
- `purchase_start`
- `purchase_success`
- `purchase_failure`
- `purchase_cancel`
- `restore`

Retained P3 events continue for Today, Muyu, weekly review, Oracle save, and
seal selection.

## Metrics

Primary:

- Activation: `onboarding_completed / first_open`.
- Free reading success: `reading_generated / free_entitlement`.
- Paywall reach: `paywall_view / reading_generated`.
- Purchase intent: `purchase_start / paywall_view`.
- Purchase completion: `purchase_success / purchase_start`.

Guardrail:

- Analytics upload failure rate by server accepted count versus queued count.
- Purchase failure by `failure_stage` and `error_code`.
- Restore success: `restore status=success / restore status=started`.
- Pro gate demand by `module`.
- No PII rows found in JSONL spot checks.

Experiment:

- Compare paywall reach, purchase intent, purchase success, cancel rate, and
  restore success between `control` and `value_stack`.
- Minimum practical readout: 50-100 US TestFlight testers, but treat results as
  directional unless each variant has enough paywall views for a stable signal.

## Privacy and Retention

- Web and iOS local queues keep the last 200 events.
- Upload is best effort and never awaited by user-facing flows.
- Upload batch size is 25.
- Server stores JSONL under `.analytics-events/` by default or
  `BAZI_ANALYTICS_DIR`.
- Default retention is 30 days; `BAZI_ANALYTICS_RETENTION_DAYS` supports 1-90.
- Disable server analytics with `BAZI_ANALYTICS_DISABLED=1`.
- Disable iOS analytics with `MING_ANALYTICS_DISABLED=1`.
- Web respects `window.MING_ANALYTICS_DISABLED`, local opt-out key
  `ming.analytics.disabled.v1`, and browser Do Not Track.
- The analytics endpoint does not write IP address or user agent into JSONL and
  suppresses normal IP-bearing access logs for that route.

## QA Steps

1. Fresh install or clear browser storage.
2. Launch app from TestFlight or with `release_channel=testflight` in local web
   preview.
3. Confirm `first_open`, `experiment_exposure`, `free_entitlement`, and
   `onboarding_started` are queued without birth fields.
4. Complete onboarding and generate a free reading.
5. Confirm `onboarding_completed` and `reading_generated` include only language,
   time accuracy, and true-solar-time boolean.
6. Tap a locked Pro module.
7. Confirm `pro_gate_denied` and `paywall_view` include module, surface, reason,
   and variant, but no birth data.
8. In StoreKit Sandbox, start monthly purchase and test success, user cancel,
   and backend validation failure.
9. Confirm `purchase_start`, `purchase_success`, `purchase_cancel`, and
   `purchase_failure` are queued and uploaded best effort.
10. Run Restore Purchase with a valid and invalid sandbox account.
11. Confirm `restore` start/success/failure status.
12. Force offline mode or point API base URL to an unavailable host.
13. Confirm onboarding, paywall, purchase UI, and restore UI remain usable while
    analytics events stay queued or fail silently.
14. Set `BAZI_ANALYTICS_DISABLED=1` and confirm endpoint returns `ok=true` with
    `accepted=0`.
15. Inspect JSONL rows and verify no forbidden keys or suspicious free text.

## Remaining External Dependencies

- StoreKit Sandbox testing on physical devices.
- TestFlight build uploaded through App Store Connect.
- US external tester cohort configuration in App Store Connect.
- Public production HTTPS domains for app, API, privacy, terms, support, and
  methodology.
- Production App Store Server API credentials and signed notification endpoint
  verification.
- App Store privacy questionnaire updated to match analytics enabled/disabled
  production configuration.
- VoiceOver, Dynamic Type, real 320 px device, and production-domain QA from
  the previous QA gap list.
