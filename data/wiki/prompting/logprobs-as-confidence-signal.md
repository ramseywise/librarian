---
title: Logprobs as Confidence Signal
tags: [prompting, llm, eval, pattern]
summary: Where the API exposes token log-probabilities they are the best confidence instrument — gate on average token probability, read classification probabilities off a first token, give every label a distinct first token to avoid prefix collision, and calibrate per-label offsets on labelled data.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--04-controlling-output.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
---

# Logprobs as Confidence Signal

A logprob is the log-probability of each emitted token (0 = certain; `exp()` converts).
Some providers disable them, especially on newer models; where available they are your
best instrument.

**Reading the numbers:** single-digit negatives are normal for free text; double-digit
negatives mean something odd happened. Tokens near the *start* of a run score lower (less
context). Expect about ±1 jitter between identical calls.

## Uses

- **Quality score.** Average token probability over the completion — or over its first
  tokens, which a code-completion product found most predictive. Gate on it: show only
  high-confidence suggestions, warn, retry, add context, or escalate to a stronger model.
  **Don't be like Clippy** — interrupting users with low-confidence output costs more trust
  than staying quiet.
- **Classification.** Make the decision the first token after a known start
  (`1. [positive | negative | neutral]`) and read each label's probability. In evals,
  comparing logprobs instead of the sampled label gives more statistical power from the
  same samples ([[Evaluating Prompts]]).
- **Prompt debugging.** With prompt echo (where supported), logprobs on the *prompt* flag
  surprising tokens — typos and odd phrasing dip below roughly −13.

## Prefix-collision pitfall

In a region classifier, "Europe" scored 44% on the first token and `North` 55% — but
`North` was split between North America (42%) and Northeast Asia (13%). Sampling picks
`North`, a less likely continuation can then win, and the output is "Northeast Asia" when
Europe was the single best label. **Give every label a distinct first token.**

## Calibration

The model's 50% is not your threshold. Shift per-label logprobs by constants fitted on
labelled data (e.g. +0.3 to "Yes" if it under-calls), fitted with logistic regression or
cross-entropy minimization. **Logit bias** applies the same shift at generation time where
available.

## See Also
- [[Sampling Parameters]] — extends
- [[Evaluating Prompts]] — prerequisite-for
- [[Stop Sequences and Completion Anatomy]] — extends (a known start makes the decision token readable)
