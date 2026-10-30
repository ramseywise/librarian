---
title: Three-Band Confidence Routing
tags: [infra, eval, pattern]
summary: "Turning a model score into one of three actions (auto-allow, human or stronger-model review, auto-act) with two thresholds set per category from the cost of each error type, instead of one global cutoff — the shared decision layer under moderation, document extraction and fraud scoring."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--content-moderation.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--document-processing.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--fraud-detection.md
---

# Three-Band Confidence Routing

A classifier or extractor gives a score. A single threshold turns that into a binary
decision and forces every borderline item into the wrong bucket. Three-band routing uses
**two** thresholds:

- **below the low threshold**: auto-allow or auto-accept
- **between the thresholds**: escalate to a stronger, costlier model or a human queue (in payments, step-up authentication)
- **above the high threshold**: auto-act (block, remove, decline)

The middle band buys precision without giving up recall. Because the expensive reviewer
only sees the uncertain slice, the cheap first stage can run on all traffic.

## How the thresholds are set

- **From error costs, per category.** For a high-harm category, bias toward recall and
  accept false positives. For subjective categories, bias toward precision to avoid
  over-blocking. For identity or financial fields, set the auto-accept bar near 100%.
  Thresholds also vary by surface, region, or transaction amount.
- **As a business decision.** In fraud scoring, "block above 0.7" is a policy choice, not a
  model output. During an active attack you can lower the review threshold temporarily,
  trading reviewer throughput for safety.
- **Thresholds move, models stay.** When policy changes, re-tune the handoff thresholds
  instead of relabelling and retraining.

## What the score is made of

The input does not have to be one model probability. Document extraction combines per-field
extractor confidence with OCR confidence, and **any business-rule failure forces the item
into the middle band** whatever its score (non-numeric income, an expired ID, a name that
differs across documents). Unknown document types go to a human first. Bounded retries
(about three) end in review, not in silent failure. Treat a "confidence" field with
suspicion before using it as a threshold: see [[Confidence That Is Not a Probability]].

## Monitoring that keeps it honest

- The **reviewer override rate** shows whether thresholds are calibrated.
- The **escalation rate** is the cost driver. A high-threshold band that is too wide floods reviewers.
- **Queue depth**: when the human queue backs up, auto-act on the high-confidence cases. For
  latency-critical pre-publish checks, let borderline items through to async review rather
  than block.
- **Appeal-overturn rate per group**: detects unfair over-blocking.
- Every human verdict is a **label**, fed back to retrain and recalibrate the first stage.

## See Also
- [[AI System Design Walkthroughs]] — instance-of (moderation, extraction and fraud all use it)
- [[Confidence That Is Not a Probability]] — prerequisite-for (check the score before thresholding it)
- [[Provenance-Tiered Confidence Gate]] — alternative-to (tiers derived from which source answered, not from a score)
- [[Security and Safety Interview Study Guide]] — extends
- [[Borderline-Band Sufficiency Probe]] — instance-of (the same two-threshold band applied to retrieval sufficiency, with a cheap LLM as the middle-band reviewer)
