# Analytics Events v2

Date: 2026-08-25

This file keeps the historical `analytics-events-v1.md` path because App Store
and QA documents already link to it. The current implementation emits
`analytics-events-v2`.

## Policy

Analytics are anonymous product-interaction events for onboarding, free use,
paywall, purchase, restore, and Pro gate validation. They are first-party only:
web and iOS keep a capped local queue and may upload to `/api/analytics/events`.
There is no third-party SDK and no CloudKit dependency.

Do not send:

- birth date or birth time;
- timezone, longitude, latitude, country, region, city, or precise birthplace;
- name, nickname, email, account identity, or App Store account information;
- raw Oracle questions;
- generated report text, reading payloads, or journal content;
- screenshots, free-form notes, pasted user text, or support message content.

The server does not store IP address or user agent in analytics JSONL rows. The
analytics route suppresses the normal IP-bearing access-log format.

## Identifiers

- `anonymous_install_id`: random UUID generated on device/browser install and
  stored locally. It is not derived from birth data, Apple ID, device ID, email,
  or account data.
- `anonymous_session_id`: random UUID for the current browser tab session or
  iOS app process.
- `event_id`: random UUID used for dedupe.
- `sequence`: local monotonic counter for ordering within one install.

These identifiers are used only to count anonymous funnels and keep experiment
assignment stable. They are not used for advertising.

## Experiment

Experiment key: `us_testflight_paywall_copy`

- Assignment: deterministic hash of `anonymous_install_id` and experiment key.
- Buckets: `control` for 0-49, `value_stack` for 50-99.
- Exposure event: `experiment_exposure`.
- Web paywall effect: `value_stack` shows included Pro value before plan cards;
  `control` keeps the standard plan-first order.

## US TestFlight Scope

Metrics for the US TestFlight experiment must filter to:

- `release_channel = testflight`
- `region_scope = us_testflight`
- `experiment.key = us_testflight_paywall_copy`

`region_scope` is intentionally coarse. iOS uses TestFlight/sandbox receipt or
`MING_RELEASE_CHANNEL=testflight`, plus device locale region `US`. Web previews
use `release_channel=testflight` or `testflight=1`, plus coarse locale/timezone
hints. App Store Connect external tester country remains the source of truth;
analytics stores only the coarse scope, never country, city, timezone, or GPS.

## Retention and Disable Controls

- Web local queue: last 200 events.
- iOS local queue: last 200 events.
- Upload batch: up to 25 events.
- Server storage: JSONL files under `.analytics-events/` or
  `BAZI_ANALYTICS_DIR`.
- Server retention: 30 days by default, configurable with
  `BAZI_ANALYTICS_RETENTION_DAYS` from 1 to 90.
- Server disable: `BAZI_ANALYTICS_DISABLED=1`.
- iOS disable: `MING_ANALYTICS_DISABLED=1`.
- Web disable: `window.MING_ANALYTICS_DISABLED = true`, local storage key
  `ming.analytics.disabled.v1 = 1`, or browser Do Not Track.

Analytics upload failure, offline mode, disabled mode, or invalid events must
not block onboarding, reading generation, paywall display, purchase, restore, or
Pro gate checks.

## Allowed Metadata

Allowed metadata is intentionally categorical:

- `language`
- `surface`
- `module`
- `seal_key`
- `duration_seconds`
- `action_key`
- `status`
- `plan_id`
- `product_id`
- `entitlement_status`
- `entitlement_tier`
- `source`
- `time_accuracy`
- `true_solar_time`
- `quest_id`
- `week_index`
- `review_period`
- `app_build`
- `experiment_key`
- `variant`
- `placement`
- `reason`
- `failure_stage`
- `error_code`
- `cancel_reason`
- `storekit_environment`

## Event Dictionary

| Event | Trigger | Required metadata | Optional metadata |
| --- | --- | --- | --- |
| `first_open` | First app/browser open for an anonymous install | `surface` | `language`, `app_build` |
| `experiment_exposure` | Experiment assignment becomes observable | `experiment_key`, `variant`, `surface` | `app_build` |
| `onboarding_started` | First launch with no saved profile | `language` |  |
| `onboarding_completed` | First successful generated reading after setup | `language`, `time_accuracy` | `true_solar_time` |
| `free_entitlement` | App confirms anonymous user has free access | `entitlement_status`, `entitlement_tier`, `source` |  |
| `reading_generated` | Backend reading generation succeeds | `language`, `time_accuracy` | `true_solar_time` |
| `today_viewed` | Today is rendered after a valid reading | `language`, `surface` | `module` |
| `seal_selected` | User selects Focus, Spark, Ground, Connect, or Restore | `language`, `seal_key` | `module` |
| `muyu_started` | Muyu Reset starts | `language`, `duration_seconds` | `seal_key` |
| `muyu_completed` | Muyu Reset timer completes | `language`, `duration_seconds` | `seal_key` |
| `quest_action_completed` | Evening mark is `completed` | `language`, `action_key` | `seal_key` |
| `weekly_review_viewed` | Seven-day trail is shown with existing records | `language`, `review_period` |  |
| `oracle_started` | First Oracle line is cast | `language` | `module` |
| `oracle_saved` | User saves an Oracle reading to local journal | `language` | `module` |
| `paywall_view` | Contextual or native Pro paywall is shown | `surface` | `language`, `module`, `variant` |
| `pro_gate_denied` | Free user attempts Pro-only module or receives Pro 403 | `reason`, `surface` | `language`, `module` |
| `purchase_start` | StoreKit purchase begins | `product_id`, `source` | `plan_id` |
| `purchase_success` | StoreKit purchase sync returns active entitlement | `product_id`, `entitlement_status`, `source` | `plan_id` |
| `purchase_failure` | StoreKit purchase or backend sync fails | `product_id`, `failure_stage`, `error_code`, `source` | `plan_id` |
| `purchase_cancel` | User cancels StoreKit purchase | `product_id`, `cancel_reason`, `source` | `plan_id` |
| `restore` | StoreKit restore starts or finishes | `source`, `status` | `entitlement_status`, `error_code` |

The server currently also accepts v1 purchase aliases for backward
compatibility with queued local events, but new code should emit the v2 names
above.

## Core Metrics

- First-open to onboarding completion:
  `onboarding_completed / first_open`.
- Free activation:
  anonymous installs with `free_entitlement` and `reading_generated`.
- Paywall reach:
  anonymous installs with `paywall_view / reading_generated`.
- Pro gate demand:
  `pro_gate_denied / reading_generated`, grouped by `module`.
- Purchase intent:
  `purchase_start / paywall_view`.
- Purchase completion:
  `purchase_success / purchase_start`.
- Purchase cancellation:
  `purchase_cancel / purchase_start`.
- Purchase failure:
  `purchase_failure / purchase_start`, grouped by `failure_stage`.
- Restore health:
  `restore status=success / restore status=started`.
- Experiment readout:
  compare the above metrics between `control` and `value_stack` for
  `region_scope=us_testflight`.

Monthly renewal, refund, revocation, and churn must come from App Store Server
Notifications or App Store subscription reports, not frontend events alone.

## Implementation Notes

- Web events are sanitized in `web/js/analytics-v20260826.js`.
- iOS events are sanitized in `ios/MINGLifePattern/Services/AppAnalytics.swift`.
- Server events are sanitized again in `server.py` before JSONL append.
- Unknown events, unknown metadata keys, forbidden keys, invalid UUIDs, and
  suspicious free-text values are dropped.
- Any future analytics vendor, account sync, or CloudKit work requires a
  separate privacy review and App Store privacy-label update.
