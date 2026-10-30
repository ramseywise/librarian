---
title: Run-Then-Assert Eval CI
tags: [eval, infra, pattern]
summary: "Split an eval job into a slow, costly RUN phase that writes results.jsonl and a fast deterministic ASSERT phase that computes CIs per slice against a stored baseline — tiered by trigger (smoke per PR, regression on prompt/tool paths, full nightly), with every gate emitting metrics, labels, worst slices and a next action."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--10-evals-in-ci.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--09-reading-results.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--README.md
---

# Run-Then-Assert Eval CI

An eval nobody runs protects nothing. Put cheap suites on every change, expensive ones on a
schedule, and separate *running* from *asserting*.

## Two phases with an artifact between them

```
Phase 1: RUN                              Phase 2: ASSERT
  for each task × trial:                    load results.jsonl
    run SUT, capture trace                  compute metrics + CIs per slice
    run graders                             compare to baseline / thresholds
    write row → results.jsonl               emit pass/fail per gate + report
  (slow, costly, non-deterministic)         (fast, free, deterministic)
```

- **Re-assert without re-running** — change a threshold or add a slice, recompute in seconds.
- **Debug the gate separately** — an assert crash doesn't cost the expensive run.
- **Results are an artifact** — uploaded, diffed against the last run, attached to the PR.
- **Flakiness is visible** — retries and infra errors are recorded in phase 1, not swallowed.

## What runs when

| Trigger | Suite | Graders | Blocks? |
|---|---|---|---|
| Every commit / PR | Unit tests + smoke eval (10–30 tasks) | Code only | Yes |
| PR touching prompts, tools, retrieval | Regression suite | Code + calibrated judges on a sample | Yes |
| Nightly | Full suite, k trials | All, experimental tracked | Alerts only |
| Pre-release | Full + held-out + adversarial | All calibrated | Release gate |
| Model / provider change | Everything, paired vs prod | All | Yes |

Path filters keep a README change from triggering a costly judge run.

## Regression gate rule types

| Rule | Example | Catches |
|---|---|---|
| Absolute floor | Schema validity ≥ 99%; citation hallucination = 0 | Never-events |
| Relative to baseline | Grounding not > 3 points below prod (paired, CI excludes −3) | Regressions |
| Per-slice floor | No labeled slice drops > 10 points | Hidden slice regressions |
| Efficiency budget | Cost per success ≤ 1.2 × baseline; p95 latency ≤ 8 s | Silent cost blow-ups |
| Regression set | Previously fixed failures ≥ 95% | Re-breaking old bugs |

Gate on the **confidence interval** of the paired difference, not the point estimate
([[Paired Eval Comparison]]). Update the baseline deliberately after each release.

## The gate ladder inside one run

```
data quality → retrieval → generation → grader calibration → release
```

A later gate scores only rows an earlier gate marked eligible (the row-pool rule in
[[RAG Eval Gate Contract]]). The grader-calibration gate fails if a gating judge is
experimental or stale ([[Grader States (Heuristic, Calibrated, Experimental)]]). This
ordering is distinct from the [[Eval Maturity Ladder]], which orders *building* an eval
practice.

## What a gate emits

Every gate returns the same shape: `gate`, `passed`, metrics with value / CI / baseline,
`rows_scored` and `rows_ineligible`, `top_failure_labels` ([[Eval Failure Taxonomy]]),
`worst_slices` with n, and a `next_action`. A gate that only says `FAILED` sends someone on
a half-day hunt.

## Practical details

- **Own API key with a spend cap** for the eval job.
- **Rate-limited concurrency** — otherwise you grade 429s.
- **Infra failures ≠ eval failures** — retry, then count separately; never a task fail,
  never silently dropped ([[Eval Metric Interpretation Pitfalls]]).
- **Cache** SUT outputs by (input, config hash) and judge outputs by (output hash, judge
  version).
- **Pin everything** — model IDs, judge versions, dataset version — and record them in the
  results file ([[Frozen Version Stamps on Logged Results]]).
- **Name owners**: infra owner (runner, CI, dashboards, cost), criteria owner (pass/fail,
  taxonomy, calibration sign-off), and every engineer adds a row when fixing a bug.

## See Also
- [[RAG Eval Gate Contract]] — instance-of (a project's gate ladder and handoff contract)
- [[Paired Eval Comparison]] — prerequisite-for (the statistics the assert phase applies)
- [[Eval-Driven Development (EDD)]] — related
- [[Frozen Version Stamps on Logged Results]] — related (versions on every result row)
- [[UNGATED Metric Convention]] — related (metrics that run but don't yet assert)
