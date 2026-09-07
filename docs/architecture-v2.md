# Architecture v2

This document fixes the module boundaries for the P0 paid-access and onboarding update.

## Runtime Shape

- `server.py` owns HTTP routing, request validation, entitlement enforcement, App Store server verification, and server-generated Pro payloads.
- `bazi_core/` owns deterministic Four Pillars, trait, annual, monthly, oracle, and system-status computation. It must not read cookies, sessions, StoreKit state, or browser storage.
- `schemas/` owns JSON Schema contracts for generated calculation payloads. Schema changes require matching tests and version notes.
- `web/index.html` owns the browser UI, onboarding flow, local profile/history storage, and rendering. It must not grant Pro access from local state and must treat Pro API failures as locked or unavailable.
- `ios/MINGLifePattern/Services/` owns network and StoreKit integration. StoreKit transactions must be synchronized to the backend before backend-gated Pro content is considered available.
- `ios/MINGLifePattern/Stores/` owns app-visible entitlement state returned by the backend.
- `ios/MINGLifePattern/Views/` owns SwiftUI/WebView presentation only. Views must not mint entitlement cookies or declare Pro directly.
- `docs/` owns product, release, compliance, architecture, and test-baseline records.
- `web/js/analytics-*.js` and `ios/MINGLifePattern/Services/AppAnalytics.swift` own the anonymous event contract. They must not accept birth inputs, precise birthplace, names, raw Oracle questions, report text, or journal text.

## Public Interfaces

Core free reading:

- `POST /api/generate`
- Input: birth datetime, timezone, gender, location, true-solar-time flag, annual/luck ranges.
- Output: `{ ok, result, traits, system }`.

Entitlement:

- `GET /api/entitlement`
- Output: `{ ok, entitlement }`.
- The entitlement source of truth is the server-side SQLite entitlement store,
  not a browser cookie.

StoreKit:

- `POST /api/app-store/transactions`
- Input: StoreKit signed transaction JWS, optional original transaction ID, optional app account token.
- Output: `{ ok, entitlement }`.

App Store notifications:

- `POST /api/app-store/notifications`
- Input: App Store Server Notifications V2 signed payload.
- Output: `{ ok }`.

Pro modules:

- `POST /api/pro/annual-report`
- `POST /api/pro/monthly-compass`
- `POST /api/pro/report`
- `POST /api/oracle/interpret`
- All require active server-side entitlement.

Analytics:

- Contract: `docs/analytics-events-v1.md`.
- Web storage key: `ming.productEvents.v1`.
- iOS storage key: `ming.productEvents.v1`.
- Current behavior: capped local queue; no third-party SDK.
- Any future upload pipeline must reuse the event dictionary and privacy denylist.

## Entitlement Boundary

- The server must reject forged `bazi_native_pro=1` or any other client-declared Pro flag.
- The iOS app may cache StoreKit purchase state for UI messaging, but server-gated Pro endpoints require backend entitlement.
- Session tokens are short-lived, signed by the server, and only point to a
  persisted entitlement subject.
- Refund, revocation, expiry, renewal, and restore flows must converge on the same entitlement store.
- If the entitlement service is unavailable, the app must show an unavailable/degraded state and must not unlock Pro by default.

## Web Onboarding Boundary

- First launch must not render personalized conclusions before birth data is provided.
- Local profile storage may remember that onboarding is complete and may prefill inputs for the same user.
- Editing birth data must create a new saved chart/history entry or require explicit confirmation before replacing the active profile.
- If sample data is retained, it must be labeled `Sample Reading - Not Yours` everywhere it appears.
- Unknown or approximate birth time must be surfaced as lower confidence, especially around hour-pillar and timing claims.

## Shared-Workspace Rules

- `main` must remain runnable after every commit.
- Each chat window must declare and keep to an owned file range before editing.
- P0 paid-access work owns: `server.py`, `tests/`, `ios/MINGLifePattern/Services/`, `ios/MINGLifePattern/Stores/`, `ios/MINGLifePattern/Models/`, and related entitlement docs.
- P0 onboarding work owns: `web/index.html`, future `web/onboarding`, `web/profile`, and `web/state` modules, and related docs.
- If two windows need the same file, one window commits or hands off before the other edits.
- Generated logs, DerivedData, virtual environments, AppleDouble files, and HTML backups stay out of Git.

## P3 Coordination Ownership

- Window 00 / current task: total control, architecture, API contracts, integration, final gate.
- Window 01: `server.py`, backend entitlement modules, backend security tests.
- Window 02: `bazi_core/`, `schemas/`, calculation reliability tests and policy docs.
- Window 03: `web/index.html`, `web/styles/`, `web/js/`, `web/features/`, `web/locales/`.
- Window 04: Today retention, Muyu Reset, seven-day quest, retention events.
- Window 05: `ios/MINGLifePattern/`, Xcode project, StoreKit2, WebView bridge, native haptics and notifications.
- Window 06: `docs/`, `ios/AppStoreConnect/`, commercial model, US copy, event dictionary, TestFlight research, App Store metadata.

If a task crosses ownership, the owning window commits first or hands off a
documented contract before another window edits the same files.
