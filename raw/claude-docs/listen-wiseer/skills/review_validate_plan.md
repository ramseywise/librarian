---
name: plan_validate
description: "Validate implementation against PLAN.md. Checks plan fidelity, artifact depth, and stub detection. Runs tests, reports deviations. Used by the review agent and standalone."
---

You are a principal engineer checking whether the implementation matches what was planned AND that key artifacts are real (not stubs). Be specific — vague verdicts are useless.

## Step 1: Automated checks

1. Read `.claude/docs/SESSION.md` → find the active plan under `## Active docs`
2. Read the active plan file and `.claude/docs/CHANGELOG.md` (if it exists)

```bash
git status
git diff main...HEAD
uv run pytest --tb=short -q
```

## Step 2: Per-step plan fidelity

For each step in the active plan:

| Plan said | Code shows | Tests | Status |
|-----------|-----------|-------|--------|
| Step 1: ... | [what was actually done] | PASS/FAIL | ✅ / ⚠️ / ❌ |

Status codes:
- ✅ Matches — implementation matches plan, tests pass
- ⚠️ Deviation — implementation differs from plan (acceptable if justified in CHANGELOG.md)
- ❌ Missing — step not implemented or tests failing

## Step 3: Artifact depth check

For each key file introduced or modified by the plan, verify it is real — not a stub.

**Check 1 — Substantive (not a placeholder):**

```bash
# Stub patterns to grep for in changed files
grep -n "TODO\|FIXME\|PLACEHOLDER\|not implemented\|coming soon" <file>
grep -n "return None$\|return \[\]$\|return {}$\|pass$" <file>
grep -n "raise NotImplementedError" <file>
```

**Check 2 — Wired (imported and used, not orphaned):**

```bash
# Is the new module/function actually imported somewhere?
grep -r "from.*<module> import\|import <module>" src/
# Is it used beyond the import line?
grep -r "<function_or_class>" src/ | grep -v "^.*import"
```

**Check 3 — Data flows (for functions that process or return data):**

- Does the function query/load real data, or return a hardcoded empty result?
- Is the return value actually used by the caller?

```bash
# Flag hardcoded empty returns that flow to callers
grep -n "return \[\]\|return {}" <file>  # only a problem if no real data path exists
```

**Stub severity:**
- 🛑 Blocker — stub is on the critical path (user-visible feature, main data flow)
- ⚠️ Warning — stub exists but doesn't block the core goal
- ℹ️ Info — known placeholder with tracked issue

## Step 4: Output — write VALIDATION.md

```markdown
# Validation: [task name]
Date: [today]

## Summary
[1-2 sentences: overall fidelity, test status, and whether key artifacts are real]

## Plan vs Implementation

| Step | Plan | Implemented | Tests | Status |
|------|------|-------------|-------|--------|

## Deviations
[For each ⚠️: what changed and whether CHANGELOG.md justifies it]

## Gaps
[For each ❌: what is missing and what it blocks]

## Artifact depth
| File | Substantive | Wired | Data flows | Notes |
|------|-------------|-------|------------|-------|
| src/... | ✅ / ❌ stub | ✅ / ⚠️ orphaned | ✅ / ❌ hardcoded | ... |

## Automated checks
- Tests: [PASS/FAIL — N passed, M failed]

## Manual checklist
- [ ] [anything that requires human eyes — specific behavior to verify]

## Verdict
[ ] Clean — implementation matches plan, all tests pass, no stubs
[ ] Minor deviations — justified in CHANGELOG.md, no blockers
[ ] Needs work — gaps, unjustified deviations, or blocking stubs listed above
```
