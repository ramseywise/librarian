---
title: Monitor the Gate, Not the Stage
tags: [eval, infra, pattern]
summary: "A pipeline meant to run unattended is safe only if every automated decision is a flag with a stored reason and a measured trust level, so the monitoring unit is the gate, not the stage: each gate shows fire rate, precision against human verdicts with n (printed `unlabelled` when there are none, never blank and never 1.0), a recall proxy from later send-backs, and drift."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-admin-dashboard-monitoring-refactor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-admin-dashboard-monitoring-refactor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-admin-dashboard-monitoring-refactor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-admin-dashboard-monitoring-refactor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-admin-dashboard-monitoring-refactor.md
---

# Monitor the Gate, Not the Stage

From a plan to rebuild an admin dashboard as end-to-end monitoring for a content
pipeline (repo akira, 2026-09-29). The pipeline was meant to run with its scheduling, QC
and publish switches all on and **no human in the loop**. The owner put the requirement
this way: "we want to automate this on these flags, so we need to see in the admin
dashboard whether they are trustworthy."

## The unit of monitoring

A stage-by-stage dashboard answers "how much came through". Unattended operation needs a
different question answered: *which automated decision stopped the rest, and can that
decision be trusted?* So each stage tab opens with a **gate table**. Every gate is a
deterministic or model **flag with a persisted reason**, and every gate carries four
numbers:

| Number | Definition |
|---|---|
| **Fire rate** | items the gate stopped ÷ items it saw, per run |
| **Precision** | of the items it stopped, the share a human agreed should be stopped, **with n** |
| **Recall proxy** | of the items it passed, the share a later gate or a human sent back (e.g. a QC "missing start date" on a row the extract gate passed) |
| **Drift** | fire rate this window vs the previous one, and vs the gate's own fixture pass rate in CI |

A gate counts as **trustworthy** at precision measured on n ≥ 30, a fire rate stable
over 10 runs, and a green heuristic grader for its rule in CI. A gate that is not yet
trustworthy may still run, but the view says which of the three it lacks. Arming
automatic publish for a content kind becomes a decision read off this table, not off a
feeling.

## `unlabelled` is a value

A gate with no human-verdict source prints **`unlabelled`** in the precision cell. It is
never blank, and it is never 1.0. On first render, 20 of 30 gates had no verdict source.
The plan treated that as the finding, not as a defect of the view. The fix that makes
those cells numbers is a sample queue: route about 10% of each unlabelled gate's drops per
week into the existing human-review table under a new subject type. The same goes for
gates with nothing persisted. Their fire-rate panel renders **"no writer"**, never 0.
See [[Silence Reads as Clean]] and [[Map Every State to Its Writer]].

## What the gate inventory surfaced

Listing every gate with its status (live / observe-only / not wired / writer needed)
turned up the gaps that stood between the flags and unattended operation. None of them
were dashboard work:

- **A gated grader guarding nothing.** The one freshness gate with a CI-gated eval had no
  production caller. Only its eval called it. (Same class as [[The Untested Copy Wins]].)
- **A classifier with no caller.** The fuzzy content-duplicate classifier existed, but
  production dedup was exact-identity only, so near-duplicates passed.
- **A hold that does not block.** The publishable-status set included "needs review". With
  publish armed, an item the enrichment gate had held would still publish. The plan did not
  change the policy, since that decision belonged to the publishing workflow. It made the
  dashboard count the rows the fix *would* have caught ("held but publishable").
- **A flag whose name lies.** The QC switch guarded one workflow step. A chained QC call in
  another workflow did not read it.
- **An observe-mode rights gate** that logged and excluded nothing. See
  [[Observe-Mode Gate With a Named Enforce Trigger]].

## One concern, several homes

The inventory also explained why "where does freshness live?" had been hard to answer.
There were three different freshness gates. Date *plausibility* sits at extraction. *Is
this worth a model call* (event over, no date) sits before enrichment. *Is the servable
pool fresh* (days of supply, expiry) sits at the catalogue. Dedup echoes the same way.
Identity is decided at extraction. A later content-hash match is the same row seen again,
a cache hit, not a duplicate. Once a concern is split by the gate that decides it, its
stage placement follows.

## Panel rules that came with it

- **A metric declares a catalogue row or it does not render.** A typed catalogue file is
  the panel contract. A test fails if a panel has no row, or if a row has neither a panel
  nor a named "no writer" state.
- **Read-only.** Six work queues (review, blocked, takedowns, QC accept/reject, candidate
  accept/reject, source registry forms) moved out to an ops surface. A page that is both a
  to-do list and a monitor is neither.
- **A time axis wherever the source has a time column.** Runs for the crawl, ISO weeks
  downstream. Where history does not exist (eval scores, κ, source health, overwritten
  columns), one append-only snapshot ledger with a fixed list of writers holds it. See
  [[A Trace Is Not a Number of Record]].
- **Every panel prints its data tier**: live, probe-loaded vN, or labels n=.
- **A "no charting library" rule is not a "no charts" rule.** For one build cycle the
  comment was read as forbidding charts, and every panel shipped as a ratio table. A bar, a
  column series and a line are each about 30 lines of server-rendered inline SVG, with a
  `<table>` twin that the component tests assert against. That keeps the page free of
  client JS, which was the rule's actual purpose.

## See Also
- [[Quality-Gate Dashboard in Pipeline Order]] — extends (the earlier stage-ordered layout; this adds per-gate trust numbers and the read-only split)
- [[Telemetry Claim Verification Gate]] — related (recompute a dashboard number before trusting it)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — extends (the trust bar a gate must meet before it enforces)
- [[Shadow Signal Before Gate Change]] — related (measure a gate before changing it)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — related (a gate's own pass rate is not its precision)
- [[Silence Reads as Clean]] — extends ("no writer" and `unlabelled` as distinct states)
- [[The Untested Copy Wins]] — instance-of (a gated rule with no production caller)
