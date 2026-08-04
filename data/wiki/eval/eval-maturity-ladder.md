---
title: Eval Maturity Ladder
tags: [eval, llm, agents, reference]
summary: "Five levels of what eval infrastructure exists — vibes, deterministic gates, separated evaluator, eval sets plus tracing, continuous sampling — with most builders at 0 and production demanding 3+."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--eval-maturity-ladder.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Eval Maturity Ladder

The **adoption path**: what to build first when a system has no evals at all.

Distinct from two neighbours that are easy to conflate:

- The **gate ladder** (data quality → retrieval → generation → grader calibration →
  release) orders gates *within* an already-mature suite.
- [[Eval Ladder]] orders *grading approaches* by project phase.

This ladder orders **the stages of getting there**.

## The ladder

| Level | What exists | What it catches | What it misses |
|---|---|---|---|
| **0** | Manual review ("vibes") | Whatever you happen to look at | Everything you don't |
| **1** | Deterministic gates (hooks, tests, linters) | Structural failures | Anything requiring judgment |
| **2** | Separated evaluator | Behavioral failures | Failures not in your sample |
| **3** | Eval sets from real failures + tracing | Regressions; *where* a run broke | Slow drift in production |
| **4** | Continuous sampling with drift alerts | Divergence from baseline over time | — |

> **Most builders sit at Level 0. Production demands Level 3+.**

That gap is the entire point of the ladder, and it is why *"we'll add evals later"* reliably
means *"we have no signal when this breaks."*

### Level 1 — deterministic gates

Tests and linters wired to hooks. Cheap, fast, no LLM in the loop. **The highest
return-per-effort rung**: it catches schema violations, broken builds, and malformed output
that would otherwise consume judgment-tier budget. Exhaust this rung before reaching for a
judge.

### Level 2 — separated evaluator

A **fresh-context** reviewer. The key property is separation — *the evaluator did not write
the thing it is judging, so it has no commitment to it.*

The strong form **operates** the output behaviorally — clicking, running, testing — rather
than reading it and forming an opinion. That behavioral insistence is this ladder's specific
contribution on top of the generator/evaluator separation in [[Verification Loops]]: a
reviewer that reads code is checking whether it *looks* correct, which is a different
question from whether it *is*.

### Level 3 — eval sets from failures + tracing

Two things that arrive together and neither works alone:

- **Eval sets seeded from real observed failures** — not synthetic cases invented up front.
  Every production failure becomes a row. This is how the suite stays about *your* system.
- **Tracing** — *"log every step's input, tool calls with arguments, results, and
  decision."*

### Level 4 — continuous sampling with drift alerts

Run the scoring pipeline against live traffic continuously; alert on divergence from
baseline. Mechanism in [[Online Eval Sampling]].

## Trajectory over outcome

The methodological claim behind levels 3–4:

> Measuring only final success tells you *that* a run failed. Trajectory analysis through
> traces tells you **where** — retrieval was wrong at step 3, an error was swallowed at
> step 7.

This matters most for agents specifically: **a multi-step run has many ways to reach the
same wrong answer, and they need different fixes.** An outcome-only eval scores them
identically. See [[Eval Harness Anatomy]] for the trajectory/outcome pair.

## Grader types are layered, not chosen between

| Grader | Scales | Cost | Role |
|---|---|---|---|
| Deterministic gates | Fully | Near-zero | First line — structural failures |
| Separated evaluator agent | Well | Medium | Behavioral verification |
| LLM-as-judge | Fully | Medium | Subjective criteria at volume |
| Human spot-checks | Poorly | High | **Calibration** of the judge |

**LLM-as-judge requires rubric specificity plus explicit mitigation of three documented
biases** — position bias, verbosity preference, and self-preference (favouring its own
output). Left unmitigated, *the judge is confidently miscalibrated rather than merely
noisy*, which is worse: noise is visible in variance, miscalibration is not.

**Human spot-checks are a 5–10% calibration sample, not a review queue.** Their job is to
tell you whether the judge can be trusted — mapping onto the `calibrated` vs `experimental`
grader states, where an uncalibrated judge is tracking-only and **must never be a release
gate**.

## Metrics beyond pass rate

- **Steps-to-completion** — efficiency. *Rising steps at a flat pass rate means the agent is
  thrashing its way to the right answer* — a real regression that outcome-only evals score
  as green.
- **Cost-per-success** — note the denominator. Failed runs are pure cost, so **a loop with a
  50% pass rate is twice as expensive as its per-run cost implies.**
- **Trace-level input/output at each step** — the substrate for everything at level 3+.

## Design checklist

- [ ] What level is this system on today — honestly?
- [ ] Are deterministic gates exhausted before reaching for an LLM judge?
- [ ] Does the evaluator have fresh context, and does it *operate* the output or just read it?
- [ ] Are eval rows seeded from observed failures, or invented?
- [ ] Is the judge calibrated against a human sample, and how recently?
- [ ] Is cost tracked per *success* rather than per run?

## See Also
- [[Eval-Driven Development (EDD)]] <!-- auto-linked -->
- [[Anthropic Three-Tier Eval Taxonomy]] <!-- auto-linked -->
- [[Eval Ladder]] — complements (grading approach by project phase; this page is infrastructure by stage)
- [[Eval Harness Anatomy]] — depends-on (the vocabulary this ladder builds on)
- [[Online Eval Sampling]] — instance-of (level 4)
- [[Eval Suite Maintenance]] — extends (keeping a level-3 suite honest)
- [[Verification Loops]] — depends-on (level 2 is generator/evaluator separation, made behavioral)
- [[LLM-as-Judge Evaluation]] — depends-on (the three biases and the calibration requirement)
- [[Observability and Runtime Patterns]] — prerequisite-for (level 3 needs tracing to exist)
