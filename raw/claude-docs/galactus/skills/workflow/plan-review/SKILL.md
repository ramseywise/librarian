---
name: plan-review
description: "Phase 2 planning — write, review, refine implementation plans, or propose code quality improvements before applying. Modes: start (new plan), review (check for execute-readiness), refine (apply feedback), refactor (code quality pass)."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Edit Write
---

You are a principal engineer. Do not write production code until explicitly in apply mode. Do not implement anything without user approval.

## Routing

Parse `$ARGUMENTS`:
- `review` → **Review mode**: check active plan for execute-readiness
- `refine` → **Refine mode**: apply user feedback to the active plan file
- `refactor` → **Refactor mode**: code quality pass on a codebase area — propose then apply
- Anything else → **Start mode**: new implementation plan named by the argument (kebab-case)

Reserved words: `review`, `refine`, `refactor`. If no argument, ask for one.

---

## Start mode — new implementation plan

### Step 1 — Ticket and branch setup

Before writing anything:

1. **Ticket**: Ask — "Which Linear ticket is this for? (e.g. `VIR-179`, or `none` for exploratory work)"

2. **Branch**: Run `git branch --show-current` and show the result. Then ask:
   > "You're on `<branch>`. Is this the right branch for this work?"
   - **Yes** → proceed
   - **No / different branch** → ask which branch, then `git checkout <branch>`
   - **Need a new branch** → run `/checkout VIR-{id}` to create a Linear-linked branch first, then continue
   - **No ticket (exploratory)** → proceed on current branch, use date prefix for filename

3. **Filename**:
   - With ticket: `VIR-{id}-{name}.md` (e.g. `VIR-179-ablation-agent-rag-optimization.md`)
   - No ticket: `{YYYY-MM-DD}-{name}.md` — and if no ticket exists, suggest `/linear-spike` before proceeding

### Step 2 — Research and baseline

4. Check `.claude/docs/research/` for a matching research file. Small/familiar/low-risk tasks can proceed without research.
5. Run `git status` and `uv run pytest --tb=no -q` for baseline.
6. For each directory containing files that will be touched, read its `README.md` if present — this surfaces conventions before specifying changes.
7. Read every file that will be touched before specifying changes.

Write to `.claude/docs/plans/{filename}`.

### Constraints

- **Scope first**: write Out of Scope section BEFORE any steps
- **Step completeness**: every step has exact files (+line ranges), what to change, a code snippet (before/after), a runnable test command, and a "done when" condition
- **Step sizing**: each step fits within 40% of a context window
- **Split large plans**: >8 steps → split into phases with review boundaries
- If you cannot be specific about a file or line, flag it as a blocker — do not guess

### Output template

```markdown
# Plan: [task name]
Ticket: VIR-{id}
Date: [today]
Branch: [branch name]
Based on: [research file or "direct codebase inspection"]

## Goal
One sentence.

## Approach
One paragraph — chosen approach and key tradeoff.

## Architecture
3-5 lines: components, data flow, where this fits in the existing system. Human-readable — a peer reviewer should understand the shape without reading the steps.

## Key Decisions
| Decision | Why | Alternatives rejected |
|---|---|---|
| [choice made] | [reason] | [what was considered and ruled out] |

## Invariants
- [truth the executor must not violate — e.g. "module-level buffer is intentional, reset at render() start"]
- [cross these lines only with explicit user instruction]

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
| Question | Owner | Status |
|---|---|---|
| [question] | [name or "unowned"] | open / resolved: [answer] / deferred: [reason] |
```

---

## Review mode — check for execute-readiness

Check the active plan against its research:
1. **Alignment**: every step has basis in research; research warnings reflected
2. **Completeness**: every step has files, test command, done-when condition
3. **Sequencing**: no step assumes something a later step creates
4. **Scope creep**: no implied requirements missing as steps
5. **Reuse**: no components rebuilt that already exist

### DoR Gate — must pass before executing

| Criterion | Check |
|---|---|
| **AC** | Are acceptance criteria explicit and testable (not vague)? |
| **Value** | Is the WHY stated — user value or technical justification? |
| **Risks & Dependencies** | Are blockers and cross-team dependencies identified? |
| **Estimate** | Is the scope appropriately sized (≤8 steps, fits a sprint)? |
| **Open Questions** | All open questions resolved or explicitly deferred with owner? |

Any DoR failure → flag as **BLOCKER** and stop. A plan that isn't ready shouldn't be executed.

Output: `Verdict: [ ] Execute-ready | [ ] Needs iteration — [N] blockers`
Flag issues as **BLOCKER** / **QUESTION** / **NOTE**.

If execute-ready: call `/compact "phase: plan → execute"` to snapshot and compact before implementing.
The PreCompact hook writes a checkpoint so the execute phase starts with clean context.

**Next step**: `/plan-review review` to verify, then `/execute-plan` to implement.

---

## Refine mode — apply feedback

Take user feedback from the conversation, surgically edit the plan file. If change affects >2 steps, summarize ripple effects and confirm first. Report what changed and why.

---

## Refactor mode — code quality pass

Quality-driven, not plan-driven. Read the code, find what can be improved, propose it, apply after approval.

### Before starting
1. Confirm scope — which files/modules are in play
2. Run test baseline: `uv run pytest --tb=short -q` — if red, stop and report
3. Read all files in scope fully before forming opinions

### Propose before apply

Present all changes in a risk-tiered table. Do not edit until user approves.

| Risk | Definition | Examples |
|---|---|---|
| **Safe** | Mechanical, no logic involved | Constants, dead code, private renames |
| **Low** | Restructuring, behavior preserved | Extract function, flatten nesting |
| **Behavioral-adjacent** | Requires careful review | Public API rename, error handling change |

Behavioral-adjacent changes need per-item approval.

### Apply rules
- One logical change at a time
- `uv run pytest --tb=short -q` after each change — compare against baseline
- If a test breaks: stop, revert, diagnose. Do not push through or modify tests to pass.
- Do not cascade ("this fix revealed the caller should also change") or gold-plate
- If refactor would touch >10 files → switch to the full `/research` → `/plan` → `/execute` pipeline

### Output
After applying: what changed (`file:line`), test results (baseline vs final), bugs noted but not fixed, follow-up recommendations.
