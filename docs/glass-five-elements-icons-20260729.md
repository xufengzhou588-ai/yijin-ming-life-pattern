# Glass Five Elements Icons

Date: 2026-07-29

## What changed

The daily Five Elements flow icons now follow the first-row concept direction from the ImageGen exploration: luminous glass orbs with clear, literal inner shapes.

## Icon mapping

- Wood: sprout and leaves
- Fire: flame
- Earth: mountain and ground line
- Metal: faceted crystal
- Water: droplet and ripples

## Product reason

The earlier symbols were atmospheric but too abstract for US/global users. This version keeps the Chinese mystic mood through glow, glass, and ritual color, while making each element readable without understanding Chinese text.

## Implementation

- Icons are inline SVG returned by `elementIcon()`.
- The orb shell is pure CSS, so it stays sharp inside the app and does not add image-loading cost.
- The same icon system can later be reused in paid reports, share cards, and onboarding.
