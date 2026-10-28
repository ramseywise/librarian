---
title: Dark Outcome Tier
tags: [eval, pattern]
summary: "A metrics hierarchy for agent work where the top tier (task success, cost per merged PR) was unmeasured while the easy-to-instrument tiers (cache hit rate, peak context) were being tuned. Establish an outcome signal first, with a manual pilot before any infrastructure, and only build a metric that passes the test 'what would I do differently if this number changed?'"
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-context-engineering-v2.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-context-engineering-v2.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-dashboard-iteration.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-dashboard-iteration.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-29-dashboard-tab-improvements.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-29-dashboard-tab-improvements.md
---

# Dark Outcome Tier

## The hierarchy

A review of a coding-agent usage dashboard ranked its metrics by how close each one sits
to the outcome that actually matters:

| Tier | Metric | State at review |
|---|---|---|
| 0 | Task success / verified-correct completion rate | **dark: not measured** |
| 0 | Cost per merged PR / per closed issue | inputs exist, join never built |
| 1 | p90/p50 cost ratio; signal density | improving / proxied |
| 2 | Cache hit rate; p90 peak context vs the context cliff | 97% (solved); just under the cliff |
| 3 | Compaction rate; turns per session | instrumented |

All the tuning effort had gone to Tiers 2–3 **because they are easy to instrument**. The
metric that decides whether the work was worth doing ("did this session produce correct,
shippable work?") was invisible. The trap carries over to the next plan: adding *more*
Tier 2–3 visibility (new tabs, review-finding counts, loop shape) before Tier 0 exists
repeats the same mistake at a larger scale.

## Rules that came out of it

- **The action test.** Every proposed metric must answer "what would I do differently if
  this number changed?" If the answer is nothing, don't build it. More tabs do not mean
  better decisions.
- **Pilot the outcome signal by hand first.** Before building any pipeline, tag about 20
  sessions manually as success / partial / failed / skip, as an opt-in prompt at session
  end. The pilot tests whether the signal is usable before it gets a fact-store column.
- **Order work by tier, not by what is cheap.** The next phase was scoped as review-finding
  persistence plus the outcome pilot. A cost-per-successful-outcome model-swap A/B waits
  for the pilot.
- **The dashboard consumes eval results, it doesn't run evals.** The analytics side reads
  what eval harnesses emit. That keeps it from turning into a second, undeclared eval
  system.

## Read the proxy for what it is

Two later findings from the same dashboard show the same gap at finer grain:

- **Cache hit rate is an input-reuse proxy, not input-volume visibility.** Input tokens
  were stored as a column and used in cost math, but no series ever showed them. "Context
  health is about input" was correct, and the metric shown did not measure it.
- **A finding's true-positive rate, derived from its post-merge disposition, measures
  "acted on", not "accurate".** The only ground truth available is whether the linked
  issue was completed or closed as not-planned. A correct finding that was deferred
  scores as a false positive. The review verdict comes before the commit and the agent
  never commits, so the timing gap is structural. Any such chart must be labeled as an
  *action rate*.

## Make each number readable

A companion dashboard pass found that chart annotations were notes from the author to
themselves. The fix:

- Every chart subtitle says **which direction is good and what the number means in
  practice**, e.g. "Higher is better. Below 90% means context churn is breaking the prompt
  cache."
- Each section answers **one question** ("Am I spending well?", "Is context under
  control?").
- Values carry magnitude labels, not just a shape.

A metric that the reader cannot interpret fails the action test by default.

## See Also
- [[Dispatch-Shaped Agents Hide Cost]] — related (the attribution gap found in the same review)
- [[Friction Is Rework, Not Error Rate]] — related (the same dashboard, reclassifying what its friction metrics measure)
- [[Telemetry Claim Verification Gate]] — extends (a number must also be the right number before it drives action)
- [[Rate Metrics Measure the Logger]] — related (the dashboard's earlier sampling-frame audit)
- [[Falsifiable Hypothesis Gate]] — related (a metric should say what would change the decision)
- [[Signal Without a Consumer]] — related (the producer-side mirror: signals emitted that nothing reads)
