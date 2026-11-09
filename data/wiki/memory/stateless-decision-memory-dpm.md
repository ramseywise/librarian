---
title: "Stateless Decision Memory (DPM)"
tags: [memory, agents, concept]
summary: "DPM keeps an immutable event log and builds the agent's memory as a projection at decision time instead of maintaining a running summary; in one small study it beat incremental summarization only when the memory budget was tight (self-reported), and it shrinks the audit surface to two calls."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-srinivasan-2026-stateless-decision-memory-enterprise-ai.md
---

# Stateless Decision Memory (DPM)

A design for agent memory inside one regulated decision (a loan or an insurance claim), where an auditor may later ask exactly what the agent saw. The log of events is append-only: an event is never edited, summarized or overwritten. Memory is not a stored object. It is a single projection computed from the full log at the moment of the decision, with every claim in the projection citing the index of the event it came from. Because nothing is shared between decisions, tenant isolation follows from the structure rather than from access rules bolted on.

The baseline is **Summ-only**: a running summary rewritten after every event within the same budget, the strongest stateful baseline the study used. The author's reading is that this loses content at each step and the losses accumulate over a trajectory of 82 to 96 events. The extraction notes this is the author's interpretation, not isolated by an ablation.

## What the study measured

All numbers below are self-reported. Setup: LongHorizon-Bench, ten cases split evenly between loan and claim decisions, trajectories of about 26,762 characters, claude-haiku-4-5 as both agent and judge at temperature 0, paired permutation test with 10k resamples.

- **Tight budget** (1,338 characters, about 20x compression): FRP 0.907 for DPM against 0.392 for Summ-only (+0.515, p=0.001), and RCS 0.800 against 0.267 (+0.533, p=0.003) (self-reported). EDA and CRR gaps of +0.500 each were not significant (p=0.065 and 0.066).
- **Moderate (5x) and loose (2x) budgets:** the designs cannot be told apart; the moderate FRP difference is -0.043 (p=0.255) and the loose one -0.032 (p=0.625) (self-reported).
- **Cost and latency, n=10 per cell:** at the tight budget $0.014 vs $0.165 per run and 59.8 s vs 440.3 s; at the moderate budget $0.020 vs $0.129 and 23.0 s vs 342.6 s; at the loose budget DPM was slower (86.6 s vs 57.4 s) (self-reported). Cost for the summary baseline is reconstructed from run time and token limits, since the harness logged no cost.
- **Audit surface:** capturing one decision from Summ-only takes 83 to 97 model calls; DPM takes 2 (self-reported, a structural count).
- **Replay:** temperature 0 on the live API was not byte-deterministic for either design over 10 replays. On the 3 large cases DPM produced 10 unique hashes in 10 runs; on the 2 small cases DPM produced 6 of 10 unique and Summ-only 9 of 10 (loan) and 5 of 10 (claim) (self-reported). Byte-exact replay would need a pinned model version and runtime.

## Selection rule

The paper proposes: use DPM when replay, audit or isolation is required; otherwise use DPM when the trajectory-to-budget compression ratio exceeds roughly 10x; otherwise either. Only ratios of 2, 5 and 20 were tested, so the 10x line is interpolated (self-reported heuristic from 2 domains and one model family).

The projection prompt asks the model to preserve amounts, dates, identifiers and policy limits exactly, attach an event index to each claim, and output three sections in fixed order: facts, reasoning, compliance notes.

## Limits

- Single author, preprint, 10 cases, two domains, one model, a same-family judge with no cross-family check, and no multiple-comparison correction; the pooled test has no per-domain breakdown.
- No full-context baseline and no no-memory baseline is reported; retrieval and schema-anchored memory were not run, and other memory systems are discussed only in prose.
- The author concedes DPM is weaker in expressive power: an agent cannot edit its own memory mid-trajectory, a single-call context ceiling applies, and hierarchical projection is future work.
- Nothing is shown about pruning, staleness, forgetting, cross-session learning, horizons above 100k characters, or adversarial content.
- Internal inconsistency: the ceiling on a single call is stated three ways: about one million tokens in the limitations text, tens of thousands of characters in the design text, and a range of 10^4 to 10^6 characters at the close. The extraction also notes that the small-case DPM replay distance (0.036 to 0.084) was higher than Summ-only's (0.000 to 0.013), so the replay advantage is argued structurally rather than shown, and that the loose-budget Summ-only timing was flagged as anomalous.

## See Also
- [[Agent Memory Types]] — prerequisite-for
- [[Memory Architecture]] — prerequisite-for
- [[Designed Memory vs Raw-Record Search]] — related (raw record kept, view built at read time)
- [[Memory Lifecycle]] — related
