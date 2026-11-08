---
title: Aegean Stability-Horizon Consensus
tags: [harness, pattern]
summary: Aegean is a leader-based, Raft-like protocol that finalizes a multi-agent answer only when a quorum agrees and the answer has held for a set number of rounds, replacing fixed round limits and majority voting; its speedups of 1.2 to 20 times at accuracy within 2.5% are self-reported on math and multiple-choice tasks.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ruan-2025-reaching-agreement-among-reasoning-llm.md
---

# Aegean Stability-Horizon Consensus

Ruan et al. (arXiv 2512.20184, December 2025 preprint) start from a failure of simple majority
voting across refinement rounds: agents revise once they see their peers' reasoning, and the majority may therefore flip
from one round to the next, and a fixed round limit or a stop-at-majority rule can commit a transient state.

## Mechanism

Aegean is a leader-based protocol modelled on Raft for stochastic agents. An answer is finalized
only when at least alpha agents agree (the quorum) and the same answer has held through beta
successive rounds (the stability horizon). If a candidate is overturned, the stability
counter goes back to 1. Defaults are three agents, alpha 2, beta 2 and at most 5 rounds. Whether two answers are equivalent is decided by exact match,
embedding similarity or an LLM judge. A fast path finalizes when a
quorum is stable for two rounds; a slow path covers an overturned majority. The serving engine
exposes dispatch, completion callback, cancel and ensemble-state calls. Safety and liveness
proofs (refinement validity, monotonicity, termination) rest on an assumption that an agent given several
solutions can reach the quality of the best (the authors do not prove this for LLMs), plus at most
half-minus-one agents that stop on failure, and a partially synchronous network.

## Results (self-reported)

- **Latency.** 1.2 to 20 times lower average latency than a barrier-synchronized baseline with fixed
  round limits and majority voting, up to 11 times at P99, with accuracy within 2.5%. Setup: five
  local open models on 8 H100 GPUs with vLLM, GSM8K, MMLU, AIME and IMO, arrivals at 0.1 to 1.0
  requests per second; the 20 times case is AIME with 1.0 req/s arrivals and a six-round limit as the comparison. With
  commercial APIs at 0.5 req/s the speedups were 6.2 times (GSM8K), 4.1 (MMLU), 2.7 (AIME) and 2.7 (IMO).
- **Accuracy.** GSM8K 97 against 98 for the baseline and 93 for the best single model; AIME 60 for
  both multi-agent systems against 46.7; IMO 47 against 49.5 and 18.
- **Why fixed rounds hurt.** Average rounds to converge were 2.0 on GSM8K, 2.3 on MMLU and 4.1 on AIME,
  and the slowest model was 11, 18 and 64 times slower than the fastest.
- **Ablations.** On GSM8K with three models, accuracy was 85% at beta 1 and about 98% at beta 2 to 4,
  while time rose from 4.8 s to 9.7 s. On IMO with five models, accuracy stayed near 43% for alpha 3
  to 5 while latency rose from 1346 s to 1695 s; at alpha 1 accuracy was near zero.
- **Weak-strong exchange.** Llama-3.1-8B rose from 3% to 54.4% on AIME after seeing a strong
  model's traces, while DeepSeek-R1 moved by 0 to 2 points after seeing weak traces.
- **Tokens and replicas.** Early termination cut tokens 4.4 times on GSM8K and 1.1 times on IMO.
  Going from 3 to 7 homogeneous replicas cost 23% to 33% more time.

## Limits

- No limitations section and no error bars, seeds or sample counts for the accuracy runs. Baselines
  are the authors' reimplementation of an existing style of system, not the original systems.
- The refinement assumption rests on one small experiment pairing one weak and one strong model;
  same-strength agents, correlated wrong majorities and adversarial agents are untested. The paper
  says a majority may reach the same wrong answer, and stability does not guard against it. The failure
  model is fail-stop only. Only maths and multiple-choice reasoning were tested.
- The multi-instance variant is omitted, no leader-failure experiment is reported, and the paper does
  not say how often the round cap is hit.
- Internal inconsistencies noted by the extraction: the ensemble ablation puts AIME accuracy at 95.8%
  with homogeneous replicas against 60% in the main figure, and IMO accuracy at alpha 3 is about 43%
  against 47% in the main figure. Which single model is the best one is not stated in the text.

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Multi-Agent Failure Modes at Scale]] — related (termination and loop risk)
- [[Loop Termination Design]] — related (stopping rules)
- [[Protocol-Driven Multi-Agent Collaboration]] — related
