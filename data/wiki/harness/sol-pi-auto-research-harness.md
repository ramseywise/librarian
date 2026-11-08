---
title: SoL-Pi Auto-Research Harness
tags: [harness, pattern]
summary: "SoL-Pi uses an auto-research loop over 535 environments to keep four token-saving harness mechanisms, with search and held-out evaluation kept apart; the stack cuts tokens and cost at a modest score loss."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2026-sol-pi.md
---

# SoL-Pi Auto-Research Harness

SoL-Pi (Liu et al., an NVIDIA-led preprint, September 2026) uses an agent to read traces, propose harness changes and test them across 535 executable environments, built on the Pi coding harness. The target is cost, not capability. Search and held-out evaluation are separated: held-out results never feed back, and a failed validation rejects a candidate without triggering more optimisation.

## The four retained mechanisms

- Action fusion: an edit and the command that follows it go out as a single tool call.
- Online context compaction: at plan-step boundaries, and only when a cache-cost gate judges it worthwhile.
- ObservationPack: large tool output (over 10 KiB) is stored locally and shown in full for two requests; after that the model gets a handle plus head and tail excerpts, and can fetch exact pages on demand.
- Evidence-preserving reducer: a cheaper model condenses long build and test logs (4 KiB and up), then a deterministic verifier checks the condensed version for schema, hash, exit code and quotes.

## Findings (self-reported; single runs, no seeds)

- EdgeBench public set, 40 final tasks: with the search backend, tokens fell 49.0% and cost from $1,339 to $894, with score 42.0 against 44.8. On a held-out backend with no re-search, tokens fell 44.7% and cost 33.5%.
- Terminal-Bench 4: 15 tasks solved against 18 for the baseline, at $211 against $286. IMO 2026 in Lean: 3 of 6 for both, against 5 of 6 for a reference harness.
- Adding one mechanism at a time raised score for some (ObservationPack +5.3% on one backend), and every one lowered tokens.

## Limits

- The full stack loses about 6% of score and solves fewer Terminal-Bench tasks, so the extraction reads "comparable performance" as generous.
- The authors call the transfer evidence preliminary, say the counts do not establish a scaling law, and note that triggered-subset comparisons do not isolate interactions. There is no leave-one-out ablation.
- Costs use August 2026 prices and cache pricing; the gate ignores the cost of the summarising call.
- The model names are taken from the text and could not be checked.

## See Also
- [[Harness Engineering]] — prerequisite-for
- [[Harness Subsystem Attribution]] — related
- [[Iterative Harness Simplification]] — related
- [[Harness Updating vs Harness Benefit]] — related (search backend versus held-out backend)
- [[Long-Horizon Execution]] — related
