---
name: execute-tasks
description: Execute planned tasks from TASKS.md. Use when the user asks to implement tasks, work through a milestone, or says things like "führe die Tasks aus", "arbeite TASKS.md ab", or "implementiere M1".
model: sonnet
---

Always follow the rules given by /.claude/skills/backend/SKILL.md and /.claude/skills/frontend/SKILL.md.

Execute all planned (`[ ]`) tasks from the milestone's task file. Follow this process strictly.

**GitHub Projects sync:** Use the github-projects SKILL for all GraphQL templates and configuration variables.

## Task File Location
Tasks are stored per epic in `docs/epics/{EPIC_ID}-TASKS.md` (e.g. `docs/epics/E12-TASKS.md`).
Legacy milestones M0–M11 use `docs/milestones/{MILESTONE_ID}-TASKS.md`.
The project-root `TASKS.md` is an index only — do not read tasks from it.

## Input
- Determine the milestone from $ARGUMENTS (e.g. "M10") or ask if not specified
- Read the TASKS file to identify all tasks with status `[ ]` (planned) or `[~]` (in progress)
- If $ARGUMENTS specifies a task ID (e.g. "T-05"), focus on that task only
- If a task is `[!]` blocked, skip it and note the blocker

## Step 1: Preparation
Before writing any code:
- Read the TASKS file fully — understand dependencies, acceptance criteria, and test requirements
- Load all applicable SKILL.md files (`/backend`, `/frontend`, etc.)
- Identify which tasks are independent and can run in parallel
- Mark tasks you are about to start as `[~]` in the TASKS file immediately and commit directly
- **GitHub sync (best-effort):** Update the corresponding issue to "In Progress" using the two-step pattern from the github-projects SKILL (get item ID via repository query, then set status to `{STATUS_IN_PROGRESS}`)

## Step 2: Codebase Analysis
Use an Explore agent to read all files affected by the planned tasks:
- Existing implementations that will be modified
- Existing test classes that will be updated
- Patterns and conventions used in adjacent code

## Step 3: Conflict Check
Before implementing, verify:
- Do any tasks require dependencies or patterns that SKILL.md files forbid?
- Do tasks conflict with rules in `CLAUDE.md` or `src/CLAUDE.md`?
- If conflicts exist, **stop and present them to the user** — do not silently resolve them

## Step 4: Implementation

### Git Workflow — Trunk-Based Development

| Condition | Workflow |
|-----------|----------|
| Single task or sequential tasks | Commit directly to `main` |
| Multiple independent task groups run **in parallel** | Each group gets its own worktree |

#### Direct Commit (default)
1. Implement on `main`, commit immediately after completion
2. **Push immediately: `git push`** — triggers `Closes #NN` processing; GitHub Projects automation sets Status → Done
3. Continue with the next task

#### Parallel Execution with Worktrees
1. Create worktrees: `git worktree add .claude/worktrees/worktree-<name> -b <temp-branch-name>`
2. Each subagent works in its own worktree — no shared file modifications
3. After completion: `git checkout main && git merge --ff-only <temp-branch>`
4. Clean up: `git worktree remove .claude/worktrees/worktree-<name> && git branch -d <temp-branch-name>`
5. Merge order follows the dependency graph; escalate conflicts to the user

### TDD Order
Tasks specifying TDD must follow: (1) failing test → (2) implementation → (3) mark `[x]`

### Parallelization
- Use subagents for tasks with no mutual dependencies
- Each subagent receives full context: file contents, SKILL.md rules, acceptance criteria
- Never have two subagents modify the same file simultaneously
- Each subagent updates only its own issues — no cross-agent updates

### Per-Task Completion
1. Verify all acceptance criteria are met
2. Update task status to `[x]` in the TASKS file
3. Commit with the format below
4. **Push: `git push`** — `Closes #NN` only takes effect on GitHub after push

## Step 5: Verification
- Run `./gradlew compileJava compileTestJava` — must succeed with zero errors
- Run `./gradlew test` for affected test classes if possible
- Confirm every completed task has `[x]` status; report remaining `[ ]` or `[!]` tasks

## Step 6: Roadmap & GitHub Sync
If all tasks are complete:
1. **Close the GitHub Milestone:**
   ```bash
   gh api repos/{REPO}/milestones/{milestone_number} --method PATCH -f state=closed
   ```
   Find milestone number: `gh api repos/{REPO}/milestones --jq '.[] | {number, title}'`
2. **Convert ROADMAP.md**: Replace "Scope" subsections with "Delivered" (past tense, factual)
3. **Mark superseded ADRs**: Find "supersedes ADR-XX" references → mark old entry `~~ADR-XX~~` — only when replacement is implemented
4. **Commit:** `chore(docs): close {EPIC_ID} epic in ROADMAP — convert Scope to Delivered`

## Commit Rules
```
feat|fix|refactor|chore(scope): <gitmoji> short description

Body explaining why.

Closes #<task-issue-number>
Epic: #<epic-issue-number>
```
- `scope` = BC or module name, not a ticket number
- Extract issue numbers from the TASKS file: heading `## T-XX: ... [ ] (#NN)` and `**Epic Issue:** #YY`
- Always append `Co-Authored-By` header for the executing model
- Never commit generated files, build artifacts, or `.env` files

## Handling the Usage Limit
1. Update TASKS file: completed → `[x]`, current → `[~]`
2. Commit all completed work
3. Resume in the same conversation with `/execute-tasks` — context and TASKS.md state allow seamless continuation

## Rules
- Never skip acceptance criteria — if unverifiable, note why
- Never silently change scope; ask first
- For `build.gradle` changes, ask the user (project rule from CLAUDE.md)
- If `gh` commands fail, log warning and continue — TASKS file is source of truth
- If a task heading lacks `(#NN)`: `gh issue list -R {REPO} --search "{EPIC_ID} T-{nn}" --json number`
