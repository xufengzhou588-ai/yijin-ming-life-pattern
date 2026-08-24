# Privacy Data Inventory v1

This document tracks data used by `MING · Life Pattern` so App Store privacy
labels, privacy policy, and backend architecture can stay aligned.

## Data Used in the Current Prototype

| Data | Purpose | Stored by default | Notes |
| --- | --- | --- | --- |
| Birth date | Chart calculation | No | Required for BaziCoreOutput. |
| Birth time | Chart calculation | No | Accuracy level is collected to explain uncertainty. |
| Birthplace | Calendar, timezone, and optional solar-time context | No | Country, region, city, timezone, longitude, latitude. |
| Gender | Luck-cycle direction and traditional calculation policy | No | `unknown` remains available. |
| Name or nickname | Display personalization only | No | Not used for calculation. |
| Generated chart | User review and optional history | Opt-in local only | Saved in browser local storage in the web prototype. |
| Oracle question | Guided reflection and optional journal | Opt-in local only | Do not use for ad targeting. |
| Product events | Conversion testing | Local only in prototype | Must not include birth details or raw questions. |
| Pro entitlement | Paid feature access | Test cookie only | Must become StoreKit receipt-backed before release. |

## Production Policy Direction

- Default stance: private by default, save only when the user chooses.
- Do not sell or share birth data.
- Do not use birth data, oracle questions, or saved readings for ad tracking.
- Avoid collecting account data until cloud sync or cross-device restore is
  truly needed.
- If accounts are added, provide data deletion and export paths.
- Paid access must be enforced by backend entitlement checks, not frontend
  visibility alone.

## App Store Privacy Label Draft Inputs

Likely data categories:

- Contact Info: only if account or support email is added.
- User Content: saved oracle questions and notes, only if sync is added.
- Identifiers: App Store receipt/account identifier for Pro access.
- Usage Data: lightweight product events, if sent to a server.
- Sensitive Info: avoid classifying birth details as broadly sensitive by
  keeping them purpose-limited, transparent, and not used for tracking.

Final labels must reflect the production implementation, not this prototype.

## Open Decisions

1. Will v1 require login, or only App Store receipt restore?
2. Will saved charts remain device-only at launch?
3. Will analytics be local-only, first-party server, or third-party SDK?
4. Will oracle journals sync across devices?
5. What is the user-facing account deletion path if accounts exist?
