# Translation QA Run — 2026-07-24

## Backup

Before translation QA changes, the current text state was backed up to:

```text
backups/before-translation-qa-20260724-004951.tar.gz
```

## Scope

Reviewed and updated:

- `web/index.html`
- `ios/AppStoreConnect/app-metadata-en-US.md`
- `ios/AppStoreConnect/review-notes.md`
- `docs/translation-qa-v1.md`

## What Changed

Created a translation standard:

```text
docs/translation-qa-v1.md
```

The standard defines how MING should translate Chinese pattern language into US-facing product English:

- preserve the original meaning;
- avoid literal metaphysics translation;
- keep user agency;
- avoid fixed-fate claims;
- use pattern/rhythm/reflection language;
- frame Pro as depth and clarity, not stronger prediction.

## Key UI Copy Improvements

Changed awkward or high-risk English into more natural product language:

- `No fatalistic fear` → `No fear-based claims`
- `Luck / Annual` → `Timing / Annual`
- `Fixed Report` → `Structured Report`
- `Not Absolute Prediction` → `Not a Fixed Prediction`
- `How to Read This` → `How to Read This Report`
- `Wealth Pro Fixed Report` → `Money & Resources Pro Report`
- `Wealth Deep Dive` → `Money & Resources Deep Dive`

Reduced language that could imply guaranteed outcomes, fixed fate, or financial prediction.

## App Store Copy Improvements

Updated App Store metadata and review notes to use safer US-facing language:

- “fixed prediction” instead of “fatalistic prediction” where user-facing copy needed a softer frame;
- “does not promise future outcomes” instead of “does not guarantee future outcomes”;
- “not as a tool for fixed future outcomes” instead of “not fortune-telling with guaranteed results.”

## Validation

JavaScript syntax check:

```bash
node --check /tmp/yijin-inline-script-translation2.js
```

Result: passed.

Local page check:

```text
http://127.0.0.1:8787/app?protest=1&v=90
```

Verified markers:

- `No fear-based claims`
- `Timing / Annual`
- `Structured Report`
- `Not a Fixed Prediction`
- `Money & Resources Pro Report`
- `How to Read This Report`
- `Pattern vs Choice`

## Current Translation Position

The English version is now closer to:

> Eastern pattern wisdom translated into modern self-understanding.

It should feel less like a literal fortune-telling translation and more like a trustworthy reflection and decision-awareness product for US users.

