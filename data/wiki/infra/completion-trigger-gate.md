---
title: Completion Trigger Gate
tags: [infra, llm, pattern]
summary: "For keystroke-triggered inline completion, the main cost and latency lever is deciding whether to call the model at all: client debounce, parser-based suppression at low-value cursor positions, and a cheap acceptance-probability classifier that skips the LLM below a threshold — plus cancelling stale in-flight requests."
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--coding-copilot.md
---

# Completion Trigger Gate

Inline code completion is triggered at every typing pause, across millions of developers.
Most of those pauses don't merit a suggestion. Calling the model on each one costs tokens
and also slows the suggestions that matter. The design answer is a gate on the client
that runs before any model call, in cheap-to-expensive order:

1. **Debounce** (about 75 ms) so the client doesn't fire on every keystroke.
2. **Syntactic suppression**: a parser such as Tree-sitter skips positions where a completion rarely helps, for example right after a completed statement.
3. **Contextual filter**: a small logistic regression over cheap features (language, whether the last suggestion was accepted, time since the last accept or reject, last line length, the character before the cursor) predicts whether a suggestion would be accepted. Below a threshold (around 15% in the reported design), the LLM call is skipped.

Only requests that pass all three reach the model, and only 1–3 candidates are requested.

## Companion mechanics

- **Cancel or recycle in-flight requests.** When the user keeps typing, cancel the stale
  request so you don't pay for an outdated completion. Make sure cancellation actually
  stops the GPU work, or the savings exist only on the client.
- **Stream and truncate early** once the suggestion forms a coherent unit.
- **Tune the gate by watching the call rate against the acceptance rate.** If the call
  rate rises while acceptance holds steady, the trigger is firing too often. Tighten the
  threshold and the debounce.

## Why it generalizes

It is the same move as [[Spend Gate Before the Model Call]] in a batch pipeline: a
deterministic or very cheap check decides whether a token is worth spending, and every
skip is counted. The copilot version adds a learned acceptance predictor, because the
"is it worth it?" signal there is user behaviour, not input hashes.

## See Also
- [[Spend Gate Before the Model Call]] — alternative-to (the batch-pipeline version of the same gate)
- [[AI System Design Walkthroughs]] — instance-of (the coding copilot problem)
- [[Context Engineering and Cost Interview Study Guide]] — extends
