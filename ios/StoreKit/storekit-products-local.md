# Local StoreKit Products

Create a StoreKit Configuration file in Xcode with this subscription group and
these products.

## Subscription Group

Reference name: `MING Pro`

## Products

### MING Pro Monthly

- Product ID: `ming.pro.monthly`
- Type: Auto-renewable subscription
- Duration: 1 month
- Price for US test: USD 9.99
- Display name: `MING Pro Monthly`
- Description: `Deep reports, monthly compass, annual rhythm, and guided oracle.`

### MING Pro Yearly

- Product ID: `ming.pro.yearly`
- Type: Auto-renewable subscription
- Duration: 1 year
- Price for US test: USD 59.99
- Display name: `MING Pro Yearly`
- Description: `A year of MING Pro reflection tools and deep reports.`

## Local StoreKit Test Cases

1. Purchase monthly from a free account.
2. Purchase yearly from a free account.
3. Restore purchase after app reinstall.
4. Cancel or expire subscription in StoreKit test session.
5. Confirm Pro endpoints lock again when entitlement is expired.
6. Force a pending purchase state and confirm Pro remains locked.
7. Point the app at a backend without Apple validation credentials and confirm
   the app shows validation unavailable.

Local StoreKit configuration verifies UI and StoreKit state handling only. Real
Sandbox/TestFlight evidence must use App Store Connect products, sandbox Apple
accounts, a signed build, and backend App Store Server API validation.

## Expected App Entitlement Mapping

| StoreKit state | App entitlement |
| --- | --- |
| Verified active monthly/yearly transaction | `pro_active` |
| No current transaction | `free` |
| Expired transaction | `expired` |
| Refunded or revoked transaction | `revoked` |
| Restore requested but no transaction found | `needs_restore` |
| Pending purchase | no Pro unlock until Apple completes the transaction |
| Cancelled purchase | no Pro unlock and no backend sync |
