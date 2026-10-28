---
title: Confidence That Is Not a Probability
tags: [patterns, eval, pattern]
summary: A field named "confidence" is often a status lookup dressed as a float; calibration (ECE/Brier) needs three things that are usually missing — a real probability, a reader that acts on it, and independent correctness labels — so check all three before building escalation or a calibration gate on it.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-25-dis238-confidence-calibration.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-25-dis238-confidence-calibration.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-25-dis238-confidence-calibration.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dsk-238-probe-confidence-calibration.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dsk-238-probe-confidence-calibration.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dsk-238-probe-confidence-calibration.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dsk-238-probe-confidence-calibration.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dsk-238-probe-confidence-calibration.md
---

# Confidence That Is Not a Probability

Found while researching an issue titled "calibrate the confidence score" in an
events-discovery product (repo akira, 2026-09). The issue assumed a probability existed
to calibrate. It did not.

## What the "confidence" actually was

A ranking trust score had a component weighted 0.15 and named confidence. Reading the
code showed it was a **fixed lookup on a 3–4 value `enrichment_status`**, with no model
probability anywhere in it. An ECE or Brier curve over it is meaningless: with four
possible values, the only real question is ordinal ("is this ranking of statuses
right?"). The research called it **a status string dressed as a float**.

Every reader was then traced. Nothing downstream used the scalar as a decision signal;
the observability readers only logged it.

## Calibration needs three things

1. **A real probability.** A model-emitted per-item confidence, or a score with a
   probabilistic meaning. An ordinal bucket doesn't qualify.
2. **A reader that acts on it.** Calibrating a number nobody reads changes nothing (see
   [[Every Column Names Its Reader]]).
3. **Independent correctness labels.** The `{confidence, correct}` pairs need a
   `correct` that doesn't come from the same model call.

The repo already had a generic `calibration()` function that computed ECE, Brier and
reliability bins from `{confidence, correct}[]`. That was a REUSE verdict (see
[[REUSE/ADAPT/SKIP Asset Verdicts]]). The arithmetic was never the blocker. The pairs
were.

## The proxy that is allowed, and how to register it

The closest real probability was the venue probe's per-tag `confidence`. Its only
available "label" was the same call's own `evidence_sufficient` bit (104 true / 95
false / 1 null of 200). Both are self-reports from one model call, so they are
correlated, not independent. That is mechanical rather than circular in the
[[UNGATED Metric Convention]] own-oracle sense, but it still doesn't measure accuracy.
The honest move is to **register it UNGATED**, following the precedent of the existing
probe-mechanics metrics, and label it as a proxy agreement rate rather than a
calibration result.

## Consequence for escalation

Two open issues ("escalate on low confidence", model tiering) both assumed a number worth
escalating on. Escalation built on the trust score would escalate on a status string.
Escalation built on the probe's per-tag confidence would escalate on an uncalibrated
self-report. **"Low confidence → escalate" is unsafe until the confidence is calibrated
against independent labels.** It also matches the enrichment contract's position that a
public per-field confidence is noise (see [[Graded-Uncertainty Enrichment Contract]]).

## Checklist before any "calibrate X" work

- Open the code that computes X. Is it a probability or a lookup?
- `grep` every reader. Does anything branch on it?
- Where would `correct` come from? If it's the same call, the metric is UNGATED.

## As built: calibrating the probe's tag confidence

- **Grade what the model emitted.** Calibration used the raw pre-filter tags (982), not
  the 782 that survived the confidence filter. Grading only survivors measures the
  filter, not the model.
- **One eval case per bin.** Ten bins, one EvalCase each, so the report reads as a
  reliability curve rather than one pass/fail number.
- `isCorrect` passes a bin when its accuracy is within 0.15 of its mean confidence.
  **Empty bins never default-pass.**
- Results: ECE 0.106, Brier 0.130. Three bins pass, four fail, three are empty. The
  caveat (small, single-labeller sample) is stated in three places: the report, the
  metric registration and the plan.
- **The label queue was blocked, not built.** The only UI that wrote per-field reviews
  had been removed, so a bare migration would have added a column with no reader.
- A premise-drift check against the spec docs found nothing needing correction.

## See Also
- [[Graded-Uncertainty Enrichment Contract]] — extends (why numeric per-field confidence was kept off the public contract)
- [[UNGATED Metric Convention]] — instance-of (a self-report vs self-report proxy stays ungated)
- [[LLM Grader Calibration Insights]] — related (calibrating a judge against humans is the labelled version of this)
- [[Write-Only Fields and the Reader Map]] — related (a scalar no reader branches on)
- [[Kiez Project]] — instance-of
- [[Provenance-Tiered Confidence Gate]] — instance-of (a status-lookup tier that is honest about being one, with a real reader)
- [[Calibrated Score, Deterministic Decision Rule]] — extends (calibration is required when a cost threshold consumes the score)
- [[Borderline-Band Sufficiency Probe]] — extends (routing on uncalibrated retrieval scores without trusting raw thresholds)
- [[Hedging Belongs in the Gate, Not the Answer]] — related (where low confidence should surface)
- [[Single-Call LLM Gate Weakness Audit]] — prerequisite-for (decorative confidence as one of seven gate weaknesses)
