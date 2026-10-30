---
title: Veto Rubric Items
tags: [eval, llm, pattern]
summary: "A must-pass rubric item that zeroes the total when it fires — hallucination is the classic one — inside a hybrid scoring scheme of must-pass gates plus a weighted remainder, so fluency cannot buy off a fabricated fact and keyword stuffing cannot pad past it."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--04-graders.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
---

# Veto Rubric Items

When a task has several graders, decide up front how they combine:

| Scheme | Rule | Use when |
|---|---|---|
| **Binary (all-pass)** | Every grader must pass | Any failure is unacceptable (safety, format, policy) |
| **Weighted** | Weighted sum clears a threshold | Dimensions legitimately trade off |
| **Hybrid** | Must-pass gates + weighted score on the rest | Most production systems |
| **Report separately** | No composite | Diagnosis — always alongside any composite |

Hybrid example: *schema valid AND no citation hallucination AND (0.5 × grounding + 0.3 ×
completeness + 0.2 × relevance ≥ 0.75)*.

## The veto

A must-pass gate on a *quality* dimension is a **veto item**: if it fires, the total is zero.
Hallucination is the classic case because it is orthogonal to quality — a fluent, detailed,
polite answer with a made-up fact does more harm than a terse correct one. A veto also blocks
reward hacking by keyword stuffing: no amount of padding scores past it.

```yaml
- id: hallucination
  criterion: Every fact in the reply appears in a tool output
  weight: veto        # fires → total score is 0
```

## Four rules for a rubric

From Li (*AI Agents in Depth*, ch. 6), following Scale AI's *Rubrics as Rewards*:

1. **Expert-grounded** — encodes domain facts and reasoning steps, not surface features like
   fluency.
2. **Covers pitfalls** — names the high-risk common errors, not only what good looks like
   (compare [[Answer Criteria with Named Wrong Answers]]).
3. **Weighted by importance** — Essential, Important, Optional or Pitfall; Pitfall items can
   veto.
4. **Self-contained** — checkable without the grader's own expertise ("cites at least two
   named sources and says how each supports the conclusion", not "shows deep
   understanding").

A rubric improves through use: grader disagreements turn it from principles into a casebook
of edge cases.

## Never let a composite hide a regression

+5 relevance and −5 grounding scores flat on a composite and is worse for users who need
correct answers. Report the dimensions alongside any composite; per-dimension gating is the
same reason the [[Specialist Verdict Panel]] keeps judges separate.

## See Also
- [[Grader States (Heuristic, Calibrated, Experimental)]] — related (which graders may hold a veto in a release gate)
- [[Answer Criteria with Named Wrong Answers]] — instance-of (pitfall items written per topic)
- [[Specialist Verdict Panel]] — complements (dimensions reported separately)
- [[Reward Hacking and Overoptimization]] — related (the veto as an anti-hacking device)
- [[Eval Harness Anatomy]] — extends (scoring design)
