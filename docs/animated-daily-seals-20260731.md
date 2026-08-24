# Animated Daily Seals

Date: 2026-07-31

## What changed

The five Daily Seal choices were upgraded from static symbols into lightweight animated SVG scenes.

## Seal concepts

- Focus / 定心: a small seated practitioner with a breathing compass aura.
- Spark / 起势: a figure lifting a brush or torch while a small flame rises.
- Ground / 安土: a figure working with mountain/earth strata as the ground settles.
- Connect / 结缘: two figures around a pulsing heart-knot / linked-thread mark.
- Restore / 养源: a spring eye with water ripples and a growing sprout.

## Implementation

- No GIF/video assets were added.
- Animation uses inline SVG plus CSS keyframes.
- `prefers-reduced-motion: reduce` disables the animations.

This keeps the App Store build small, crisp, and easier to maintain while giving the check-in section more Eastern ritual personality.
