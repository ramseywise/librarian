# Git Workflows — Team Cheat Sheet

Quick reference for day-to-day git on this project. Assumes GitHub + Linear issue tracking.

---

## Branch naming

Always branch from an up-to-date `main`.

```bash
git switch main && git pull
git switch -c feature/LIN-123-short-description
```

Pattern: `<type>/LIN-<id>-<slug>`
Types: `feature/`, `fix/`, `chore/`, `refactor/`

The `LIN-<id>` is required — it auto-links the branch to the Linear ticket.

---

## Commit style

```
feat(LIN-123): add invoice routing to support agent
```

- **Types:** `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `ci`
- Title under 60 chars, imperative mood ("add" not "added")
- Body: *why*, not what — the diff already shows what changed

---

## Keeping your branch current (rebase, not merge)

Prefer rebase over merge to keep history linear and PRs easy to read.

```bash
# Update your branch with latest main
git fetch origin
git rebase origin/main

# If conflicts arise, resolve each file, then:
git add <resolved-file>
git rebase --continue

# Bail out if it gets messy
git rebase --abort
```

Never rebase a branch that others are already working on — rewriting shared history causes pain.

---

## Resolving merge conflicts

When git stops with a conflict, the file looks like:

```
<<<<<<< HEAD          ← your changes
your version
=======
their version
>>>>>>> origin/main   ← incoming changes
```

Steps:
1. Edit the file to the correct final state (remove all `<<<<`, `====`, `>>>>` markers)
2. `git add <file>`
3. `git rebase --continue` (or `git merge --continue` if merging)

Useful flags:
- `git checkout --ours <file>` — take your version wholesale
- `git checkout --theirs <file>` — take incoming version wholesale
- `git diff --merge` — show the full 3-way diff while in conflict state

---

## Pull requests

- One logical change per PR — easier to review, easier to revert
- Draft PR early if you want early feedback; mark ready when tests pass
- Title must include `LIN-<id>`: `feat(LIN-123): add invoice routing`
- Squash commits on merge to keep `main` history clean

---

## Undoing things

| Situation | Command |
|-----------|---------|
| Unstage a file | `git restore --staged <file>` |
| Discard local edits to a file | `git restore <file>` |
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` |
| Undo last commit, keep changes unstaged | `git reset HEAD~1` |
| Completely discard last commit | `git reset --hard HEAD~1` ⚠️ irreversible |
| Find a lost commit | `git reflog` — everything is in here |
| Revert a commit already on main | `git revert <sha>` — creates a new undo commit, safe for shared branches |

---

## Stashing work-in-progress

```bash
git stash            # save current WIP
git stash pop        # restore it
git stash list       # see all stashes
git stash drop       # discard top stash
```

Useful when you need to pull or switch branches mid-task without committing noise.

---

## Checking what you're about to push

```bash
git log origin/main..HEAD          # commits not yet on main
git diff origin/main..HEAD         # full diff
git diff origin/main..HEAD --stat  # file summary only
```

---

## Interactive rebase (cleaning up before a PR)

Squash, reorder, or reword commits before your PR goes up for review.

```bash
git rebase -i origin/main
```

In the editor:
- `pick` — keep as-is
- `squash` / `s` — fold into previous commit
- `reword` / `r` — keep commit, edit message
- `drop` — delete the commit entirely

Only do this on your own branch before others have pulled it.

---

## Common mistakes

**"I committed to main by accident"**
```bash
git reset HEAD~1          # undo commit, keep changes
git switch -c fix/LIN-xxx-my-fix
```

**"I pushed sensitive data"**
Contact a maintainer immediately — `git rm` alone is not enough once something is pushed.

**"My rebase has dozens of conflicts"**
Stop, abort, and talk to whoever owns the conflicting code. A merge might be more appropriate. `git rebase --abort` restores you to where you started.
