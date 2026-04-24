---
name: review-pr
description: Review an open pull request against project standards and task acceptance criteria. Use when the user asks to review a PR, or when execute-tasks creates a PR for a breaking change. Triggers like "review PR #42", "prüfe den PR", or automatically after PR creation.
model: sonnet
---

Review pull request $ARGUMENTS against project standards, skill rules, and task acceptance criteria. Act as a **Senior Reviewer** — verify correctness, compliance, and completeness. Follow this process strictly.

## Input
- If $ARGUMENTS is a PR number (e.g. "42" or "#42"), use `gh pr view <number>`
- If $ARGUMENTS is a URL, extract the PR number
- If $ARGUMENTS is empty, use `gh pr list` to show open PRs and ask the user which one to review

## Step 1: Gather Context

1. Read the PR metadata: `gh pr view <number> --json title,body,headRefName,baseRefName,files`
2. Read the PR diff: `gh pr diff <number>`
3. Identify which tasks from TASKS.md this PR implements (look for T-XX references in PR body or commits)
4. Load the acceptance criteria for those tasks from TASKS.md
5. Load all applicable SKILL.md files (backend, frontend, etc.) based on changed files

## Step 2: Compliance Check

Verify the changes against:

### Project Rules (CLAUDE.md / src/CLAUDE.md)
- No forbidden patterns or dependencies
- No `build.gradle` changes without user approval
- KISS/YAGNI — no unnecessary complexity

### Skill Rules
- BCE layering correct (backend SKILL)
- Naming conventions followed
- Testing strategy aligned (correct test layer, TDD where required)
- Web component patterns correct (frontend SKILL)

### Task Acceptance Criteria
- Every acceptance criterion from TASKS.md for the referenced tasks is met
- No scope creep — changes stay within what the task specifies
- Tests exist where required and cover the specified scenarios

### Code Quality
- No security vulnerabilities (OWASP top 10)
- No leaked secrets or internal details in error responses
- Proper error handling at system boundaries
- No backwards-compatibility hacks unless explicitly required

## Step 3: Build Verification

Run verification commands if the PR is checked out locally or in a worktree:
- `./gradlew compileJava compileTestJava` — must compile
- `./gradlew test` — tests must pass
- If the PR is remote-only, check CI status: `gh pr checks <number>`

## Step 4: Decision

Based on the review, take one of these actions:

### Approve
If all checks pass:
```bash
gh pr review <number> --approve -b "LGTM. All acceptance criteria met, skill rules followed."
```

### Request Changes
If issues are found:
```bash
gh pr review <number> --request-changes -b "<structured feedback>"
```

Feedback format:
```markdown
## Review: Changes Requested

### Issues
- **[blocking]** <file:line> — <description of the issue and why it matters>
- **[blocking]** <file:line> — <description>

### Suggestions (non-blocking)
- <file:line> — <optional improvement>

### Checklist
- [ ] <specific fix needed>
- [ ] <specific fix needed>
```

### Auto-Merge (only when invoked by execute-tasks)
If approved and all CI checks pass:
```bash
gh pr merge <number> --rebase --delete-branch
```
Only auto-merge when:
1. This review was triggered automatically by execute-tasks (not a manual user request)
2. All acceptance criteria are met
3. All CI checks pass (`gh pr checks <number>` shows all green)
4. No blocking issues found

If any of these conditions fail, do NOT auto-merge — report the result instead.

## Step 5: Report

Summarize the review result to the user:
- PR title and number
- Decision (approved / changes requested)
- Key findings (blocking issues, if any)
- Merge status (merged / ready to merge / needs fixes)

## Rules
- Never approve a PR that has failing tests or compilation errors
- Never approve if acceptance criteria from TASKS.md are not met
- Be specific in feedback — reference exact files and line numbers
- Distinguish blocking issues from suggestions
- Max 3 review rounds — if issues persist after 3 rounds, escalate to the user
- Do not review your own changes without disclosing it (if execute-tasks created the PR and review-pr reviews it, note this in the review comment)
