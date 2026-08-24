# Data Sources and Update Policy — 2026-08-21

## Decision

MING uses a hybrid update model:

- automatic generation for daily, monthly, and annual user-facing prompts;
- manual review for rule tables, calendar dependency upgrades, location data releases, paid report copy, App Store metadata, privacy policy, terms, and support copy.

This keeps the product fresh without making the underlying calculation engine unstable.

## Current System Versions

| Area | Version |
| --- | --- |
| System policy | `2026.08.21` |
| Calculation data | `2026.08` |
| Location data | `world-locations-v1` |
| Rule model | `bazi-core-v1` |
| Trait model | `trait-v1` |
| Annual model | `annual-trait-rules-v1` |
| Monthly model | `monthly-compass-v1` |
| Oracle model | `three-coin-change-rules-v1` |
| Content copy | `en-US-zh-CN-2026.08` |

The machine-readable status endpoint is:

```text
/api/system/status
```

The user-facing methodology page is:

```text
/legal/methodology
```

## Automatic Generation

These outputs are generated automatically from the user's input, chart structure, and current date rhythm:

- daily card;
- daily seal;
- monthly compass;
- annual rhythm.

They are not external rankings, live data feeds, or guaranteed predictions.

## Manual Review Required

These areas must not update silently:

- heavenly stems, earthly branches, five elements, ten-god relationships, and hidden stems;
- calendar dependency or solar-term calculation changes;
- city, timezone, longitude, and latitude dataset releases;
- paid report copy;
- English/Chinese localization;
- App Store metadata;
- privacy policy, terms, and support copy.

## Release Rule

If a change can alter the same user's reading result, it requires:

1. a version bump;
2. regression tests;
3. a changelog entry;
4. manual approval before production release.

If a change only updates daily/monthly/annual derived prompts without changing the underlying chart or trait model, it can be generated automatically under the current model version.

## App Store Positioning

Do not market data updates as stronger prediction. The paid value should be framed as:

- deeper reasoning;
- traceable evidence;
- monthly and annual continuity;
- private reflection history;
- better localization and usability.

Avoid claims that imply real-time fate data, guaranteed wealth, guaranteed relationship outcomes, or professional advice.
