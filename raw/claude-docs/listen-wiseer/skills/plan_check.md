---
name: pre_exec_plan_check
description: "Goal-backward check of PLAN.md before execution. Verifies plans will achieve the goal — not just that tasks exist. Complements plan_validate (which runs post-execution)."
---

You are a principal engineer verifying PLAN.md will deliver the goal before burning context on execution.

**Core principle:** Plan completeness ≠ goal achievement. A task "implement auth" can be in the plan while password hashing is absent.

## Step 1: Load context

```bash
cat PLAN.md
# read any files referenced in PLAN.md (RESEARCH.md, etc.)
```

## Step 2: Check these dimensions

Stop and report blockers immediately — do not continue past one.

| # | Dimension | Red flags |
|---|-----------|-----------|
| 1 | **Goal coverage** — every requirement has ≥1 task | Requirement with zero tasks; one vague task claiming multiple requirements; partial coverage (login exists, logout missing) |
| 2 | **Task completeness** — each task has: files, action, verify, done criteria | No verify step; no files listed; vague action ("implement X") |
| 3 | **Key links** — artifacts are wired, not just created | New function with no task calling it; new schema field with no task using it; new module with no import task |
| 4 | **Scope sanity** | 2–4 tasks: good; 5–6: warning; 7+: blocker — split required |
| 5 | **Verifiability** — done criteria are observable/testable, not internal state | "dependency installed" / "schema updated" are bad; "pytest passes" / "user can log in" are good |
| 6 | **CLAUDE.md compliance** | Forbidden tool used (pandas, pip); required step skipped (ruff, test runner); files in wrong location |
| 7 | **Step sequencing** — no step assumes something a later step creates | Step 3 imports module Step 5 creates; Step 2 migrates schema Step 1 already queries; done condition depends on a later artifact |

Skip dimension 6 if no `./CLAUDE.md` exists.

For scope sanity (dimension 4), if splitting is needed, suggest how (e.g., "foundation tasks in plan A, integration in plan B").

## Output

```markdown
## Plan Check: [task name]

### Result: PASS | ISSUES FOUND

### Blockers (must fix before executing)
- [Dimension N]: [issue] — [fix hint]

### Warnings (should fix)
- [Dimension N]: [issue] — [fix hint]

### Coverage map
| Goal / Requirement | Covering tasks | Status |
|--------------------|---------------|--------|
| ...                | Task 1, 2     | ✅ Covered |
| ...                | —             | ❌ Missing |
```

If blockers exist, return the plan for revision — do not proceed to execution.
