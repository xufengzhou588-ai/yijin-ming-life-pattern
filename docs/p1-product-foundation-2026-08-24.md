# P1 Product Foundation 2026-08-24

## Reliability Test System

- Golden fixture set: `tests/fixtures/bazi_golden_v1.json`
- Fixture count: 104
- Covered categories:
  - solar-term minute boundary
  - Zi hour day-boundary policy
  - US DST
  - China historical timezone offsets
  - true solar time crossing hour branches
  - unknown / approximate birth time
  - leap day and cross-year cases
- Regression tests:
  - `tests/test_bazi_golden_fixtures.py`
  - `tests/test_generate_validate.py`
- Policy document: `docs/calculation-policy-v1.md`
- Blind review record: `docs/professional-blind-review-v1.md`

External blind review is not complete. P1 reliability should not be described as externally accepted until two professional reviewer records are added.

## Web Split

`web/index.html` now owns page structure only and loads versioned static resources:

- `web/styles/tokens-v20260824.css`
- `web/styles/base-v20260824.css`
- `web/styles/components-v20260824.css`
- `web/styles/responsive-v20260824.css`
- `web/js/state-v20260824.js`
- `web/js/storage-v20260824.js`
- `web/js/api-v20260824.js`
- `web/js/analytics-v20260824.js`
- `web/js/locales-v20260824.js`
- `web/js/app-v20260824.js`
- `web/locales/zh-CN.json`
- `web/locales/en-US.json`

The locale JSON files currently contain the serializable static copy. Runtime template functions remain in `locales-v20260824.js` and should be migrated to parameterized JSON templates in a later cleanup.

## Navigation

The mobile primary navigation uses four entries:

1. Today
2. Blueprint
3. Oracle
4. Me

Pro is not a permanent primary tab. Pro report cards and subscription/paywall surfaces live inside contextual sections, primarily under Me or inside locked Pro actions.

## Accessibility And Performance

- Main status uses `role="status"` and `aria-live="polite"`.
- Oracle error/status messaging uses `role="alert"` and assertive live updates.
- Calculation ritual has dialog semantics, Escape close, and focus return.
- Reduced motion disables the calculation ritual and shortens decorative animations.
- Main form controls and buttons have a minimum 44px target height.
- Oracle audio uses `preload="none"`.
- Oracle large background image is gated behind `body[data-oracle-assets="ready"]`.
- Versioned JS/CSS assets use `Cache-Control: public, max-age=31536000, immutable`.

## Verification

- Python unit tests: 29 passed.
- JS syntax checks: passed for all `web/js/*-v20260824.js` files.
- HTTP smoke:
  - `/app`: 200, no-store
  - `/js/app-v20260824.js`: 200, long-cache immutable
  - `/styles/components-v20260824.css`: 200, long-cache immutable
- Visual screenshot QA: not completed locally. Firecrawl could not access `127.0.0.1`, and local Playwright/Chromium were unavailable.
