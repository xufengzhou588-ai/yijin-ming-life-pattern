# Pro Pattern vs Choice Experiment — 2026-07-23

## Backup

Before making changes, the previous working state was backed up to:

```text
backups/before-pro-pattern-choice-20260723-233116.tar.gz
```

## Product Intent

This experiment folds the “not fortune-telling, not random guessing” product philosophy into the paid Pro experience without turning it into a cold disclaimer.

The goal is to make Pro feel:

- more trustworthy;
- more modern for US users;
- still rooted in Eastern pattern language;
- less like absolute prediction;
- more useful for self-reflection and decision awareness.

## UI Change

The Pro report now has three layers:

1. Quick visual overview
   - `综合速览 / Quick Pattern View`
   - short cards with visual marks and colored backgrounds;
   - designed for scanning and screenshots.

2. Pattern vs Choice
   - `结构与选择 / Pattern vs Choice`
   - separates what the structure suggests from what the user still decides.

3. Detailed Reading
   - keeps the original full-text Pro report for users who want depth.

## Added Paid Value

Each Pro report now includes a module-specific “Before You Decide” checklist:

- Career: deliverables, recognition, proof/case/process.
- Wealth: opportunity vs cost, maximum loss, review/exit timing.
- Relationship: facts vs interpretation, concrete request, protective boundary.

## Local Test

Local Pro test mode:

```bash
BAZI_DEMO_UNLOCK=1 bash tools/start_mac_local_server.sh
```

Test URL:

```text
http://127.0.0.1:8787/app?protest=1&v=88
```

Checked markers:

- `pro-method-panel`
- `Pattern vs Choice`
- `结构与选择`
- `Before You Decide`
- `做决定前问自己`

Demo Pro unlock endpoint returned `pro_active`.

