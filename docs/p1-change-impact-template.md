# P1 Rule Change Impact Template

Use this template whenever a calculation, timezone, solar-term, luck-cycle, or trait-weight version changes.

## Change

- Previous version:
- New version:
- Files changed:
- Reason:

## Fixture Impact

```bash
.venv/bin/python -m unittest -v tests.test_bazi_golden_fixtures
```

- Total fixture count:
- Changed fixture ids:
- Changed categories:
- User-visible fields changed:

## User Impact

- Who may see a different chart:
- Who may see different Trait scores:
- Who may see different confidence or uncertainty reasons:
- Migration / messaging:

## Review

- Internal reviewer:
- Professional reviewer A:
- Professional reviewer B:
- Decision:
