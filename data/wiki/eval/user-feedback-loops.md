---
title: User Feedback Loops
tags: [eval, llm, infra]
summary: Explicit ratings or implicit usage signals from deployed users — the only eval source that catches "technically correct but unhelpful", slow and sparse and biased, whose real payoff is converting thumbs-down cases into permanent golden-set entries.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
---

# User Feedback Loops

Real users rate responses (thumbs up/down, star rating, "was this helpful?") or implicitly
signal quality — did they use the answer? did they ask a follow-up? Real signal from real
usage.

**Use when** the system is deployed with real users; you want to know if the AI is
actually *helpful*, not merely correct; you're past prototype and need ongoing monitoring.

**Avoid when** pre-deployment (no users — use golden-set or manual review); users won't
engage with feedback UI; or you need immediate automated gating, since feedback is slow
and sparse.

## What it uniquely catches

Every other rung of the [[Eval Ladder]] measures against criteria *you* defined, so none
can detect a system that satisfies its rubric while failing users. Feedback is the only
source of the "technically correct but unhelpful" signal — which is why it complements
rather than supersedes automated eval.

## The loop that matters

1. Add thumbs up/down after each response.
2. Store timestamp, user_id, query, response, rating.
3. Review weekly — what's getting thumbs down, and why?
4. **Use thumbs-down cases to expand the golden QA set.**

Step 4 is the compounding step: real failures become permanent regression tests, so
production continuously improves rung 2. Without it, feedback is a dashboard nobody acts
on. This is exactly the "wire thumbs-down in automatically" practice in
[[Golden Set Mechanics]].

## Complexity

**Multi-sprint** to implement — needs a feedback UI component, storage, and a dashboard or
alerting on quality trends.

## Scaffold mapping

| Parameter | Value | Rationale |
|---|---|---|
| `project_type` | `chat_app` | Feedback loops fit conversational interfaces |
| `agent_memory` | `conversation` or `long_term` | Store context alongside feedback |
| `vector_backend` | `postgres` | Feedback in the same Postgres as app data |

The template ships **no** direct feedback infrastructure — it's application-specific.
`agents/*/models.py` is the extension point for a `FeedbackEvent` schema.

## Trade-offs

**Pro:** real signal; catches what automated eval misses; builds a ground-truth dataset
over time.
**Con:** slow (days/weeks to accumulate); sparse (most users don't rate); **biased —
angry users rate more**; requires deployment first.

The bias matters when reading rates as quality: a falling thumbs-up ratio may reflect
changing engagement rather than a regression, so pair it with [[Heuristic Pipeline Metrics]].

## See Also
- [[Eval Ladder]] — part-of (rung 4)
- [[Golden Set Mechanics]] — feeds (thumbs-down cases become golden entries)
- [[Copilot Learning Loop]] — related (usage signal as training feedback)
- [[Heuristic Pipeline Metrics]] — complements
