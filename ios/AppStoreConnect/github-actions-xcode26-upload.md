# GitHub Actions Xcode 26 Upload

Status: recommended final build/upload path for the MING 1.0 free-first App
Store release when the local Mac only has Xcode 16.1.

Workflow:

```text
.github/workflows/ios-app-store.yml
```

## Why This Exists

The local Mac can run simulator builds and Python/web validation, but it has
Xcode 16.1 and iOS 18.1 SDK. Final App Store uploads require an upload-capable
Xcode 26+ environment. This workflow mirrors the successful Couple Flight Chess
release pattern while using MING's native Xcode project.

## Required GitHub Repository

Push this repository to GitHub before using the workflow.

Current local repository state on 2026-10-10:

- No Git remote is configured.
- Team ID: `WQ8RHQUVQQ`
- Bundle ID: `app.mingpattern.life`
- Scheme: `MINGLifePattern`
- Project: `MINGLifePattern.xcodeproj`

## Required GitHub Secrets

Create an App Store Connect API key:

1. App Store Connect
2. Users and Access
3. Integrations
4. App Store Connect API
5. Create key
6. Recommended role: App Manager or Admin
7. Download the `.p8` key once

Add these repository secrets in GitHub:

```text
APP_STORE_CONNECT_API_KEY_ID
APP_STORE_CONNECT_ISSUER_ID
APP_STORE_CONNECT_API_KEY_BASE64
```

Create the base64 value on macOS:

```bash
base64 -i AuthKey_XXXXXXXXXX.p8 | pbcopy
```

Never commit the `.p8` file, Issuer ID, Key ID, contact phone, email, or other
private release credentials to the repository.

## How To Run

1. Push the latest release-prep commit to GitHub.
2. Open the GitHub repository.
3. Go to Actions.
4. Choose `iOS App Store`.
5. Run workflow.
6. First run: set `upload_to_app_store` to `false`.
7. If archive/export succeeds and the IPA artifact is present, run again with
   `upload_to_app_store` set to `true`.

## Expected Output

- Artifact: `MINGLifePattern-XCArchive`
- Artifact: `MINGLifePattern-AppStore-IPA`
- If upload is enabled, the build appears in App Store Connect / TestFlight
  after Apple processing.

## Workflow Validation

The workflow runs:

- Python dependency install
- `pytest`
- Python compile check
- JS syntax checks for the hosted web app files
- `plutil` Info.plist lint
- `git diff --check`
- free-first production config diagnostic
- Xcode archive on `macos-26`
- IPA export
- optional App Store Connect upload

## Known Remaining External Requirements

- `ming-life-pattern.netlify.app` must resolve and proxy `/api/*` to the
  production API over HTTPS before App Review submission.
- App Store Connect app record for `MING · Life Pattern` must exist.
- App Privacy labels must match final production logging/analytics behavior.
- Upload a short real-device review video or be ready to provide it in
  Resolution Center if Apple requests more information.
