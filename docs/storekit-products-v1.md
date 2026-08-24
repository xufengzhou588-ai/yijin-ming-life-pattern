# StoreKit Products v1

## Product Group

Subscription group: `MING Pro`

## Products

| Product ID | Type | Price target | User-facing name | Included access |
| --- | --- | --- | --- | --- |
| `ming.pro.monthly` | Auto-renewable subscription | USD 9.99 / month | MING Pro Monthly | All Pro reports, monthly compass, annual rhythm, guided oracle, local export. |
| `ming.pro.yearly` | Auto-renewable subscription | USD 59.99 / year | MING Pro Yearly | Same as monthly, positioned as best value for ongoing reflection. |

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
