---
title: Case Study Interview Study Guide
tags: [interview, reference]
summary: "Method guide for the case-study round in its live, take-home, and defense forms — the memorized eight-section template, baseline-first and number-anchored objectives, three ROI formulas to have cold, the assumptions-first take-home writeup, and the five-step response to a defense-round challenge."
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--aie-track--one-hour-code-test.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--aie-track--rag-pipeline-defense.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--rag-pipeline-defense.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--aie-track--retail-support-automation.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--retail-support-automation.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--churn-prediction-takehome.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--case-study--examples--ml-track--churn-prediction-takehome.md
---

# Case Study Interview Study Guide

The case round bridges theory to a business problem. Four graded dimensions:
problem-solving process, applied ML/LLM knowledge, business awareness, communication.
**Process beats results** — they grade how you structure ambiguity and use the
interviewer as a resource, not whether you land their pet answer. The FDE live case is
reported as the loop's highest-weight round (~30%) with the lowest pass rate (~40%); the
DS take-home-with-presentation is near-universal. AIE/MLE loops fold case elements into
[[System Design Interview Study Guide|system design]].

| Format | Window | Graded hardest on |
|---|---|---|
| Live case | 45–75 min | clarify-first, trade-off narration |
| Code test (emerging, not canonical) | 1h | triage, shipping, API safety — see [[AIE Code-Test Flaw Taxonomy]] |
| Technical test | 1–3h | correctness, scoping, writeup |
| Work Trial | 3–6h | production-readiness ≈ feature completeness — see [[Timebox-Scaled Deliverable Bar]] |
| Presentation / defense | panel | adapting under challenge |

## The one-page template (write it from memory in 2 minutes)

1. **Objective & users** — never accept the stated solution ("a chatbot" is an answer, not
   a problem). State the objective as a number before designing: "cost per ticket $12 → $8".
2. **Constraints** — latency, cost per 1K tokens, privacy, budget. Sensitive data drives
   model hosting; say so out loud.
3. **Data sources** — what exists, what's missing (labels, feedback, ground truth), quality
   concerns stated upfront. For LLM cases the retrieval corpus is a data source.
4. **Baseline first** — heuristic or logistic regression for ML; keyword search + static FAQ
   for LLM. If the baseline handles 40% at $0/token, the LLM only needs the other 60% — the
   cost math changes. State the baseline metric before the model metric.
5. **MVP pipeline sketch** — components, not vendors; then one vendor choice justified
   ("already on Postgres → pgvector").
6. **Offline + online eval** — kept separate. Offline: labeled set, and why not the obvious
   metric (AUROC over accuracy at an 8% positive rate; faithfulness over BLEU when grounding).
   Online: leading indicator, drift detection, rollback trigger.
7. **Risks & safety** — at least three, each with a mitigation.
8. **Milestones** — phased (data audit → MVP + offline eval → shadow mode → 10% A/B → full
   rollout), ending in a **measurement close**: "success = 40% deflection with CSAT ≥ 4.1."

ML vs LLM adaptation: the LLM version swaps feature engineering for ingest → chunk → embed
→ retrieve → generate, adds token cost / rate limits / stale index / prompt injection to
risks, and requires an explicit RAG-vs-fine-tune call (RAG when knowledge is large and
changing; fine-tune when style/format is the gap).

## ROI arithmetic — have it cold

- **Token math:** queries/day × tokens/query × price. A tenfold-cheaper model turns the
  question into "what is the accuracy gap worth?"
- **Hours saved:** hours/week × loaded rate × 52 → payback period against build cost.
- **Error cost:** error rate × volume × cost per error. This is how "how good is good
  enough?" gets answered — the reduction in exposure bounds what improvement is worth.

## Trade-off narration

Name the trade-off and the condition that would flip it: "RAG because the FAQ updates
monthly; fine-tuning would mean retraining each update." "pgvector avoids a new service in
the pilot; at 10× volume a dedicated store earns its ops cost." "Small model for routing
and FAQ, escalate to the large model only for multi-document synthesis."

## Take-home writeup

Budget ~20% of the time for it — graders spend minutes on your work, and the memo *is* the
artifact. Order: **assumptions first** (they cannot penalize an assumption they didn't
correct) → objective restated as a number → what you built and why → findings, honestly →
what went wrong / data issues → **next steps / not done** (an empty one reads as believing
it's complete, which is worse). Over-scoping and burning a 48h window on a 4h task are
documented negatives. Common failures: no assumptions, no baseline, no eval story, writeup
as afterthought.

## Defense rounds

Challenge types: "why not deep learning?", "what breaks at 10×?", "why this chunking?",
"what would you cut with a week left?", "retrieval is poor — now what?", "what went wrong?".

Five-step response: acknowledge the *specific* concern → explain the original reasoning
briefly → state the conditions under which you'd change it → adapt visibly when the
challenge is valid → name what is genuinely hard.

The strongest metric defense is a **failure breakdown**: label ~100 failures and bucket them
(e.g. truncated chunks, correct chunk ranked just outside top-k, cross-chunk synthesis
errors, genuine multi-doc conflicts), then attack the cheapest lever first — which
is the same discipline as [[RAG Interview Study Guide|RAG debugging]]. Failing patterns: "great question" filler, "it depends" without
saying on what, solving a challenge by adding complexity instead of prioritizing, and
backpedaling with no reasoning (as weak as rigid defense).

## See Also
- [[AI Role Interview Loop Map]] — extends (which loops weight this round)
- [[AI-Assisted Take-Home Playbook]] — extends (time budget for the AI-assisted build variant)
- [[Timebox-Scaled Deliverable Bar]] — extends (how the bar moves with the window)
- [[AIE Code-Test Flaw Taxonomy]] — extends (the 1h code-test variant's defect list)
- [[System Design Interview Study Guide]] — alternative-to (AIE/MLE loops run case content here)
- [[Behavioral Interview Study Guide]] — extends (the "what went wrong" answer)
