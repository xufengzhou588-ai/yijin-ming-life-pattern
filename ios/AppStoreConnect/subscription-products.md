# App Store Connect Subscription Products

Status: ready to configure once the app record exists in App Store Connect.

## Subscription Group

- Reference name: `MING Pro`
- User-facing subscription group display name: `MING Pro`

## Product 1 — Monthly

- Product ID: `ming.pro.monthly`
- Reference name: `MING Pro Monthly`
- Type: Auto-renewable subscription
- Duration: 1 month
- Price target: USD 9.99 control; test USD 7.99 and USD 8.99 after retention baseline exists
- Display name: `MING Pro Monthly`
- Description: `Unlock Monthly Compass, complete Oracle and Journal, personalized seven-day quests, deeper reports, ritual soundscapes, and reflection history.`

## Product 2 — Yearly

- Product ID: `ming.pro.yearly`
- Reference name: `MING Pro Yearly`
- Type: Auto-renewable subscription
- Duration: 1 year
- Price target: USD 59.99 control; test USD 39.99 and USD 49.99 after monthly conversion baseline exists
- Display name: `MING Pro Yearly`
- Description: `Best value for ongoing reflection. Includes Monthly Compass, complete Oracle and Journal, personalized quests, deeper reports, ritual soundscapes, and review history.`

## Introductory Offers

Launch default: none.

Add an introductory offer only after pricing and retention strategy are final. If added, update screenshots, review notes, and paywall copy.

## Required Paywall Rules

The native Pro screen must visibly include:

- subscription name;
- price and billing period from StoreKit;
- feature list: Monthly Compass, complete Oracle and Journal, personalized seven-day quests, review history, and ritual soundscapes;
- Restore Purchase button;
- Terms of Use link;
- Privacy Policy link;
- no external payment messaging.
- no promise of luck, merit, random rewards, auto-tapping, leaderboards, or guaranteed outcomes.

## One-Time Purchase Boundary

Do not configure one-time products in App Store Connect until backend scoped
entitlements exist. Reserved P3 concepts:

- `ming.blueprint.complete`: Complete Life Blueprint, USD 9.99-14.99.
- `ming.year_ahead.2027`: annual-edition Year Ahead report, around USD 11.99.
- Relationship Reflection: later single-purchase product after paid demand is validated.

## Reviewer Notes

If Apple Review needs Pro access, provide sandbox tester instructions after products are active in App Store Connect. Do not give a non-IAP bypass for production builds.

## Current Implementation Notes

- iOS product IDs are hardcoded in `StoreKitManager.swift`.
- The local Xcode 16.1 build can compile the StoreKit UI and read products if configured.
- Final production validation should be completed on an Xcode 26+ machine with App Store Server API credentials.
