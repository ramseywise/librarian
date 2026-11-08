---
title: SWE-Lancer
tags: [eval, reference]
summary: "OpenAI's benchmark of 1,488 real Upwork software tasks worth $1,000,000 in payouts, graded by hidden end-to-end browser tests and scored in dollars earned; Claude 3.5 Sonnet earned $208k of $501k on the public Diamond split (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-miserendino-2025-swe-lancer.md
---

# SWE-Lancer

SWE-Lancer (Miserendino et al., OpenAI, ICML 2025, arXiv 2502.12115) draws its tasks from freelance
jobs posted on Upwork for a single repository, Expensify. The set has 1,488 tasks whose real payouts
add up to $1,000,000: 764 individual-contributor (IC) coding tasks worth $414,775 and 724
manager tasks worth $585,225. A public subset called Diamond holds 502 tasks worth $500,800.

## How it grades

- **IC tasks** are graded by applying the model's patch and running Playwright end-to-end
  tests that paid engineers wrote and kept hidden from the model. A task pays only if every
  applicable test passes. The tests went through three rounds of validation by engineers, plus an
  automated check that each test fails on the broken state and passes on the fixed one.
- **Manager tasks** give the model an issue, four to five proposals and the codebase; the model
  writes the id of the proposal it picks. The pick is correct if it matches the one the original
  manager chose. A separate validation by experienced engineers showed 99% agreement with those choices.
- **The metric** is dollars earned, and the earn rate is payout received divided by total
  possible payout, reported next to pass@1.

## Results (self-reported)

The headline pass@1 and earn-rate figures are single runs, with no internet access and a basic scaffold.

- On Diamond, Claude 3.5 Sonnet passed 26.2% of IC tasks and 44.9% of manager tasks and earned
  $208k of $501k (41.5%). o1 at high reasoning effort passed 16.5% and 41.5%; GPT-4o passed 8.0% and 37.0%.
- On the full set, Claude 3.5 Sonnet earned $403k of $1M (40.3%).
- Dollar weighting and pass rate diverge: Sonnet's IC earn rate is 24.5% against a 26.2% pass
  rate, while its manager earn rate is 56.8% against 44.9%.
- Attempts: on Diamond IC tasks with GPT-4o and o1, six extra attempts nearly tripled the share
  solved, and GPT-4o at pass@6 matched o1 at pass@1 (16.5%). See [[Best-of-k Headline Inflation]].
- Reasoning effort: o1 on Diamond IC tasks rose from 9.3% at low effort to 16.5% at high.
- Cost: on Diamond IC tasks averaged over 5 runs at list prices, a run cost $194.31 ± $17.31 for GPT-4o and
  $1,623.76 ± $56.68 for o1.

## Contamination handling

About half the value ($499,200) is a private holdout, partly made of IC tasks that engineers rewrote to
reintroduce the bug in a different way. Agents run without internet, and the git remote and later commits are stripped from their checkout. On a before/after-cutoff split, the authors read no clear gain on tasks that predate a
model's cutoff. See [[Eval Contamination Defenses]].

## Limits

The authors concede one repository and one platform, under-represented infrastructure work, text-only
input, no clarifying questions, and public Diamond issues that may be contaminated. The paper reports no
confidence intervals, no chance baseline for the manager task, no holdout-only scores, and no
trajectory grading; the full-set Sonnet run was a single run, which the authors tie to rate limits. Manager ground truth reflects what one manager chose, and the paper says several proposals may be technically valid. The models date from 2024.

## See Also
- [[Best-of-k Headline Inflation]] — related (the attempts ablation)
- [[MLE-bench]] — alternative-to (another outcome-graded benchmark of real engineering work)
- [[Trajectory Over Outcome]] — related (SWE-Lancer grades end state only)
- [[Repository-Level Coding Benchmarks]] — related
- [[AlphaEval]] — related (value-weighted scoring)
