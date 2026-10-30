---
title: Review Cursor Advances Only Past a Clean Run
tags: [infra, eval, pattern]
summary: A scheduled cross-repo review keeps, per repo, a cursor at the last default-branch commit it reviewed cleanly; each run reviews only what changed since that cursor, in a throwaway detached worktree, and moves the cursor only when the run completes — so a failed or partial run re-covers the same range next time instead of silently skipping it.
updated: 2026-10-30
sources:
  - data/raw/repos/guacamayo/CLAUDE.md
---

# Review Cursor Advances Only Past a Clean Run

The weekly portfolio sweep in guacamayo (the repo behind
[[Puffin Consciousness Development Skills]]) reviews every repo it governs. It runs on a
schedule, unattended, against repos that are also being worked on by hand.

## Mechanism

- **One list of repos.** A single `repos.toml` names each governed repo with its role,
  visibility, path and whether the sweep reviews it. The board, the hygiene script and
  the sweep all read it, so adding a repo is a one-line change. A missing clone is
  reported, never skipped.
- **Two passes.** First a read-only state pass (git and PR state). Then a review of the
  files changed on each `origin/<default>` branch since the last clean review.
- **The cursor moves only on success.** The review cursor advances only past a clean run.
  A crash, timeout or partial run leaves it where it was, so the next run reviews the
  same range again. A cursor that advanced on every attempt would turn one failed run
  into a permanent gap in coverage, with nothing to show it ([[Silence Reads as Clean]]).
- **The user's checkout is never touched.** The review runs in a throwaway detached
  worktree, so an in-progress branch, uncommitted work or a dirty index in the real
  checkout cannot affect what is reviewed, and the review cannot change them.
- **Findings are a ledger, not a report.** Output goes to a git-ignored directory (it
  covers private repos): a dated digest, a state snapshot, and a `findings.json` ledger
  whose entries are open, acknowledged (ticked by hand) or resolved.
- **The reviewer belongs to the sweep, not the target.** The review driver defaults its
  agents and skills directories to the sweeping repo's own `.claude/`, so every target
  is reviewed by the same dimensions regardless of what that repo has installed.
- **Cron mode unsets the API key**, so the scheduled run bills to the subscription plan
  through the agent SDK rather than to a metered key.

## See Also
- [[Silence Reads as Clean]] — extends (why a skipped range must not look reviewed)
- [[An Unrun Scan Is Not a Clean Scan]] — extends
- [[Parallel Dimension Scanner Architecture]] (the review that runs per repo)
