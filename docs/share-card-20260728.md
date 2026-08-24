# Share Cards

Date: 2026-07-28

## Purpose

Add a free growth loop before the first App Store release without introducing
account login, cloud sync, or social-network SDK review risk.

## Implemented Cards

1. Core Pattern Card
   - archetype;
   - dominant element;
   - dominant ten-god pattern;
   - practical next move.

2. Daily Focus Card
   - daily focus;
   - best small move;
   - energy leak;
   - reflection question.

## Sharing Behavior

- Uses the native Web Share API when available.
- Falls back to clipboard copy when native sharing is unavailable.
- Does not include a localhost URL in local development shares.
- Does not require login.
- Does not send social account data to the app.

## Product Rationale

For the first release, sharing is safer and more useful than adding Google,
Facebook, X, or Apple account login:

- lower App Store review surface;
- no account deletion flow required yet;
- no third-party SDK privacy disclosures;
- gives users a reason to send the app to friends after the first reading.

## Boundary Copy

The shared text states that the result is for cultural exploration and personal
reflection, not a fixed prediction.

