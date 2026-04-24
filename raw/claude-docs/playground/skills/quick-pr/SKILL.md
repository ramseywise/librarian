---
name: quick-pr
description: "All-in-one: stage, commit, push, open PR, resolve merge conflicts, and merge — single command end to end."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Write
---

End-to-end PR flow for the current working tree.

`$ARGUMENTS` — optional commit message. If omitted, derive from diff.

## Flow

1. **Check**: `git status` + `git diff main...HEAD --stat` — if clean and no unpushed commits, stop
2. **Commit** (if needed): list files, skip secrets/`.env`/large binaries, show list + message, confirm before `git commit`
3. **Push**: `git push -u origin HEAD` — if rejected, `git pull --rebase origin main`, resolve conflicts, retry
4. **Draft PR**: read active plan if present, write title + body per conventions below, show full content, confirm before `gh pr create`
5. **Merge** (optional): ask **"Merge now? (y/n/squash)"** → merge with `--delete-branch` or leave open

## PR conventions

- Title: Conventional Commits format, under 60 chars. Extract ticket from branch: `feat(LIN-123): description`
- Body follows `.github/pull_request_template.md`:

```markdown
## Overview
[Derive from diff: what this PR accomplishes and why]

## Related Issue(s)
- [Auto-fill from branch name: LIN-{id}, or prompt user]

## Changes Made
[Summarize from `git diff --stat` and commit messages]

## Impact
- [x] [Infer: Low/Medium/High from scope of changes]

## Priority
- [x] [Infer: Low/Medium/High from context]

## Testing
- [x] [Check applicable: unit/integration tests from test output]
- [ ] Manual testing performed

## Type of Change
- [x] [Infer from diff: New feature / Bug fix / Refactoring / Documentation update]

## Documentation
- [Check if docs were modified in diff]

## Deployment Considerations
- [Check if infra/ files were modified in diff]
```

Auto-fill what you can infer from the diff and test results. Leave unchecked boxes for the user to verify.

## Conflict resolution

`git diff --name-only --diff-filter=U` → read each → resolve → `git add` → `git rebase --continue` → retry push.

## Safety

- Never force-push or skip hooks
- Never commit `.env`, `*.pem`, `models/*.pkl`, or files >10 MB
