---
name: refactor_propose
description: "Structures the pre-change proposal for a refactor: risk-tiered table, grouped changes, and explicit confirmation gate. Used by the refactor agent before any edits."
---

Use this skill during Phase 3 of `code_refactor`, after identifying improvements and before touching any code. A well-structured proposal lets the user review and approve in seconds rather than minutes.

## Proposal format

Output the following sections in order. Do not start editing until the user responds with approval.

### 1. Scope declaration (from `refactor_scope`)

```
## Scope
**In scope**: [files/functions you will touch]
**Out of scope**: [things you noticed but will not touch — one line each with reason]
```

### 2. Risk-tiered change table

Group all proposed changes into three tiers. Be specific: every row needs a `file:line` reference.

```
## Proposed changes

### Safe — mechanical, no logic involved
| # | Location | Change | Pattern |
|---|----------|--------|---------|
| 1 | src/loader.py:12,34,67 | Replace literal `100` with `PAGE_SIZE = 100` | Magic value → constant |
| 2 | src/utils.py:23-41 | Delete `format_legacy()` — no callers found | Dead code removal |

### Low risk — restructuring, behavior preserved
| # | Location | Change | Pattern |
|---|----------|--------|---------|
| 3 | src/loader.py:45-89 | Extract `_parse_row()` from `load_csv()` | Extract function |
| 4 | src/pipeline.py:102 | Flatten 4-level nesting with early returns | Early return |

### Behavioral-adjacent — requires careful review
| # | Location | Change | Why flagged |
|---|----------|--------|-------------|
| 5 | src/auth.py:78 | Rename `check()` → `is_authorized()` — public method, callers must be verified | Rename |
```

**Risk tier definitions:**
- **Safe**: No logic change. Moves, renames of private symbols, deleting dead code, adding constants.
- **Low risk**: Restructures code flow without changing outputs. Extractions, flattenings, consolidations. Covered by tests.
- **Behavioral-adjacent**: Changes that touch public APIs, modify call signatures, alter error paths, or affect untested code. Needs explicit attention.

### 3. What will NOT be done (follow-up recommendations)

List improvements you found that are out of scope or too large for this pass:

```
## Follow-up recommendations (not in this pass)
- src/pipeline.py is structured differently from the rest of the codebase — worth a dedicated refactor pass
- `DataLoader` class mixes I/O and transformation concerns — consider splitting (large change, own task)
- 3 tests are testing implementation details rather than behavior — fragile, but out of scope here
```

### 4. Confirmation gate

End with exactly this line:

```
Ready to apply? Reply **yes** to proceed, or let me know which changes to skip or modify.
```

## How to handle partial approval

If the user approves some changes but not others:
- Acknowledge which are approved and which are skipped
- Update your mental scope — treat skipped items as out of scope for this session
- Proceed only with approved changes, one at a time per `code_refactor` Phase 4

## Rules

- Never edit before receiving approval
- Never bundle "safe" changes into a single step — apply one row at a time, run tests between each
- If a change turns out to be more complex than proposed, stop and re-propose the revised version
- Behavioral-adjacent changes require the user to explicitly approve them — a general "yes" is not sufficient if any behavioral-adjacent items are in the table
