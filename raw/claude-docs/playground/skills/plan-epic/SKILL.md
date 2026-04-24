---
name: plan-epic
description: Break down an epic from ROADMAP.md into actionable, well-specified tasks. Use when the user asks to plan an epic, break down tasks, or says things like "plan E12", "brich E12 in Tasks runter", or "plan das nächste Epic".
model: opus
---

Break down epic $ARGUMENTS from ROADMAP.md into actionable tasks. Act as a **Tech Lead** — translate product goals into implementable, well-specified tasks. Follow this process strictly.

Always follow the rules given by /.claude/skills/backend/SKILL.md and /.claude/skills/frontend/SKILL.md.

**GitHub Projects sync:** Use the github-projects SKILL for all GraphQL templates and configuration variables.

## Input
- Read the target epic from `ROADMAP.md` — understand goals, ADRs, and scope bullets
- For legacy milestones M0–M11, read `docs/milestones/M{n}-TASKS.md` and `ROADMAP.md`
- If $ARGUMENTS is empty, ask which epic to plan

## Step 0: Set Epic Status → In Progress
Find the Epic issue number from `ROADMAP.md` (`#NNN` after the epic heading).
**GitHub sync (best-effort):** Use the two-step pattern from github-projects SKILL — get item ID via organization query, then set status to `{STATUS_IN_PROGRESS}`. Skip silently if item not found.

## Step 1: Prerequisite Check
- Check milestone state: `gh api repos/{REPO}/milestones --jq '.[] | .title + " → " + .state'`
- As fallback, check predecessor TASKS files for `[ ]` or `[~]` tasks
- If the target epic depends on an incomplete predecessor, warn and ask whether to proceed

## Step 2: Codebase Analysis
Use an Explore agent to analyze the current codebase:
- Find all files affected by the epic (exact paths, current state)
- Identify existing patterns, conventions, and test structure
- Note what already exists vs. what needs to be created

## Step 3: Skill Compliance Check
Read all applicable SKILL.md files and check for conflicts with planned tasks. Present conflicts to the user — do not resolve silently.

## Step 4: Task Breakdown
For each task, specify:
- **ID**: sequential `T-XX` within the epic
- **Depends on**: list of prerequisite task IDs
- **What**: one-paragraph description of what to do and why
- **Files**: exact paths to create or modify
- **Specification**: code snippets, API contracts, or behavioral descriptions where helpful
- **Acceptance criteria**: concrete, verifiable conditions for "done"
- **Tests**: layer (unit/integration/none), what to test, TDD or not

## Step 4b: Concept Gap Check
After drafting, verify completeness against the epic's goals:

- **Coverage:** every goal/scope bullet has at least one task (or is marked out of scope with reason)
- **Error & edge cases:** failure paths covered?
- **Cross-cutting concerns:** auth, validation, audit logging addressed?
- **Data lifecycle:** create/read/update/delete/list for new entities?
- **Integration points:** all external system interactions modeled?
- **Migration:** schema/API changes have migration or compatibility plan?

Present a brief gap summary to the user even if no gaps found.

## Step 5: Dependency Graph & Parallelization Plan
- Draw ASCII dependency graph; identify critical path and parallelizable tasks
- **File Ownership Matrix** for parallel tasks:
  ```
  | File                    | T-01 | T-02 |
  |-------------------------|------|------|
  | src/.../Entity.java     | W    | R    |
  ```
  Two tasks with `W` on the same file cannot run in parallel.

- **Breaking Change Detection:** Mark tasks `breaking` when they change API contracts, DB schema non-additively, or remove/rename public interfaces. Breaking tasks get a PR with review gate.

## Step 6: Create Issues (Two-Pass)

### Pass 1 — Create all issues, collect numbers and global IDs
```bash
gh issue create -R {REPO} \
  --title "E{n} T-{nn}: {short description}" \
  --body "$(cat <<'EOF'
## Summary
{1-3 sentence summary}

> **Detailed spec:** see `docs/epics/E{n}-TASKS.md` — section "T-{nn}"

### Acceptance Criteria
{Abbreviated criteria}

### Dependencies
Depends on: {T-XX or "none"}
EOF
)" \
  --milestone "E{n}: {Milestone Title}" \
  --label {backend|frontend|ai-service|devops}
```

Fetch global ID after creation (needed for sub-issues API):
```bash
gh issue view {NR} -R {REPO} --json id -q .id
```

Build mapping: `T-01 → {number: NNN, id: XXXXXXXXX}, ...`

### Pass 2 — Patch dependency tasklists
For each issue with dependencies, append a `### Blocked by` tasklist with real issue numbers.

### Sub-issues and prioritization
Use github-projects SKILL to: (1) add each task as sub-issue of the Epic, (2) prioritize in dependency order, (3) add `breaking` label if applicable.

### Add to project, set Status = Ready
Use github-projects SKILL: add each issue to the project (note item ID), then set status to `{STATUS_READY}`.

### Iteration assignment
Query available iterations dynamically using github-projects SKILL (`List available iterations`). Present to user and ask which iteration to assign. If confirmed, set Iteration field for each item (including Epic) using github-projects SKILL.

### Check for existing issues before creating
`gh issue list -R {REPO} --search "E{n} T-{nn}" --json number`

## Step 7: Annotate TASKS file + update Epic body
Update each task heading: `## T-01: Description [ ] (#67)`

Clean up Epic issue body if it still has a placeholder task list:
```bash
gh issue edit {EPIC_NR} -R {REPO} --body "$(cat <<'EOF'
## Goal
{goal}

## Scope
See `docs/epics/E{n}-TASKS.md` for full task breakdown.
EOF
)"
```

## Step 8: Commit & Push
```bash
git add docs/epics/E{n}-TASKS.md TASKS.md
git commit -m "chore(docs): plan E{n} — add TASKS file and index entry"
git push
```

## Rules
- Every task must be self-contained enough for an agent to implement without extra context
- Ask when multiple valid approaches exist — do not decide silently
- Plain records/DTOs without logic: note "tested indirectly through T-XX"
- If `gh` commands fail, log and continue — TASKS file is source of truth

## Output Format
- Write tasks to `docs/epics/E{n}-TASKS.md`
- Status markers: `[ ]` planned · `[~]` in progress · `[x]` done · `[!]` blocked
- Update `TASKS.md` root index: add one line for the new epic
- Report created issue URLs to the user
