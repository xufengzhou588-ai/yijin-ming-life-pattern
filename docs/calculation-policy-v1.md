# Calculation Policy v1

This policy fixes the rules used by `bazi-calculation-rules-v1` and `trait-weights-v1`.

## Scope

- Calendar input: Gregorian only in v1.
- Calendar dependency: pinned `sxtwl` plus Python `zoneinfo` / host tzdata.
- Golden fixture set: `tests/fixtures/bazi_golden_v1.json`.
- Professional blind-review status: pending; see `docs/professional-blind-review-v1.md`.

## Pillar Policy

- Year pillar: solar-year boundary follows the exact `jie` boundary, especially Li Chun.
- Month pillar: month transition follows exact `jie` boundaries, not whole-day dates.
- Day pillar: v1 uses the civil midnight day boundary after timezone normalization.
- Zi hour: 23:00-00:59 is the Zi branch, but 23:00-23:59 does not move the day pillar to the next day in v1.
- Hour pillar: calculated from the normalized calculation datetime hour.
- True solar time: optional. When enabled, civil clock time is adjusted with longitude and equation-of-time approximation before hour-pillar calculation.

## Luck Cycle Policy

- Direction:
  - male + yang year stem: forward
  - male + yin year stem: reverse
  - female + yang year stem: reverse
  - female + yin year stem: forward
  - unknown gender: forward with uncertainty reason `gender_unknown_luck_direction_defaulted`
- Start age: days to the next or previous `jie` anchor divided by 3.
- This is a launch policy, not a claim that all traditional schools agree.

## Timezone Policy

- Inputs without an explicit offset are interpreted in the supplied IANA timezone.
- Historical timezone offsets from `zoneinfo` are preserved, including sub-minute offsets.
- Sub-minute historical offsets add uncertainty reason `historical_timezone_offset_has_subminute_component`.
- DST behavior follows the host tzdata used by Python `zoneinfo`; changes in tzdata require fixture regeneration and review.

## Confidence And Uncertainty

- `confidence` is a method-confidence indicator, not a psychological or statistical validity score.
- Unknown birth time lowers confidence and adds `birth_time_unknown_hour_pillar_placeholder`.
- Approximate birth time lowers confidence and adds `birth_time_approximate_hour_boundary_possible`.
- True solar time adds `true_solar_time_uses_approximate_equation_of_time`.
- Trait scores are uncalibrated structural indicators; they must not be described as clinically or psychologically validated scales.

## Versioning

- Calculation rule changes must update `CALCULATION_MODEL_VERSION`.
- Interpretation wording/model changes must update `INTERPRETATION_MODEL_VERSION`.
- Trait rule logic must update `TRAIT_MODEL_VERSION`.
- Trait weights must update `TRAIT_WEIGHT_VERSION`.
- Any change that alters pillars, confidence, uncertainty reasons, or trait context must explain which fixture categories changed.
