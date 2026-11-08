---
title: User Feedback Loops
tags: [eval, llm, infra]
summary: Explicit ratings or implicit usage signals from deployed users — the only eval source that catches "technically correct but unhelpful", slow and sparse and biased, whose real payoff is converting thumbs-down cases into permanent golden-set entries.
updated: 2026-11-08
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/eval-approaches.md
  - data/raw/claude-docs/akira/docs/research/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-20-dis345-favourite-holdout-judgments.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--11-production-and-the-maturity-ladder.md
  - data/raw/papers/2026-11-07-building-applications-with-ai-agents-ch10-monitoring-production.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch10-ai-engineering-architecture-user-feedback.md
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch10-composable-agentic-workflows.md
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

## Favourites as a Held-Out Signal, Not Ground Truth

A proposal to treat user favourites as relevance labels was scoped down to a **held-out
validation signal**: compare favourites against existing rater-graded moments instead of
training or gating on them. Three traps surfaced:

- Reusing an existing holdout constant for a new purpose hides a second decision. Name
  it separately.
- Stamping rows with version values that weren't actually in force would break the
  row-level invariant that a stamp means "produced by this version".
- **Check volume first.** Both source tables had 0 rows, so the design question was
  premature.

The executed decision (akira, 2026-09-20) recorded the reason for the scoping as a
**leakage asymmetry**: held-out rows exist precisely so they can score a corpus from
outside. Using them to *validate* a corpus they were never part of is not circular;
inserting them into that corpus as ground truth would be. Two practical consequences:

- **Stop the code promising a path nobody will build.** Source comments still said the
  holdout enum value would be populated "once" an earlier issue shipped. That issue had
  shipped and nothing wrote the value. The fix was comment-and-spec only: re-document the
  enum value as validation-only, keep the seam, no migration, no populator, at zero rows.
- **Name the unbuilt prerequisite instead of filing it.** Writing real judgment rows would
  need the serving log to retain the full scored candidate and the version columns it
  never wrote. That gap was recorded as a named follow-up in the decision row, so it is
  not rediscovered as a surprise.

## Three kinds of feedback signal (course synthesis)

| Signal | Strength | Weakness |
|---|---|---|
| **Explicit** (👍/👎, ratings) | Direct | Sparse (often < 1–2% of turns), biased toward extremes |
| **Implicit** (rephrasing, abandonment, escalation, copy) | Plentiful | Ambiguous — a short session may be success or giving up |
| **Downstream outcomes** (ticket reopened, refund reversed) | Closest to value | Delayed, hard to attribute |

Feedback is a **sampling rule and a calibration label**, not a metric to optimize directly:
optimizing the 👍 rate rewards flattery.

## Conversational feedback and its biases (Huyen, Albada)

Huyen (*AI Engineering*, O'Reilly, chapter 10) separates **explicit** feedback (information users give in answer to a request) from **implicit** feedback (inferred from what they do). Albada (chapter 10 of *Building Applications with AI Agents*) logs implicit signals such as rephrasing and abandonment, and explicit ratings, as metrics, and ties low ratings to traces so they can enter the evaluation set. The chapter also advises converting each production failure into a regression test, by exporting its trace into the test suite, and keeping exemplar successes as golden paths.

- **What users say.** In the FITS dataset, automatic clustering into 8 groups found the largest cluster to be users clarifying their demand again, 26.54% (3,702 items) (reported).
- **When to ask.** Huyen recommends asking without interrupting: at the start of a conversation, after something goes wrong, and when the model is unsure. Showing the prompt to just 1% of a big user base is proposed to spare users annoyance, though that adds feedback bias (the chapter's claim).
- **Biases.** Huyen recommends varying option positions to offset position bias and inspecting rating distributions for leniency: Uber drivers averaged 4.8 in 2015 and scores below 4.6 risked deactivation (reported).
- **Training on feedback.** Huyen advises care with degenerate feedback loops, where predictions shape the feedback that shapes the next model, and with sycophancy.

Limits: the chapter admits it does not know which gives more reliable feedback, full or partial side-by-side responses, and the rewrite of Uber's rating options is not validated. Neither chapter has experiments of its own.

## Copilot mode and agent mode (Lakshmanan and Hapke)

Their composable-workflow chapter treats agent mode as copilot mode where the user accepts every recommendation, so one workflow serves both. Feedback is collected through the interface: both the generated draft and the person's edited version are stored, and a changed decision (for example a different writer assigned) is logged. If people have to leave the application to complete the task, the agent never sees the context it would need to learn from. They add that organic feedback alone is not enough (volume, detail hidden by last-step edits, automation fatigue, wrong labels) and pair it with a data program, tie steps to delayed business outcomes, and sample logs at scale. No numbers are given.

## See Also
- [[Eval Ladder]] — related (part of; rung 4)
- [[Golden Set Mechanics]] — related (feeds; thumbs-down cases become golden entries)
- [[Copilot Learning Loop]] — related (usage signal as training feedback)
- [[Heuristic Pipeline Metrics]] — related
- [[Online Eval Sampling]] — extends (negative feedback as one of four production sampling rules)
- [[Explore Slice for Position Bias]] — extends (a feedback loop that cannot learn from its own ranking)
- [[Outcome Signal Ladder]] — extends (which proxy counts as the outcome before attendance is loggable)
- [[Write-Time Deterministic Holdout]] — extends (the hash-split column that made favourites holdable before any consumer existed)
- [[Observability and Runtime Patterns]] — related (the monitoring side that feeds the same evaluation set)
