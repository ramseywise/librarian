---
title: SALE Strategy Auction
tags: [harness, pattern]
summary: SALE has each agent in a pool of different-sized models bid with a short plan, scores bids by plan cost against a peer-jury value, and refines losing bids from memory; on two domains it beat the largest single agent by 2.7 to 3.5 pass@1 points at 25% to 42% lower cost per million tokens (self-reported, one model family).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-alazraki-2026-scaling-small-agents-through-strategy.md
---

# SALE Strategy Auction

Alazraki et al. (Meta Superintelligence Labs and universities, arXiv 2602.02751, v3 June 2026
preprint) assign each task to one agent from a pool of four Qwen3 sizes (4B, 8B, 14B, 32B) by a
mechanism they call an auction. It differs from routers that choose from the task description alone:
selection uses the plans the agents themselves write. Model routing proper belongs to separate
pages; this page covers only this mechanism.

## Mechanism

1. Every agent submits a brief plan, which serves as its bid.
2. Cost is a weight times the agent's price times the plan's token count. Value is a weighted sum
   of the agent's output entropy and a 0-5 score from every agent in the pool, including the bidder
   (the peer jury).
3. The winner minimises cost minus value. Weights are fitted by a min-max mixed-integer program on a
   development set.
4. Agents cheaper than the provisional winner may rebid, using retrieved win and loss plan pairs
   from a memory bank.

The benchmark, HST-Bench, has 753 tasks with complexity set by expert human solution time in five
bins up to 60 minutes, scored by an LLM judge on pass@1; it is released by the authors.

## Results (self-reported)

Setup: greedy decoding for single agents, SALE averaged over 5 random task orderings against
single-run baselines, price calibrated at $0.05, $0.09, $0.16 and $0.36 per million tokens for 4B,
8B, 14B and 32B.

- **Size matters per task.** The 4B agent reached about 87% (deep search) and 92% (coding) of the
  pass@1 of the 32B agent on the easiest tasks, and 25% and 17% on the hardest.
- **Against the best single agent (Qwen3-32B).** Deep search 63.8 to 67.3 pass@1 with cost $0.36 to
  $0.21 (-42%); coding 58.4 to 61.1 with $0.36 to $0.27 (-25%). The abstract gives -52% reliance on
  the largest agent and -35% cost.
- **Routers.** Four task-description routers trained on the same split did worse: on the hardest
  coding bin one scored 6.3 against 22.8 for the best single agent and 26.1 for SALE. One router was
  cheaper than SALE on coding ($0.11 against $0.27), and another tied it on an easy bin.
- **Overhead.** 669 extra tokens per task for deep search and 1,042 for coding; 3.59 s auction time
  against 5-10 minutes of execution. Plan length correlates only moderately with realised trace
  length (Spearman 0.39).
- **Ablations.** Memory shifted the 32B share from 35% to about 17% over a 100-task study. Without peer feedback coding pass@1 fell
  to 48.7; without self-feedback SALE sat near the best single agent. Jury scores correlated 0.74-0.82 with
  human plan ratings given blind, but only 0.36 with task success.
- **Oracle gap.** An oracle choice scored 77.9 (deep search) and 68.4 (coding), above SALE's 67.3 and 61.1.

## Limits

- Coverage is limited to deep search and coding, with one model family with about an 8x price spread; no models
  above 32B. Only tokens are counted as cost; tool calls carry no price, latency is out of scope, and
  cross-family evidence is preliminary (100 tasks).
- The memory bank grows linearly; retrieval at scale, model upgrades and distribution shift are untested.
- Extraction observations: "auction" is a metaphor, with no payments or incentive analysis and a
  central scorer; the strongest baseline is Qwen3-32B and not a frontier model; averaged SALE runs are compared
  with single-run baselines; fitting the weights needs a dev set; gains are a few points.
- Table column order was inferred from the caption in the extraction.

## See Also
- [[Harness Orchestration]] — prerequisite-for
- [[Task Decomposition Patterns]] — related
- [[Multi-Agent Topology Patterns]] — related
