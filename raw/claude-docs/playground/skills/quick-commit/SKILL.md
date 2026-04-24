---
name: quick-commit
description: "Create a feature branch, stage changes, and commit — without opening a PR."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash
---

Create a feature branch and commit current changes.

`$ARGUMENTS` — required. Format: `<slug> [commit message]`

## Branch naming

- If current branch matches `feature/lin-{id}-*` → carry ID: `feature/lin-{id}-<slug>`
- Otherwise → `feature/<slug>`

## Flow

1. `git status` — if tree is clean, stop
2. Create/switch to branch: `git checkout -b feature/<slug>`
3. `git branch --show-current` — extract ticket ID (e.g. `LIN-123` from `feature/LIN-123-desc`)
4. List files to stage (`git diff --name-only` + `git diff --cached --name-only`)
5. Skip: `.env`, `*.pem`, `models/*.pkl`, files >10 MB
6. Show file list → ask **"Stage these files and commit? (y/n)"**
7. Commit message in **Conventional Commits** format:
   - `<type>(<ticket>): <description>` — e.g. `feat(LIN-123): add invoice export`
   - Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `style`, `test`, `perf`, `ci`, `build`
   - If `$ARGUMENTS` provided, use as description; infer type from diff
   - If no ticket ID in branch, omit parenthetical: `feat: add invoice export`

## Safety

- Never force-push or amend published commits
- Never skip hooks (`--no-verify`)
- Never commit secrets or large binaries

To push and open a PR: `/quick-pr`.
