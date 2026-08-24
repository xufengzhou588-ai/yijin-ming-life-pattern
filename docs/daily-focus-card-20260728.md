# Daily Focus Card

Date: 2026-07-28

## Purpose

Add a free retention feature for the first App Store release without requiring
accounts, cloud sync, push notifications, or paid entitlement setup.

The card appears after a user generates a chart and gives one lightweight daily
prompt. It is designed as a daily reflection/action feature, not a fortune
prediction.

## Free Launch Behavior

- Visible to free users after a chart is generated.
- Does not require login.
- Does not send or store account data.
- Same chart + same local date produces the same card.
- The card changes when the local date changes.
- Pro remains hidden in `free_first` mode.

## Inputs Used

The first implementation is computed in the web client from data already
returned by `/api/generate`:

1. User natal chart:
   - day master element;
   - strongest element;
   - strongest ten-god pattern.
2. Trait engine context:
   - main reminder topic: career stability, wealth retention, or relationship
     pressure.
3. Local current date:
   - mapped into the 60-day stem-branch cycle using a deterministic anchor;
   - converted into today's stem and branch element.

## User-Facing Framing

The card intentionally avoids claims such as:

- today you will become rich;
- today you will meet someone;
- today a specific event will happen;
- today is lucky or unlucky.

It instead gives:

- a daily focus;
- one small action;
- one likely energy leak;
- one reflection question;
- transparent evidence chips.

## QA Completed

- Inline web script syntax check passed.
- `/api/generate` smoke check passed.
- `tools/mac_verify.sh` passed:
  - Python tests: 12 passed;
  - HTTP smoke: passed;
  - Xcode simulator generic build: passed.

