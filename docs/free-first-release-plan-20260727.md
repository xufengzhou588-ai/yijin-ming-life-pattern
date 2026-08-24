# Free First Release Plan — 2026-07-27

## Decision

Ship the first US App Store version as a free app, then enable paid Pro subscriptions in a later update.

## Why

This reduces first-submission risk:

- no StoreKit product setup required for v1.0;
- no subscription review required for v1.0;
- simpler App Review notes;
- easier user testing after the app is live;
- avoids showing a broken purchase flow while Apple Developer/App Store Connect setup is still pending.

## Implementation

The project now has a release-mode switch:

```text
MING_PRO_MODE=free_first
```

Current default:

- iOS `Info.plist`: `free_first`
- Xcode Debug scheme: `free_first`
- Web default: `free_first`

In free-first mode:

- Pro value remains visible as a future roadmap;
- purchase buttons are hidden;
- restore purchase is hidden;
- web demo unlock is hidden even if the backend is accidentally started with `BAZI_DEMO_UNLOCK=1`;
- StoreKit loading is skipped in the native app.

For later paid testing:

```text
MING_PRO_MODE=storekit
```

and web testing can use:

```text
http://127.0.0.1:8787/app?release=paid_test
```

## What to Test Locally

Free first URL:

```text
http://127.0.0.1:8787/app?v=101
```

Verify:

- free reading can be generated;
- Pro cards show planned value;
- clicking Pro cards opens the Coming Soon panel;
- no monthly/yearly price appears;
- no purchase button appears;
- no restore purchase button appears;
- no demo unlock button appears;
- Oracle remains gated as a planned Pro feature;
- privacy, terms, and support links open.

## Later Paid Update

For v1.1 paid Pro:

1. Apple Developer membership active.
2. App Store Connect app record live.
3. Subscription group `MING Pro`.
4. Products:
   - `ming.pro.monthly`
   - `ming.pro.yearly`
5. `MING_PRO_MODE=storekit`.
6. Public HTTPS backend includes App Store transaction validation.
7. TestFlight purchase/restore QA.

