---
title: Shadow Signal Before Gate Change
tags: [llm, infra, pattern]
summary: Before changing what a skip-or-run gate keys on, compute the proposed key alongside the live one as a non-gating shadow (here `computeContentHashExcludingDates` next to the real content hash) and log where they disagree — so the decision to change the gate is made on counted evidence, and a plan step that is conditional on an undecided question is marked BLOCKED, not quietly deferred, because a decision-conditional step is not dispatchable.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis281-stage2-schedule-gate-decision.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis281-stage2-schedule-gate-decision.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis281-stage2-schedule-gate-decision.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis281-schedule-only-rehash.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis281-schedule-only-rehash.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis281-schedule-only-rehash.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis281-schedule-only-rehash.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis281-schedule-only-rehash.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis281-stage2b-schedule-sensitivity-eval.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis234-yorck-dryrun-and-b85-reenable.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis234-yorck-dryrun-and-b85-reenable.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis234-yorck-dryrun-and-b85-reenable.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis234-yorck-dryrun-and-b85-reenable.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis234-yorck-dryrun-and-b85-reenable.md
---

# Shadow Signal Before Gate Change

An enrichment pipeline skipped the model call when a row's content hash was unchanged
(see [[Spend Gate Before the Model Call]]). The open question was whether schedule
fields — dates that change on every re-crawl of a recurring event — should be excluded
from the hash, so that a date-only change no longer triggers a paid re-enrichment.

## The move

Rather than argue the hash definition, the plan added a **second, non-gating hash** that
excluded the date fields, computed it beside the live one, and logged rows where the two
disagreed. (The shadow is log-only. It is not persisted as a column; see Stage 1 below.) The live gate kept deciding; the shadow only recorded. After a run, the
question "how many re-enrichments were date-only?" has a number instead of an estimate,
and the gate change — if made — is justified by that number.

Two details that mattered:

- **A null hash fails open.** A row with no stored hash must re-enrich, never skip. The
  schema audit had already found one check that failed *closed* and one that failed
  *open* on a missing column; here the safe direction is explicit.
- **The shadow is cheap to remove.** One function and a log line, no stored column, no reader except the
  count. If the decision goes the other way nothing has to be unwound.

## BLOCKED, not deferred

The plan's step that would actually change the gate depended on the decision the shadow
exists to inform. The plan marked that step **BLOCKED** on the decision rather than
"deferred" or "optional". The distinction: a deferred step has a trigger and will be
picked up; a step conditional on an undecided question **is not dispatchable** — an
agent handed it has nothing to execute and will either invent the decision or stall.
Naming it BLOCKED keeps it out of the build queue until a human decides.

## Stage 1: what the shadow needed before its numbers meant anything

Shipping the shadow hash (akira DIS-281 stage 1) turned up conditions that decide whether
its log can answer the question at all:

- **Exclude the derived copies too.** The date fields had copies elsewhere in the hashed
  payload: raw date text, raw time text, and a free-text schedule string. With only the
  structured dates excluded, the shadow still changed on every date-only edit, and the
  "date-only" ratio would have read about 0% forever. A golden-hash test now pins the
  exclusion list, so adding a field to the payload cannot silently re-include a date.
- **A first sighting is not a data point.** The first time a content id appears there is no
  previous shadow to compare with. Counting it as "changed" or "unchanged" skews the ratio.
- **No cron, no evidence.** The scheduled import was off, so nothing accumulated passively.
  An early ratio from manual runs only smoke-tests the logging path. It is not the decision
  input.
- **Strip ANSI codes before parsing dev logs.** Coloured dev output broke the counting regex.
  Pipe through `sed` to remove escape codes first.

## The shadow must reach every path you measure on (akira, 2026-09-22)

A later plan was asked to produce the representative ratio by running two dry-run
passes on different days. Research found that the issue's "split the hash" prerequisite
had **already shipped**: the shadow hash was computed and logged on the live path, on
every outcome, including a hash-match skip. The issue text was stale (`origin:
upstream-wrong`). The real gap was elsewhere. The **dry-run** handoff log line carried no
hash fields at all, even though the dry-run gate decision computed the hash internally
and then discarded it. The fix returned the hash from that function. It extended only
the existing `known`-row conditional, so a *new* row's dry-run line stayed
byte-identical. That invariant existed only as a code comment, not as a test.

The frequency ratio answers how often a change is date-only. Whether the output depends
on the date at all needs its own measurement: see [[Paired Input-Perturbation Eval]].

## See Also
- [[Spend Gate Before the Model Call]] — extends (how to change the gate's key safely)
- [[Deferred Decision Status]] — extends (BLOCKED-on-decision as a fourth state distinct from Deferred(trigger))
- [[Plan-Doc Status Enum]] — related
- [[Online Eval Sampling]] — related (shadow measurement that does not affect the live path)
- [[Paired Input-Perturbation Eval]] — extends (the output-sensitivity half of the same gate decision)
