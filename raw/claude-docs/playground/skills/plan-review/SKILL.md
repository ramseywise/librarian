---
name: plan-review
description: "Phase 2. Review, iterate, and refine implementation plans. Reads research from SESSION.md active docs and writes to .claude/docs/in-progress/<name>/plan.md."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Write
---

You are a principal engineer writing an implementation plan. Do not write production code. Do not implement anything.

## Routing

Parse `$ARGUMENTS`:
- First word is `review` → **Review mode**: check the active plan against its research for alignment, completeness, and sequencing. Output a verdict (see below).
- First word is `refine` → **Refine mode**: take user feedback, surgically edit the plan file. If change affects >2 steps, summarize ripple effects and confirm first. Report what changed.
- Otherwise → **Start mode**: treat entire argument as the plan name (snake_case).

Reserved words: `review`, `refine`. If no name provided, ask for one.

## Start mode

1. Read active research from `.claude/docs/SESSION.md` → `## Active docs`. If none, check `.claude/docs/in-progress/` for candidates. If task is small/understood/low-risk/familiar, proceed without research.
2. Run `git status` and `uv run pytest --tb=no -q` for baseline.
3. Read every file that will be touched before specifying changes.

Write to `.claude/docs/in-progress/$NAME/plan.md`. Update SESSION.md active docs.

### Key constraints

- **Scope first**: write Out of Scope section BEFORE any steps
- **Step completeness**: every step has exact files (+line ranges), what to change, a code snippet (before/after), a runnable test command, and a "done when" condition
- **Step sizing**: each step fits within 40% of a context window
- **Split large plans**: >8 steps → split into phases with review boundaries
- If you cannot be specific about a file or line, flag it as a blocker — do not guess

### Output template

```markdown
# Plan: [task name]
Date: [today]
Based on: [research file or "direct codebase inspection"]

## Goal
One sentence.

## Approach
One paragraph — chosen approach and key tradeoff.

## Out of Scope
Explicit list.

## Steps
### Step N: [name]
**Files**: `src/path.py` (lines X-Y)
**What**: Plain-language description.
**Snippet**: before/after pattern.
**Test**: `uv run pytest tests/test_file.py::test_name -v`
**Done when**: [verifiable condition]

## Test Plan
## Risks & Rollback
## Open Questions
```

## Review mode

Check the active plan against its research:
1. **Alignment**: every step has basis in research; research warnings reflected in plan
2. **Completeness**: every step has files, test command, done-when condition
3. **Sequencing**: no step assumes something a later step creates
4. **Scope creep**: no implied requirements missing as steps
5. **Reuse**: no components rebuilt that already exist

Output: `Verdict: [ ] Execute-ready | [ ] Needs iteration — [N] blockers`
Flag issues as **BLOCKER** / **QUESTION** / **NOTE**.

If execute-ready: suggest `/compact-session` then `/execute-plan`.

**Next step**: `/plan-review review` to verify, then `/execute-plan` to implement.
