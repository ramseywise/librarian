---
title: Eval Metric Interpretation Pitfalls
tags: [eval, llm, concept]
summary: "Ways a correct-looking eval number misleads — flat headlines hiding cancelling slice moves (Simpson's paradox), dropped errored rows shrinking the denominator, ratio metrics whose denominator moves, novelty effects — and the rule: count errors and refusals as failures or report them separately."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--09-reading-results.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--12-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--06-eval--notes--03-eval-datasets.md
  - data/raw/papers/2026-11-05-zhang-2023-benchmarking-large-language-models-news.md
---

# Eval Metric Interpretation Pitfalls

## Slice before you conclude

A flat headline can hide a win and a loss that cancel:

| Slice | n | A | B | Δ |
|---|---|---|---|---|
| Billing | 120 | 82% | 90% | +8 |
| How-to | 150 | 88% | 89% | +1 |
| Non-English | 40 | 75% | 58% | **−17** |
| **Overall** | 310 | 84% | 85% | +1 |

"+1 overall" ships a change that breaks non-English users. Break results down by the slices
labeled on every row, and show n per slice so nobody over-reads a 12-task slice. **Simpson's
paradox:** B can win every slice and lose overall (or the reverse) when slice mix differs
between runs — compare on identical task sets. Too many slices manufactures false positives
([[Eval Error Bars and Sample Size]]).

## The denominator

"92% pass" means nothing until you say *of what*. From Dmitriev et al.'s *Dirty Dozen*
(KDD 2017), the pitfalls that bite LLM evals:

| Pitfall | In LLM evals |
|---|---|
| **Sample ratio mismatch** | B errored on 8% of tasks, which were dropped; B's pass rate is over its easier 92% |
| **Ratio metric, moving denominator** | "Grounding rate" rose because B refuses more and answers less |
| **Novelty effect** | Online, users engage more with any change for the first week |
| **Overall vs segment confusion** | The slicing problem above |
| **Ignoring the error bar** | Shipping on +2 points over 50 tasks |

**Rule: count errors and refusals as failures, or report them as their own rate — never let
them silently leave the denominator.** Infra failures are retried, then counted separately,
never as task fails and never dropped ([[Run-Then-Assert Eval CI]]).

## Measuring the wrong thing

The quietest failure: everything works and the metric does not track what users care about.

- Generic metrics instead of ones from [[Error Analysis (Open and Axial Coding)]].
- Wrong unit — per-turn scores fine while conversations fail to resolve.
- Offline–online gap — the set no longer looks like production.
- Reference quality — in news summarization (Zhang et al., arXiv 2301.13848; 100 articles each
  from CNN/DM and XSUM, three MTurk raters per summary, system-level Kendall's tau), the authors report that ROUGE-L,
  METEOR, BERTScore, BARTScore and BLEURT correlated better with human ratings on aspects where the
  reference summaries themselves rated well. On XSUM faithfulness the
  correlations were negative (ROUGE-L -0.27) with the original references, and the authors report a
  much more positive one with freelance-written references (figure only, no number). The authors found the
  original references rated below most systems (CNN/DM faithfulness 0.84 against 0.99 for
  zero-shot Instruct Davinci), and in a blinded comparison of 100 pairs six annotators preferred
  freelance-writer summaries over Instruct Davinci 50.4% to 49.6%, with Krippendorff's alpha 0.07
  for overall preference. Limits: news only, English, 2022 models, no LLM judge tested, no
  inter-annotator agreement for the main MTurk study.

Check periodically that offline scores **predict** online outcomes; if the offline winner
doesn't win online, the eval measures something else.

## Mechanism vs target in online experiments

When the change is "shorter plan files", plan length is the *mechanism*, not the *target*
(session cost) — shorter plans can cause more edit–check–edit loops and raise total cost.
Optimize the target; test several doses, not just on/off, to see the dose–response curve.

## See Also
- [[Eval Error Bars and Sample Size]] — related (width vs meaning of a number)
- [[Paired Eval Comparison]] — related (identical task sets)
- [[Outcome Signal Ladder]] — related (proxy vs outcome signals)
- [[Validated Concept vs Unmeasured System]] — related (a number quoted beyond what it measured)
- [[VLM Benchmark Shortcuts]] — instance-of (tie-breaking, language priors and strict string match in VLM benchmarks)
- [[Output Length Confounds Reference Metrics]] — instance-of (answer length moves n-gram and judge scores)
