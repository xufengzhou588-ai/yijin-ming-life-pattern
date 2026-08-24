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

## Sandbox Test Cases

1. Purchase monthly from a free account.
2. Purchase yearly from a free account.
3. Restore purchase after app reinstall.
4. Cancel or expire subscription in StoreKit test session.
5. Confirm Pro endpoints lock again when entitlement is expired.

## Expected App Entitlement Mapping

| StoreKit state | App entitlement |
| --- | --- |
| Verified active monthly/yearly transaction | `pro_active` |
| No current transaction | `free` |
| Expired transaction | `expired` |
| Restore requested but no transaction found | `needs_restore` |
