---
title: "Memento Case-Bank Retrieval"
tags: [memory, pattern]
summary: "Memento keeps the LLM frozen and improves an agent by storing (state, action, reward) cases and learning only which cases to retrieve, by similarity or by a small learned Q-function; it reports GAIA validation 87.88% Pass@3 and a best retrieval size of four cases (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhou-2025-memento.md
---

# Memento Case-Bank Retrieval

Memento (a 2025 preprint) adapts a deep-research agent without touching model weights. The agent writes each finished attempt into an episodic case bank as a (state, action, reward) tuple. Reading fetches K cases, ranked in one variant by embedding similarity (the non-parametric one) and in the other by a learned Q-function (the parametric one). That learned scorer is a small two-layer network on top of sentence embeddings, fitted as a success-or-failure classifier for retrieved cases; in the planning-only deployment the paper's soft-Q derivation collapses to a plain supervised objective without bootstrapped targets. A GPT-4.1 planner hands steps to an o4-mini executor (o3 on GAIA).

## Results

All figures are self-reported.

- GAIA validation 87.88% Pass@3 and test 79.40% (fourth on the leaderboard as of June 2025). The GAIA runs allow three attempts and build memory on the validation set, so the protocol differs from single-attempt scoring.
- Case-based memory is additive over planning and tools in the ablation: +4.5 F1 on HLE, +3.7 on SimpleQA and +6.7 on DeepResearcher data.
- On DeepResearcher data after five iterations: parametric 85.44, non-parametric 84.85, no case memory 84.47, so the parametric-versus-non-parametric gap is under 1.5 points per iteration.
- Performance peaks at K=4 retrieved cases (average F1 64.5 against 59.9 at K=0) then plateaus or declines; the authors warn of the swamping problem, where retrieval cost outweighs utility.
- Out of distribution, retrieving four cases gained 4.7 to 9.6 points on three held-out datasets.
- A non-reasoning planner beat a reasoning one: GPT-4.1 planner with an o3 executor scored 70.91% on GAIA validation against 63.03% with o3 for both, because o3 often skipped planning or wrote verbose plans that misled the executor.

## Limits

- The case bank saturates at about 3k training items, so it shows nothing about continual learning over a long horizon; no variance or seeds; contamination is acknowledged on DeepResearcher.
- Rewards are binary and deterministic; no test of poisoning, staleness or deletion, and Mem0, A-Mem and MemRL are not compared. The multi-step soft-Q machinery is not what is deployed.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory Intelligence Agent]] — related (uses Memento as its strongest memory baseline)
- [[Self-Learning Agents]] — related
