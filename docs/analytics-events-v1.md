# Analytics Events v1

Date: 2026-08-25

## Policy

Analytics are anonymous product-interaction events. The current implementation
stores a capped local queue only; the same contract must be used before any
server upload or third-party SDK is added.

Do not send:

- birth date or birth time;
- timezone, longitude, latitude, country, region, city, or precise birthplace;
- name, nickname, email, or account identity;
- raw Oracle questions;
- generated report text, reading payloads, or journal content;
- screenshots, free-form notes, or pasted user text.

Allowed metadata is intentionally small and categorical:

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
- `source`
- `time_accuracy`
- `true_solar_time`
- `quest_id`
- `week_index`
- `review_period`

## Event Dictionary

| Event | Trigger | Required metadata | Optional metadata |
| --- | --- | --- | --- |
| `onboarding_started` | First launch with no saved profile | `language` |  |
| `onboarding_completed` | First successful generated reading after setup | `language`, `time_accuracy` | `true_solar_time` |
| `reading_generated` | Backend reading generation succeeds | `language`, `time_accuracy` | `true_solar_time` |
| `today_viewed` | Today is rendered after a valid reading | `language`, `surface` | `module` |
| `seal_selected` | User selects Focus, Spark, Ground, Connect, or Restore | `language`, `seal_key` | `module` |
| `muyu_started` | Muyu Reset starts | `language`, `duration_seconds` | `seal_key` |
| `muyu_completed` | Muyu Reset timer completes | `language`, `duration_seconds` | `seal_key` |
| `quest_action_completed` | Evening mark is `completed` | `language`, `action_key` | `seal_key` |
| `weekly_review_viewed` | Seven-day trail is shown with existing records | `language`, `review_period` |  |
| `oracle_started` | First Oracle line is cast | `language` | `module` |
| `oracle_saved` | User saves an Oracle reading to local journal | `language` | `module` |
| `paywall_viewed` | Contextual Pro paywall is shown | `language`, `module` | `surface` |
| `purchase_started` | StoreKit purchase begins | `product_id`, `source` | `plan_id` |
| `purchase_completed` | StoreKit purchase sync returns entitlement | `product_id`, `entitlement_status`, `source` | `plan_id` |
| `subscription_restored` | StoreKit restore finishes | `entitlement_status`, `source` | `product_id` |

## Core Metrics

- Onboarding completion rate: `onboarding_completed / onboarding_started`.
- D1, D7, D30: distinct anonymous installs with `today_viewed` after first
  `reading_generated`; do not derive this from birth inputs.
- Weekly Today use days: unique local dates with `today_viewed`.
- Muyu completion rate: `muyu_completed / muyu_started`.
- Seven-day task completion rate: `quest_action_completed / today_viewed`.
- Paywall conversion: `purchase_completed / paywall_viewed`.
- Monthly subscription second-month retention: StoreKit renewal entitlement
  state, not frontend events.
- Yearly refund rate: App Store Server Notifications / subscription reports,
  not frontend events.

## Implementation Notes

- Web events are sanitized in `web/js/analytics-*.js`; unknown events and
  unapproved metadata keys are dropped.
- iOS StoreKit events are stored locally through `AppAnalytics`.
- Any future upload pipeline must reuse this event dictionary and pass a
  privacy review before release.
