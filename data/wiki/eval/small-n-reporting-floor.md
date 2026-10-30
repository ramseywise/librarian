---
title: Small-N Reporting Floor
tags: [eval, pattern]
summary: "A baseline report over human labels whose N is unknown at design time must never print a confident-looking rate from a small sample: every rate carries its N, buckets under 30 print raw counts only, totals under 100 get a fixed INSUFFICIENT-N banner (exit 0, it is a report, not a gate), and a before/after delta is computed only when both runs clear the same floor on the same population."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis357-qc-baseline-fixes.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis357-qc-baseline-fixes.md
---

# Small-N Reporting Floor

From an akira plan that set out to measure an LLM publish gate against human labels for
the first time. It is the measurement step of [[Single-Call LLM Gate Weakness Audit]]. The
plan author had no database access and could not know how many labelled items existed.
So the plan fixed the reporting rules up front, before any number was produced.

## The rules

| Condition | What the report prints |
|---|---|
| Any rate | Always with its N: confusion cells, false-accept, false-block, per-slice. Never a bare percentage. |
| Bucket N < 30 | Raw counts only (`3/9 unusable→auto_accepted`). No percentage, no interval. |
| Total N < 100 | Runs and reports honestly, plus a fixed banner: `INSUFFICIENT N (<100) — do not treat this as a measured rate; label more via <queue> before using this number in a decision.` |
| Total N ≥ 100 | Wilson interval, still labelled with N. |

The CLI **exits 0 regardless**. It is a report, not a gate, and the metric it feeds stays
UNGATED either way (see [[UNGATED Metric Convention]]). A small sample does not block
progress. It only downgrades the claim.

## Deltas need the same population

The fix stage added a deterministic precheck that short-circuits some items before the
model call. After the fixes, the eligible sample for the model therefore shrinks. The rule:
a before/after delta is meaningful only if both runs clear the same N floor. If the
population changed, print both N's side by side and compute no delta across them.
Otherwise an improvement can be nothing more than having removed the easy rejects from
the denominator. This is the same trap as [[Measurement Fix Mistaken for Model Gain]].

## Record of a real run

Every operator-run spend step records N, date, model and prompt hash. A number without
that record is never merged as a claimed result. The plan also puts the baseline *before*
any logic change. It enforces this through commit order, not code dependency, so a
reviewer can see why each fix was made.

## See Also
- [[Binary Gate Sample Power]] — extends (what N can detect; this is how to print what N measured)
- [[Single-Call LLM Gate Weakness Audit]] — part-of (the baseline step of that audit)
- [[Measurement Fix Mistaken for Model Gain]] — related (deltas across changed populations)
- [[UNGATED Metric Convention]] — related
- [[Eval Error Bars and Sample Size]] — extends
