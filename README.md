# BaziCoreOutput v1 MVP

This repository contains the first deterministic layer for the Bazi expert system:

- `schemas/bazi-core-output-v1.schema.json`: canonical output contract.
- `schemas/bazi-trait-output-v1.schema.json`: modern trait and conflict-resolution contract.
- `bazi_core/`: minimal generator and validator.
- `samples/`: generated example charts that validate against the schema.
- `tests/`: schema validation tests.

Current MVP boundaries:

- Gregorian input only.
- No LLM, prompt, 用神, 格局, or 身强身弱裁决.
- If `birth_datetime` includes an offset, its wall-clock time is preserved for pillar calculation.
- True solar time applies longitude, birth-time UTC offset, and the NOAA-style
  equation-of-time approximation before pillar calculation. The correction is
  recorded as `input.time_basis` evidence.
- Luck cycles use a transparent MVP rule: 顺逆 + nearest 节气 days / 3.
- TraitOutput v1 exposes ten modern dimensions with score, level, confidence,
  positive factors, negative factors, and core evidence references.
- The web overview and Pro reports read TraitOutput from the backend; they do
  not calculate wealth retention or relationship pressure in the browser.
- The 1.0 App Store target is a free-first release. Pro reports remain gated and
  preview planned value only; no purchase or Restore Purchase path is active in
  the default build.
- The later StoreKit update keeps server-verified entitlement support. App
  Store signed transactions are validated by the backend, normalized into
  `status`, `tier`, `product_id`, `expires_at`, `needs_restore`, and
  `storekit_ready`, and stored in the server-side entitlement database. Browser
  cookies are only short-lived signed session pointers and cannot declare Pro by
  themselves.
- Draft legal/support pages exist under `web/legal/`; production App Store
  Connect will require public HTTPS Privacy Policy, Terms, and Support URLs.
- `ios/` contains the SwiftUI shell source skeleton for the App Store build:
  native navigation, WKWebView reading surface, free-first Pro preview,
  StoreKit2 subscription manager for the later paid update, entitlement store,
  and Trust links.
- Pro report copy is still bundled in the frontend. Production paid content
  must be returned by an authenticated backend report endpoint.
- AnnualOutlook v1 is generated through the protected Pro endpoint and keeps
  yearly career, wealth, relationship, and stability signals separate.
- MonthlyCompass v1 provides a six-month action arc with one focus, boundary,
  real-world experiment, reflection prompt, and collectible cultural mark per
  month.
- I Ching Oracle v1 uses the three-coin method: cryptographic randomness
  determines only the six coin totals, while King Wen hexagram mapping,
  moving-line inversion, interpretation structure, and evidence remain
  deterministic and reproducible.
- Oracle readings can be explicitly saved to a device-only journal. Repeated
  saved questions within 24 hours return the previous reading instead of
  encouraging repeated casting for a preferred answer.
- Unlocked reports can be exported as a local UTF-8 text file without upload.

Generate one chart:

```bash
python3 -m bazi_core.cli generate --birth 1990-05-17T08:30:00+08:00 --timezone Asia/Shanghai --gender male --country CN --region Shanghai --city Shanghai --longitude 121.4737 --latitude 31.2304
```

Validate a chart:

```bash
python3 -m bazi_core.cli validate samples/sample-shanghai-1990.json
```

Start the local test system:

```bash
bash tools/start_mac_local_server.sh
```

Then open:

```text
http://127.0.0.1:8787
```

Run tests:

```bash
bash tools/mac_verify.sh
```

Create a Mac handoff package:

```bash
bash tools/package_appstore_sprint.sh
```
