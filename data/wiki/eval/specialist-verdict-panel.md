---
title: Specialist Verdict Panel
tags: [eval, pattern]
summary: "Agent-output eval as a panel of single-dimension specialist judges — relevance, hallucination, completeness, escalation — each returning a structured verdict, so dimensions aggregate without a halo effect and each failure is attributable."
updated: 2026-10-30
sources:
  - data/raw/articles/2026-07-19-langfuse-multi-agent-eval.md
  - data/raw/articles/2026-07-19-evaluating-ai-agents-deeplearning.md
---

# Specialist Verdict Panel

Instead of one judge prompt asking "was this a good answer?", an orchestrator fans the
(query, retrieved docs, response) triple out to specialists that each check **one**
dimension and return a **structured verdict**, not free-text critique. Built in a personal
Langfuse hallucination-analysis project; the same separation is the "add structure to
evaluations" step of the agent-eval course sequence.

```
Orchestrator → [Document Relevance, Hallucination Detector,
                Completeness Checker, Escalation Validator] → aggregate
```

## The four specialists

| Specialist | Question | Output shape |
|---|---|---|
| **Document relevance** | Were the retrieved documents relevant to the query? | per-doc verdict |
| **Hallucination detector** | Is each claim supported by the provided sources? | `{claim, source_support, verdict, confidence}` per claim |
| **Completeness checker** | Does the response address every required information element? | per-element score → `completeness_ratio` |
| **Escalation validator** | Did the agent hand off to a human exactly when it should have? | routing verdict |

## Why split the dimensions

- **No halo effect.** A single score lets one strong dimension mask a weak one. Scored
  independently, "high helpfulness / low safety" is visible as a trade-off instead of
  averaging to "fine".
- **The dimensions are orthogonal.** A response can be factually correct but incomplete
  (omitted a required field), or complete but hallucinated (covered every element with
  invented facts). One judge conflates these.
- **Mechanism over intuition.** The hallucination specialist checks citations — is this
  claim grounded in the given document — rather than semantic similarity or the judge's
  sense of plausibility (see [[Grounding Claim Methodology]]).
- **Structured verdicts aggregate.** Fixed schemas can be summed, thresholded, and
  trended; prose critiques cannot.

## Escalation is asymmetric

Escalation accuracy is a routing eval for the human-handoff decision, and its errors are
not symmetric: a missed escalation (agent kept going when it should have handed off) is
usually costlier than an unnecessary one. Weight or gate the two error directions
separately rather than reporting one accuracy number.

## Where it sits

The panel is the judge layer of [[LLM-as-Judge Evaluation]] decomposed along the same lines
as [[Decompose Low-Ceiling Dimensions into Checkable Sub-Signals]]. It complements, not
replaces, routing and path checks: router evals (was the right tool chosen?) and trajectory
evals (was the path acceptable?) from [[Trajectory Over Outcome]] catch failures a
final-answer panel cannot see.

## See Also
- [[LLM-as-Judge Evaluation]] — extends (one judge split into single-dimension specialists)
- [[Trajectory Over Outcome]] — related (path and routing evals the panel does not cover)
- [[Grounding Claim Methodology]] — related (claim-level citation checking)
- [[Decompose Low-Ceiling Dimensions into Checkable Sub-Signals]] — instance-of
- [[Langfuse Platform]] — related (where the verdicts are attached as scores)
