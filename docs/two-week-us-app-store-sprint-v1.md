# Two-Week US App Store Sprint v1

## Target

Prepare a first US App Store submission candidate in 14 calendar days.

Reality check: Apple review timing is external. The internal target is a
submission-ready build, TestFlight feedback, and review packet. Approval may
take longer if Apple requests changes.

## Daily Plan

### Day 1 - Commercial Foundation

- Finalize Pro value proposition.
- Add subscription-style paywall structure.
- Add privacy and boundaries copy.
- Document data inventory and launch roadmap.

### Day 2 - Pro Product Depth

- Make career, wealth, relationship, annual, monthly, and oracle benefits read
  as one coherent Pro membership.
- Remove test-price language from user-facing release copy.
- Add restore-purchase and terms/privacy entry points.

### Day 3 - iOS Shell Decision

- Chosen implementation path:
  - SwiftUI native shell with controlled WKWebView for speed;
  - native StoreKit Pro screen;
  - native Trust/legal screen;
  - gradual migration toward deeper native screens after launch.
- Define build bundle id, display name, icon direction, and supported devices.

### Day 4 - StoreKit Products

- Define product ids:
  - `ming.pro.monthly`
  - `ming.pro.yearly`
  - optional `ming.report.lifetime` only if one-time reports stay in scope.
- Build local StoreKit configuration for sandbox testing.
- Add purchase, restore, and entitlement state flows.
- Current status: Swift StoreKit2 skeleton exists; App Store Server validation
  still needs implementation.

### Day 5 - Backend Entitlement Hardening

- Replace demo-only entitlement assumptions with a production-shaped API.
- Keep backend enforcement for Pro reports and oracle.
- Document receipt-validation path.

### Day 6 - Legal and Support Packet

- Draft privacy policy.
- Draft terms of use.
- Draft support page.
- Finalize disclaimers for cultural reflection and non-professional advice.

### Day 7 - English Copy Review

- Review English UI for cultural translation, not literal translation.
- Move dense Chinese metaphysics terms behind optional context.
- Remove fear, guarantee, and deterministic outcome wording.

### Day 8 - Reliability Fixtures

- Add regression tests for boundary dates, timezones, and approximate-time
  behavior.
- Confirm no Pro report exposes raw internal decimal scores.

### Day 9 - Mobile QA

- Test small-screen navigation and Pro/oracle flows.
- Fix text overflow, spacing, and paywall clarity.
- Prepare App Store screenshot flows.

### Day 10 - App Store Connect Prep

- Create metadata draft:
  - title;
  - subtitle;
  - description;
  - keywords;
  - privacy labels;
  - review notes.
- Prepare screenshots and app preview copy.

### Day 11 - TestFlight Build

- Build first iOS candidate.
- Run sandbox purchase/restore tests.
- Invite small internal tester group.

### Day 12 - Feedback Fixes

- Fix top clarity and trust issues.
- Improve onboarding if users cannot explain the app after one minute.

### Day 13 - Submission Polish

- Final QA.
- Verify links, purchases, restore, privacy, terms, screenshots, and review
  notes.

### Day 14 - Submit

- Submit to App Review.
- Prepare fast-response checklist for review questions.

## Critical Path

The schedule only works if we defer:

- user accounts and cloud sync;
- full native rewrite;
- open-ended AI chat;
- complete global location coverage;
- professional calibration claims;
- any claim of guaranteed prediction.

## Launch Definition

Minimum launchable v1:

- free life-pattern reading;
- Pro membership paywall;
- Pro deep reports;
- Pro monthly/annual guidance;
- Pro oracle reflection;
- privacy/terms/support pages;
- StoreKit purchase and restore;
- backend-enforced Pro entitlement;
- no absolute predictions.
