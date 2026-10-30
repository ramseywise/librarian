---
title: Binary Gate Sample Power
tags: [eval, pattern]
summary: "Before a small model-comparison run, compute what it can detect: with per-event pass/fail gates, the chance of seeing at least one failure in N events is 1-(1-p)^N. That makes N=10-20 a gross-failure detector (it catches a 15-30% failure rate) and not evidence of parity, so the results must state that scope."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
---

# Binary Gate Sample Power

A cheaper-model experiment (repo akira) planned a hosted open-weight arm against the
production model, using 10–20 live events cut down for cost. The issue asked a *quality*
question. A sample too small to see the thing it measures produces a false "no difference",
which is worse than not running the experiment. So the plan made the power argument
explicit instead of just asserting a sample size.

## The arithmetic

The instruments were four deterministic, per-event pass/fail gates (validation, review
gate, sanitize, flatten), each thresholded at 1.0. If an arm's true per-event failure rate
is *p*, the chance of seeing at least one failure in *N* independent events is
`1 - (1 - p)^N`:

| True failure rate | N = 10 | N = 20 |
|---|---|---|
| 30% (systemic break) | 97% | >99.9% |
| 15% (moderate) | 80% | 96% |
| 10% | 65% | 88% |
| 5% (subtle) | 40% | 64% |

## What to claim

- **N=10–20 detects gross failure only.** It can say with good confidence whether the new arm
  breaks the deterministic pipeline at least 10–15 points more often than the incumbent.
  It can't separate a few-point degradation from noise.
- **Write the scope into the result row.** "4/4 gates held at 1.0 across 20 events" must not
  be read as subtle-quality parity.
- **No N fixes a missing instrument.** These gates check output shape, not whether a mood tag
  is apt. The prose-quality judge stayed ungated until a human-agreement ceiling existed,
  and no sample size changes that.
- **Size the follow-up from the same formula.** Detecting a ~5-point structural degradation
  at ≥90% power needs about 45–60 events per arm. That is batch-run infrastructure, not
  sequential single-event CLI calls.

## Related discipline from the same plan

- **Measure tokens, then price them with the published price sheets.** The internal cost
  baseline was marked disputed, likely 6–10× too high. The plan sidestepped the dispute by
  recording per-call prompt and completion tokens from each provider's own response and
  multiplying by each provider's published per-token price at run time. The incidental
  incumbent $/event figure was explicitly *not* written back as a replacement baseline.
- **Closed ≠ done.** The prerequisite cost-baseline issue was closed by a triage comment
  while its execution plan was still in progress with every box unchecked. Tracker state is
  not evidence that an artifact exists.
- **Check capability dependencies before swapping providers.** The enrichment call used
  plain text generation, not structured output or tool calling, so any
  chat-completions-compatible endpoint would do. The thing that has to be provider-agnostic
  is the usage-field mapping, which the SDK's adapter normalises.
- **Pin the scope.** A local-model arm answered a different question ("does the pipeline
  work provider-agnostically at zero cost?") from the issue's ("is a cheap hosted model good
  enough to adopt?"), so it was named out of scope rather than bundled into the done
  criteria.

## See Also
- [[Fixture Eval Blind to the Swapped Component]] — extends (once the eval actually calls the model, this is how big the live sample has to be)
- [[Eval Falsifiability]] — related (an underpowered sample is another eval that cannot fail)
- [[Measurement Fix Mistaken for Model Gain]] — related (the other way a small model comparison misleads)
- [[Small-N Reporting Floor]] — prerequisite-for (printing what a small N measured)
- [[Eval Error Bars and Sample Size]] — extends
