---
title: Path-Verified Build State Markers
tags: [meta, pattern]
summary: When scoping on top of an existing codebase, every capability a source doc claims exists must be backed by a file path — BUILT (exists and tested), ABSENT, or UNVERIFIED, never an optimistic partial — because a wrong done-marker silently removes work from the plan; on greenfield the honest state is SPECIFIED.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/playground/skills/design-product/SKILL.md
  - data/raw/claude-docs/playground/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/playground/skills/design-initiative/SKILL.md
  - data/raw/claude-docs/galactus/skills/proto-scope/SKILL.md
  - data/raw/repos/akira/CLAUDE.md
  - data/raw/repos/diskoe/CLAUDE.md
  - data/raw/repos/diskoe/README.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase4-dry-run-modes.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis330-spec-staleness-pass.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis244-alternatives-expand-in-place.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis244-alternatives-expand-in-place.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis244-alternatives-expand-in-place.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis244-alternatives-expand-in-place.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis244-alternatives-expand-in-place.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis359-retention-verification.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis359-retention-verification.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis359-retention-verification.md
---

# Path-Verified Build State Markers

Step 5b of the galactus `/proto-scope` skill applies to **brownfield work only**, where a
prototype layers onto an existing codebase. For every capability a source doc claims
exists, find the file. A capability with no file path is **ABSENT**, whatever the doc says.

| Marker | Meaning |
|---|---|
| `BUILT` | Module exists **and** is tested. Never "deliverable is accepted." |
| `ABSENT` | No file found. Not partial, not yellow, absent. |
| `UNVERIFIED` | Could not verify (code without tests, ambiguous path). Never an optimistic partial. |

## Why

> "Shipped" claims decay silently; a path is the only claim the next reader can check.
> A wrong done-marker removes work from the plan — that work then never gets planned.

**Evidence (diskoe).** A PRD inherited green markers from feasibility docs written before
anyone read the code. Six of the eight were wrong. Each wrong marker was a capability the
plan would have built on and nobody would have built.

The failure is asymmetric. A false ABSENT costs a duplicate look at code that exists. A
false BUILT drops a work item out of every later stage, and nothing downstream will ever
check for it.

## Corollaries

- **Greenfield.** With no working tree, **nothing** may be marked BUILT. The honest state is
  `SPECIFIED`, and the artifact says build state could not be verified. That is not the
  same as "nothing works": the system may be running and simply not in this checkout.
- **Discovery mode.** The step doesn't apply (there is no code context yet). Write
  `N/A — discovery mode` rather than skipping silently.
- BUILT means "module exists and is tested," not "accepted." Collapsing the two is the same
  status-vocabulary failure as a roadmap row that outran its evidence.

## Partial States Must Name Their Gap

From the playground copy of the design skills: binary built/not-built cannot express the most
common outcome, where the shape shipped and the field list did not. Requirements use
`ABSENT` / `PARTIAL` / `MET`, and **`PARTIAL` is invalid unless it names the specific missing
field or unmet criterion**. Components use only `BUILT` / `BUILT, NOT WIRED` / `SPECIFIED` /
`GAP` in the State column, with nuance in a separate Note column, because prose states can't
be counted or filtered. When two registries disagree, the stricter one wins and both headers
say so; otherwise BUILT quietly means two different things in two files.

## Claims Have an Expiry; ABSENT Claims Are Rebuild Instructions (akira)

The akira repo treats every build-state row as **a claim with an expiry**. A `BUILT` row
is only as good as its last verification date, so it is re-verified and the date restated,
or marked unverified. It is never copied forward. A `make spec-staleness` report lists
every dated claim across the specs, oldest first, and marks the ones that assert a
capability is **absent**. Those come first, because a spec saying something does not exist
is an instruction to build it again. The repo did this twice: a robots.txt parser and an
instrumentation layer were both described as absent for weeks after they shipped.

The report is **deliberately not a gate**. An age-based failure would turn every document
red on the same day and be `ALLOW_`-ed away within a week. What was missing was never
enforcement; it was the list. The same repo moved its build-state table out of CLAUDE.md,
which is injected into every subagent, after it reached 31 of 79 KB. A reviewer with a
six-file diff was paying for the entire build history first.

## Reads complete, empty where it executes (galactus dry-run research)

The same class surfaced twice, unlooked-for, while locating a dry-run target: an ML
runner importing toolkit modules that existed only on an unmerged branch of another repo
(resolved through an environment variable), and a half-finished directory move where the
data extract and the walkthrough doc had moved but the source had not — leaving a
complete-looking directory whose `src/` held only `__pycache__`. Both were **structures that
read as complete to a documentation-level inspection and are empty at the level that
executes**, both were caught by nothing, and both were found by asking where things
physically are. Component tests stayed green throughout — the failure lives in composition.

## Closed Is Not Done (akira, 2026-09)

An issue tracker's open/closed state is not a build-state marker. A cost-baseline issue
blocking a model experiment showed `CLOSED` on re-check, but it had been closed by a
**triage comment** (correcting a stale number). The plan for the run it tracked was still
`Status: IN_PROGRESS` with every Definition-of-Done box unchecked. A reader trusting the
issue state would have assumed the baseline existed and quoted a cost figure from a table
still marked disputed. The marker that counts is the artifact (the run plan's status, or the
output file), not the ticket.

## "Landed" in an Issue Body Is Not a Git Fact (akira, 2026-09)

A spec-staleness issue ticked two boxes as "landed with this issue": the scanner target and
the corrected robots-parser claim. Checked against `main`, **neither was there**. The work
existed only as staged, uncommitted changes in a worktree, on a base one commit behind
`main`. The plan's first act was to uncheck both boxes on the live issue and annotate the
real state, which turned step 1 from "build the scanner" into "land this branch". The same
plan made the staleness pass explicitly **recurring**. Done-when is "the `ABSENT?` claims
older than ~14 days have been read against the tree", not "zero claims remain". A claim
marked re-verified without actually reading its cited path reproduces the bug being fixed.

## Open Is Not Unbuilt (akira, 2026-09-29)

The reverse of closed≠done: a ticket that asked for an expand-in-place alternatives row on
the result card was still open, and the work was already on `main`, with a test. `git log`
on the component showed it had landed as a side effect of a broader PR whose message never
named the ticket. Refinement turned the ticket into a status table (BUILT / BUILT
differently than specified / DELIBERATELY NOT DONE / NOT DONE), with a file:line for each
row:

- **Built differently than specified.** A native `<details>/<summary>` gives keyboard
  operation and open/closed state without the hand-rolled `aria-expanded` the ticket
  asked for.
- **Deliberately not done.** The ticket asked for interaction logging. Alternatives occupy
  no served position, so the logging contract does not apply to them. The component's
  header says so, and its rows carry no event-id attribute, so the viewport observer cannot
  pick them up either.
- **Not done.** The e2e coverage. That was the ticket's real remaining scope.

Before planning the build of an open ticket, grep the tree for its feature.

## ENFORCED Describes a Capability, Not a Run (akira, 2026-09-29)

A compliance register marked a retention workflow **ENFORCED** for storage limitation. The
code and cron existed. The cron had produced **zero real executions**: both scheduled runs
were 0-step billing failures. "ENFORCED" was describing what the system *could* do, not an
observed outcome. A register state has to name what was observed: the run, its date, and
the rows it affected. Until then it is "armed", not "enforced". See
[[Atomic Archive-Then-Delete for Irreversible Retention]] for how the first real run is
verified.

## See Also
- [[Rollback Restores Code Only]] — related (a READY plan never executed; premises re-verified at triage)
- [[Workflow Pipeline Telemetry Audit]] — instance-of (a BUILT row that outran its evidence)
- [[Scope-POC Design Interview]] — part-of (the scoping skill this step belongs to)
- [[Plan-Doc Status Enum]] — extends (status words need a checkable referent)
- [[Verified Runtime Capability Constraint]] — extends (the same "only claim what you can demonstrate" rule for controls)
- [[Re-Derive, Never Re-Read]] — extends (the same rule for ledger rows and dashboards)
- [[Reproduce to Tell a Break From a Stuck Agent]] — extends (unattended runs as the detector for this class)
