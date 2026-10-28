---
title: Name-Only Sync Guards Miss Content Drift
tags: [infra, pattern]
summary: "A vendoring sync whose guard only checks that listed names exist upstream is blind to everything that actually breaks downstream — machine-local paths in content, orphaned dirs, referenced-but-unvendored dependencies, stale indexes — and a sync that silently repairs instead of reporting gives CI nothing to fail on; add content checks and a --check mode."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-08-05-workflow-and-graph-capabilities.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-08-05-workflow-and-graph-capabilities.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-89-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-89-plan.md
---

# Name-Only Sync Guards Miss Content Drift

A project template vendors global Claude Code skills, agents, and rules into every
scaffolded project, because a rendered project cannot reach the maintainer's `~/.claude/`.
A one-way script copies them in (`rm -rf; cp -R`, whole directories, no path rewriting).
After an earlier incident it gained a hard-fail guard: every name in the
`SKILLS[]`/`AGENTS[]`/`RULES[]` lists must exist in the reservoir.

An audit measured what that guard could and could not see.

## What the guard checked

Only that the **names listed** existed upstream. Nothing about content, nothing about the
reverse direction, and nothing about names that skill bodies *reference*.

## What it missed (all shipping to every scaffold)

- **Machine-local absolute paths in content.** Vendored skills referenced
  `~/workspace/<repo>` checkouts and `--project` absolute paths. These failed at
  invocation time in a rendered project on someone else's machine. A planned change to
  make two global skills shell out to a sibling repo's CLI would have added load-bearing
  calls to a class of reference that was already shipping.
- **Orphans.** A vendored skill dir whose reservoir copy had been merged into another
  skill weeks earlier still shipped. Nothing detected a directory that the reservoir no
  longer had, and the cleanup list for the "no global skills" profile missed it too.
- **Referenced-but-unvendored dependencies.** A research skill dispatched
  `subagent_type: plan-research-scout`, an agent that was never in `AGENTS[]`, so its
  fan-out mode was broken in every scaffold.
- **An index wrong in both directions.** The vendored skills README listed 17 skills that
  did not exist (pre-rename names) and omitted 16 that did.
- **Plain content drift.** 4 of 22 synced skills had fallen behind the reservoir within
  about two days. One vendored instruction now produced wrong output (double-dated report
  filenames). Detection required a human to run the script by hand.

## Why it stayed silent

- **A plain run repairs instead of reporting.** The script's only flag was `--dry-run`. A
  normal run overwrote the drift, so there was never an artifact saying "these were
  stale". CI had nothing to fail on. It needs a `--check` mode that exits non-zero on
  drift and runs against the vendored copies.
- **A permanent false positive trains people to ignore the channel.** An issue about a
  spurious reconciliation warning was closed with no code change. The warning kept firing
  on every dry-run, which conditioned reviewers to skip the one output that would flag a
  real skew. See [[Always-Red Check Carries No Signal]].
- **Hard-failing on a pre-existing bug blocks unrelated work.** Later, an unrelated change
  needed one new reference file synced. The script hard-failed on a *clean tree*: a listed
  skill existed only in the template, never in the reservoir. The check ran before any
  copying, so nothing synced at all.
- **Wholesale vendoring smuggles in unrelated diffs.** Once that was fixed, the sync swept
  ten other drifted skills into the branch. The reviewer had to read them as unrelated
  noise in a feature PR.

## The fix shape

- A **content-level deny pattern** for machine-local absolute paths in vendored files.
  This is the cheapest honest content check.
- **Orphan detection.** Vendored dirs with no reservoir counterpart and no allow-list
  entry fail the check.
- **Referenced-name validation.** `subagent_type:` and similar references in skill bodies
  must resolve to something vendored.
- A **`--check` mode** for CI, and a **regenerated index** instead of a hand-maintained
  one.
- **Fix the known false-positive warning** so the channel means something again.

## See Also
- [[Sync as Render, Not Copy]] — extends (what the sync should transform; this page is what its guard must check)
- [[Always-Red Check Carries No Signal]] — instance-of (the permanent false-positive warning)
- [[Silence Reads as Clean]] — instance-of (repair-without-report leaves no failure to see)
- [[Template Only Decided Patterns]] — related (the HOLD research that commissioned the audit)
- [[AI Project Template Scaffold]] — instance-of
- [[Freshness Key Blind to Content Semantics]] — related (an index rebuild check blind to what the builder writes)
