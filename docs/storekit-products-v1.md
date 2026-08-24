# StoreKit Products v1

## Product Group

Subscription group: `MING Pro`

## Products

| Product ID | Type | Price target | User-facing name | Included access |
| --- | --- | --- | --- | --- |
| `ming.pro.monthly` | Auto-renewable subscription | USD 9.99 / month | MING Pro Monthly | All Pro reports, monthly compass, annual rhythm, guided oracle, local export. |
| `ming.pro.yearly` | Auto-renewable subscription | USD 59.99 / year | MING Pro Yearly | Same as monthly, positioned as best value for ongoing reflection. |

## P3 Product Ladder

The US paid release separates static report value from ongoing reflection value.

Free includes:

- core life-pattern blueprint;
- Today card;
- daily seal;
- Muyu Reset;
- one seven-day pattern quest;
- simple Oracle preview;
- on-device history.

One-time purchases are reserved for static or edition-based reports:

| Reserved Product ID | Type | Price test | User-facing name | Included access |
| --- | --- | --- | --- | --- |
| `ming.blueprint.complete` | Non-consumable | USD 9.99-14.99 | Complete Life Blueprint | Full static blueprint report. |
| `ming.year_ahead.2027` | Non-consumable annual edition | Around USD 11.99 | Year Ahead 2027 | One annual rhythm report for the named edition year. |

Do not expose the reserved one-time products in the paywall until the backend
entitlement contract supports scoped non-subscription purchases.

Pro remains the subscription tier for continuing value:

- Monthly Compass;
- complete Oracle and Journal;
- personalized seven-day quests;
- weekly and monthly history reviews;
- more rituals and soundscapes;
- future cross-device sync.

P3 subscription price experiments:

- Monthly: USD 7.99, 8.99, 9.99.
- Yearly: USD 39.99, 49.99, 59.99.

Current App Store Connect control values remain USD 9.99 monthly and USD 59.99
yearly until a pricing experiment is explicitly scheduled.

## Entitlement Shape

The backend and app should normalize Apple purchase state into this response:

```json
{
  "status": "free | pro_active | expired | needs_restore",
  "is_pro": true,
  "tier": "free | pro",
  "source": "app_store",
  "environment": "sandbox | production",
  "product_id": "ming.pro.yearly",
  "expires_at": "2026-07-29T00:00:00Z",
  "needs_restore": false,
  "storekit_ready": true
}
```

## Purchase Flow

1. User opens Pro paywall.
2. App requests StoreKit products.
3. User selects monthly or yearly.
4. StoreKit completes purchase.
5. App sends signed transaction data to backend `POST /api/app-store/transactions`.
6. Backend validates with Apple and returns normalized entitlement.
7. Pro endpoints unlock only when `is_pro` is true.

## Restore Flow

1. User taps Restore Purchase.
2. App runs StoreKit restore / current entitlements query.
3. App sends verified transaction data to backend.
4. Backend updates entitlement state.
5. UI shows Pro Active or a clear not-found message.

## Review Notes

- This app sells digital interpretation content, so App Store IAP must be used.
- Do not mention external payment methods.
- Paywall must show subscription nature, price, and restore entry.
- Pro does not promise guaranteed outcomes.
- Pro content is informational and reflective, not professional advice.
- Do not sell luck, merit, random rewards, auto-tapping, or leaderboards.

## Web Prototype Status

The current web build exposes a production-shaped entitlement response, but uses
`source: local_demo` and `storekit_ready: false`. This is intentional until the
iOS StoreKit integration is implemented.

The backend now includes `POST /api/app-store/transactions` as an integration
point. By default it returns `app_store_validation_not_configured` because Apple
validation is not implemented yet. For local sandbox UI testing only, set:

```powershell
$env:BAZI_STOREKIT_STUB="1"
python server.py
```

Do not use this stub in production.
