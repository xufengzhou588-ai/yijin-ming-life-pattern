# Free First Test Run — 2026-07-27

## Backup

Before the free-first release changes, the current project state was backed up to:

```text
backups/before-free-first-release-20260727-185258.tar.gz
```

## Release Mode

Default release mode is now:

```text
free_first
```

Configured in:

- `ios/MINGLifePattern/Resources/Info.plist`
- `ios/MINGLifePattern/Support/AppEnvironment.swift`
- `MINGLifePattern.xcodeproj/xcshareddata/xcschemes/MINGLifePattern.xcscheme`
- `web/index.html`

## What Free First Means

In the free-first build:

- Free reading remains available.
- Pro value preview remains visible.
- Pro cards open a Coming Soon panel.
- No real purchase button is shown.
- No Restore Purchase button is shown in the web free-first flow.
- No demo unlock button is shown by default.
- Native StoreKit loading is skipped.
- Pro subscriptions are planned for a later update.

## Local Test URL

Start:

```bash
cd "/Volumes/Data/AI 系统/Yijin"
bash tools/start_free_first_local_server.sh
```

Open:

```text
http://127.0.0.1:8787/app?v=101
```

## Validation Completed

Ran:

```bash
bash tools/mac_verify.sh
```

Result:

- Python tests: `12 passed`
- HTTP smoke test: passed
- Demo unlock disabled by default: passed
- Xcode simulator generic build: passed

Also checked:

- `Info.plist`: valid
- inline JavaScript: syntax check passed

## Paid Test Mode for Later

Do not use this for v1.0 App Store submission.

For future paid testing:

```text
http://127.0.0.1:8787/app?release=paid_test
```

For iOS paid update:

```text
MING_PRO_MODE=storekit
```

