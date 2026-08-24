# Test Baseline 2026-08-24

Baseline tag: `prototype-audit-2026-08`

## Commands

```bash
.venv/bin/python -m unittest -v tests.test_generate_validate
xcodebuild -project MINGLifePattern.xcodeproj -scheme MINGLifePattern -configuration Debug -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 16' build
```

## Result

- Python: 12 tests passed.
- iOS Simulator: Debug build passed on iPhone 16, iOS 18.1 simulator.

## Runtime Versions

- API service: `BaziCoreHTTP/0.1`
- System version: `2026.08.21`
- Calculation data: `2026.08`
- Location data: `world-locations-v1`
- Rule model: `bazi-core-v1`
- Trait model: `trait-v1`
- Annual model: `annual-trait-rules-v1`
- Monthly model: `monthly-compass-v1`
- Oracle model: `three-coin-change-rules-v1`
- Content copy: `en-US-zh-CN-2026.08`

## Schema Versions

- `bazi-core-output-v1`: `1.0.0`
- `bazi-trait-output-v1`: `1.0.0`
- `bazi-annual-outlook-v1`: `1.0.0`
- `bazi-monthly-compass-v1`: `1.0.0`
- `i-ching-oracle-v1`: `1.0.0`

## Notes

- The Xcode bundled Python initially failed before dependency installation because AppleDouble `._*.pth` files inside the generated `.venv` were parsed as site files. Removing ignored `._*` files from the venv allowed dependency installation and the tests passed.
