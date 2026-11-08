---
title: SoL-Pi Auto-Research Harness
tags: [harness, pattern]
summary: "SoL-Pi uses an auto-research loop over 535 environments to keep four token-saving harness mechanisms, with search and held-out evaluation kept apart; the stack cuts tokens and cost at a modest score loss."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2026-sol-pi.md
---

# SoL-Pi Auto-Research Harness

SoL-Pi (Liu et al., an NVIDIA-led preprint, September 2026) runs an agent that reads traces, proposes harness changes and tests them over 535 executable environments, on top of the Pi coding harness. The target is cost, not capability. Search and held-out evaluation are separated: held-out results never feed back, and a failed validation rejects a candidate without triggering more optimisation.

## The four retained mechanisms

- Action fusion: an edit and its follow-up command in one tool call.
- Online context compaction at plan-step boundaries, when a cache-cost gate says it pays.
- ObservationPack: tool output over 10 KiB is archived to local storage and sent in full for two requests, after which the model sees a handle and head and tail excerpts and can fetch exact pages.
- Evidence-preserving reducer: a cheaper model summarises build and test logs of 4 KiB or more, and a deterministic verifier checks the summary (schema, hash, exit code, quotes).

## Findings (self-reported; single runs, no seeds)

- EdgeBench public set, 40 final tasks: with the search backend, tokens fell 49.0% and cost from $1,339 to $894, with score 42.0 against 44.8. On a held-out backend with no re-search, tokens fell 44.7% and cost 33.5%.
- Terminal-Bench 4: 15 tasks solved against 18 for the baseline, at $211 against $286. IMO 2026 in Lean: 3 of 6 for both, against 5 of 6 for a reference harness.
- Adding one mechanism at a time raised score for some (ObservationPack +5.3% on one backend), and every one lowered tokens.

## Limits

- The score drops about 6% at the full-stack point, and the harness solves fewer tasks on Terminal-Bench, so "comparable performance" is generous (the extraction's reading).
- The authors call the transfer evidence preliminary, say the counts do not establish a scaling law, and note that triggered-subset comparisons do not isolate interactions. There is no leave-one-out ablation.
- Costs use August 2026 prices and cache pricing; the gate ignores the cost of the summarising call.
- The model names are taken from the text and could not be checked.

## See Also
- [[Harness Engineering]] — prerequisite-for
- [[Harness Subsystem Attribution]] — related
- [[Iterative Harness Simplification]] — related
- [[Harness Updating vs Harness Benefit]] — related (search backend versus held-out backend)
- [[Long-Horizon Execution]] — related
