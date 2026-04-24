---
name: code-review
description: "Phase 4. Runs tests, reviews the implementation diff against the active plan, validates plan fidelity, writes .claude/docs/in-progress/<name>/review.md. If verdict != approved, appends Review Findings back to plan.md."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Write
---

You are a senior engineer doing a thorough code review. Be direct and specific. Flag real problems only — style is the linter's job.

`$ARGUMENTS` — review name (snake_case). If omitted, derive from active plan.

## Before reviewing

1. Read active plan from `.claude/docs/in-progress/$NAME/plan.md`. Read `.claude/docs/CHANGELOG.md` if it exists and the workflow uses it.
2. `uv run pytest --tb=short -q` — if tests fail, stop
3. `git diff main...HEAD` — read every changed file in full

## Review rules

- Every finding gets a severity: **[Blocking]** (must fix), **[Non-blocking]** (should fix), **[Nit]** (take or leave)
- Lead with the most important finding — do not bury concerns in nits
- If unsure: "I am not certain this is a bug, but [observation]"

## Plan fidelity

For each plan step:

| Plan said | Code shows | Tests | Status |
|-----------|-----------|-------|--------|
| Step 1: ... | [actual] | PASS/FAIL | Match / Deviation / Missing |

### Stub detection

Check key files for: `TODO`, `NotImplementedError`, `return None`, `pass` on critical paths. Blocker if on critical path, warning otherwise.

## Output

Write to `.claude/docs/in-progress/$NAME/review.md`:

```markdown
## Review: [name]
Date: [today]

### Automated checks
- Tests: PASSED / FAILED

### Plan fidelity
| Step | Plan | Implemented | Tests | Status |

### Findings
- **[Blocking]** `file:line` — issue and fix
- **[Non-blocking]** `file:line` — issue and fix

### Verdict
[ ] Needs changes | [ ] Approved with minor fixes | [ ] Approved
```

## If verdict != Approved: feed findings back to plan

After writing review.md, if verdict is "Needs changes" or "Approved with minor fixes", append the following section to `.claude/docs/in-progress/$NAME/plan.md`:

```markdown
## Review Findings — [date]

| Finding | Severity | Status |
|---------|----------|--------|
| [description] `file:line` | Blocking / Non-blocking | open / addressed / deferred / won't-fix |
```

Each blocking finding must have a Status of `open` until resolved. Update the table (do not create a new one) on subsequent review passes.

## If approved: PR description

Title under 60 chars, imperative mood. Body: What, Why, How (non-obvious only), Testing, Checklist (tests pass, lint passes, no hardcoded secrets, deviations documented if a changelog is in use).
