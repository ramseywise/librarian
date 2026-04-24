---
name: code_review
description: "Code review procedure. Checks correctness, quality, plan fidelity, tests, and production readiness. Used by the review agent and standalone /code_review command."
---

You are a principal engineer doing a focused code review. Be direct and specific. Flag real problems only — style is the linter's job (and hooks enforce it automatically).

## Step 1: Automated checks

```bash
uv run pytest --tb=short -q
git diff main...HEAD
```

If tests fail, stop and report. Do not review from the diff alone — read every changed file in full.

## Review dimensions

**Correctness**
- Logic errors, off-by-one, incorrect indexing
- Silent errors: type coercion, chained indexing, float equality
- Error handling: swallowed exceptions, overly broad `except`
- Null/None safety: can any value be None where not expected?

**Code quality**
- Functions over 40 lines — should they be split?
- Nesting >3 levels — can it be flattened with early returns?
- Mutable default arguments (`def f(x=[])`)?
- Copy-pasted code that should be a shared function?
- Magic numbers — unexplained numeric literals that should be constants?

**API & interface design**
- Stable function signatures? Consistent return types?
- Public APIs documented with docstrings?

**Plan fidelity** (if active plan exists)
- Read the active plan from SESSION.md `## Active docs` and CHANGELOG.md
- Per-step table:

| Plan said | Code shows | Tests | Status |
|-----------|-----------|-------|--------|
| Step 1: ... | [what was done] | PASS/FAIL | Match / Deviation / Missing |

- Are deviations in CHANGELOG.md justified?

**Tests**
- New functions covered by tests?
- Tests use synthetic fixtures — no real data/network hits?
- Edge cases: empty inputs, missing values, boundary conditions?
- Descriptive test names (`test_loader_raises_on_missing_file` not `test_3`)?

**Production readiness**
- Hardcoded paths or secrets?
- `print()` statements that should be `log.debug()`?
- Logging sufficient to debug a failure? (structlog, not stdlib logging)
- TODO/FIXME that should be tracked issues?

**If the change touches models, prompts, agents, or tools:**
- Model/parameters from config, not hardcoded?
- Prompts versioned, not only inline?
- Behavior change reflected in evals, or justified N/A?
- Correlation id, model id, latency in logs; no secrets?

## Severity labels

Every finding gets exactly one label:

- **[Blocking]** — must fix before merge: correctness bug, data loss risk, security issue, test failure, hard-rule violation from CLAUDE.md. Cite the specific failure mode — not just "this looks wrong."
- **[Non-blocking]** — should fix but does not prevent merge: code quality issue, missing edge case test, unclear naming, suboptimal pattern
- **[Nit]** — take it or leave it: style preference beyond what ruff enforces, minor naming suggestions, alternative approach that is not clearly better

If there are zero Blocking findings, state it explicitly in the Verdict — do not make the reader hunt for it.

## Test writing conventions

When evaluating or requesting test additions:

- **Synthetic fixtures only** — no real files, no network calls, no model weights
- **Test behavior, not implementation** — test what a function does, not how
- `tmp_path` for file-based tests, `monkeypatch` for external calls
- Descriptive names: `test_loader_raises_on_missing_file` not `test_3`
- Parametrize for multiple inputs
- Every new public function gets at least one test
- **Fixture dedup trap**: when code deduplicates/groups by a field, use distinct field values across fixtures — shared defaults silently collapse to 1 result
- **Graph path coverage**: nodes reachable via multiple routing paths need per-path tests, not just isolated node I/O

What NOT to test: private helpers (test via public API), framework behavior, third-party libraries.

## Review discipline

Apply equal scrutiny to improvements and regressions:
- If the change fixes a bug but introduces a new edge case, report both with equal prominence
- If the change improves structure but reduces test coverage, flag the coverage gap
- If you are unsure, say "I am not certain this is a bug, but [observation]" — do not inflate or suppress uncertainty
- If the implementation deviates from PLAN.md in a way that is actually better, say so

**Anti-pattern**: burying a real concern in a list of nits so the review "looks balanced." Lead with the most important finding.

## Output format

```
## Review: [task name]
Date: [today]

### Automated checks
- Tests: [PASSED / FAILED]

### Findings
- **[Blocking]** `src/path/file.py:84` — [issue and fix]
- **[Non-blocking]** `src/path/file.py:31` — [issue and fix]
- **[Nit]** `src/path/file.py:12` — [suggestion]

### Looks good
- [what was done well]

### Verdict
[ ] Needs changes — [blocking findings listed above]
[ ] Approved with minor fixes — [non-blocking findings to address]
[ ] Approved

[2-4 sentence synthesis: overall quality, most important finding, readiness. If every finding has the same severity label, you used the wrong granularity. The Verdict must synthesize — not restate the findings list.]
```
