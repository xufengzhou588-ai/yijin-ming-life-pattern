# Daily Check-in Stamps

Date: 2026-07-30

## What changed

Added a first-pass Daily Seal check-in below the Daily Focus card.

The feature is intentionally visual-first:

- 5 tappable seal icons: Focus, Spark, Ground, Connect, Restore
- One daily collection action
- Current streak
- 7-day seal rail
- Local-only storage with `localStorage`

## Why

A one-time life-pattern reading is not enough for retention. The app needs a lightweight reason to return daily. The check-in creates a small ritual loop without turning the product into a plain text journal.

## Data boundary

Records stay on device in `ming.dailyCheckins.v1`.

Stored fields:

- date
- selected seal key
- daily pillar label
- daily relation/theme
- five-element flow label
- timestamp

No account sync or server storage is used in this first pass.

## Product positioning

Free users can build a daily habit. Pro can later unlock weekly/monthly pattern review based on these local check-ins.
