# Product Review v1

## Current Positioning

The product should present itself as a structured Bazi and I Ching interpretation tool, not as absolute fortune prediction.

Core product principle:

- Backend: deterministic, traceable, evidence-based.
- Frontend: simple, readable, non-threatening, action-oriented.
- AI layer: later, only explains existing structured conclusions.

## Display Strategy

Default user view:

- Overview first: career, wealth, relationships, and decision style.
- Each overview card should show human-readable confidence, such as well supported, moderately supported, or initial reference.
- Four Pillars second.
- Classic reference third.
- Professional data collapsed by default.

Avoid default exposure of:

- Raw JSON.
- Evidence IDs.
- Rule IDs.
- Dense ten-god tables without explanation.

## App Store Readiness Notes

For US App Store release:

- Use bilingual UI from the beginning.
- Avoid wording like guaranteed wealth, guaranteed divorce, fate is bad, or medical/financial certainty.
- Add clear language that interpretations are reflective and informational.
- Keep personal birth data processing transparent.
- Prepare privacy policy before external testing.

## Next Product Priorities

1. Replace the test city list with a complete China administrative location dataset.
2. Expand the new opt-in device-only chart history into authenticated encrypted
   sync only after account and privacy architecture are approved.
3. Keep professional data available, but never make it the default user experience.
4. Split i18n copy into locale files before the app grows larger.
5. Replace MVP interpretation heuristics with a calibrated trait engine.
6. Add export/share flow only after privacy and disclaimer copy are finalized.

## Open Reliability Register

- True solar time now applies longitude and equation-of-time correction before
  pillar calculation. Cross-check boundary cases against an independent
  professional calendar before release. The approximation follows NOAA's
  published solar-calculation equations:
  https://gml.noaa.gov/grad/solcalc/calcdetails.html
- Historical civil-time policy needs explicit product review. IANA timezone
  data applies China's historical daylight-saving offset where applicable;
  some traditional calculators assume UTC+8 for all mainland birth records.
  The release version must state and test the chosen policy.
- The current `sxtwl` year and month pillar path is day-based; exact
  within-day solar-term boundary behavior still needs a dedicated regression
  fixture set.
- Luck-cycle start age remains the transparent `nearest jie / 3` MVP rule and
  needs school-specific policy review.
- The city dataset still covers representative Chinese cities rather than all
  prefecture-level locations.
- Trait weights remain uncalibrated and must not be marketed as validated
  psychological measurement.
