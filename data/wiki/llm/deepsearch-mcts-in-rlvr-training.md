---
title: DeepSearch MCTS in RLVR Training
tags: [llm, reinforcement-learning, pattern]
summary: "DeepSearch puts Monte Carlo tree search inside RLVR training (global frontier selection, entropy-guided negatives, a replay buffer, Tree-GRPO) on a 1.5B math model; the headline gain is about one point over the previous 1.5B result."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-wu-2025-deepsearch.md
---

# DeepSearch MCTS in RLVR Training

Wu et al. (ICLR 2026, arXiv 2509.25454v4) run tree search during RLVR training rather than only at inference. The authors argue that RLVR bottlenecks come from the quality of exploration, not insufficient training time. The paper cites training plateaus after thousands of steps from earlier work and does not re-test them directly.

## Method

A node is a 256-token step with 8 children and a maximum depth of 64; sibling choice uses UCT (lambda 2.0). A global frontier score `F(s) = l1*tanh(Q_parent) + l2*H(pi(s|o_s)) + l3*sqrt(d/d_T)` (defaults l1 0.4, l3 0.01) picks which node to expand across the tree. Values are backed up with an asymmetric constrained q-update with depth decay (gamma_min 0.1). When search finds no correct answer, the lowest-entropy (most confident) wrong trajectory is backpropagated. A replay buffer caches solutions over five adaptive rounds. Tree-GRPO applies tanh soft clipping to q, takes Clip-Higher from DAPO (0.2 and 0.28), drops the KL term and uses a mean-only advantage `q(s_j) - mean`. The terminal reward is +1 for a correct answer and -1 for a wrong or unfinished one; using the outcome reward at every node collapses it back to [[DAPO]]. Training setup: veRL, learning rate 1e-6, global batch 256, 8 rollouts for each prompt, responses up to 16,384 tokens, 100 steps.

## Results (self-reported)

The model starts from Nemotron-Research-Reasoning-Qwen-1.5B v2 and trains on DeepMath-103K; scores are pass@1 over 32 samples on six math benchmarks:

- Average 62.95 against 61.70 for the previous best (AIME24 53.65 against 51.77, AMC23 90.39 against 88.83).
- Continuing DAPO with a KL term: 1,875 extra steps cost 1,883.2 GPU hours for 62.02, 325 steps cost 326.4 hours for 61.78, and 785 steps cost 788.8 hours for 62.08. DeepSearch reaches 62.95 after 50 additional steps and about 330 GPU hours, which the authors call 5.7x fewer hours than the 1,883.2 (and 72x fewer than the 24,000 hours credited to Nemotron v2).
- Ablation, averaged over the six benchmarks from a 61.70 base: plain DeepSearch 60.27; the new q-update gives 61.38 with coarse scores and 61.85 with fine-grained ones; adding standard advantage normalisation 62.27 or mean-only normalisation 62.32; adding global frontier selection on top 62.95. According to the extraction, the improvement over base mostly comes from the q-update, per-node advantages and normalisation instead of from search alone.
- Which wrong trajectory is used as the negative matters: the most confident gives 62.95, a random one 62.09 and the least confident 61.90.
- Across 1.2K very hard DeepMath problems, frontier selection in place of plain UCT lowered iterations from 209.6 to 187.7 and raised trajectory reward (-0.82 before, -0.65 after). A linear depth bonus reduced time per tree by 59% but left reward at -0.76.
- Generation is over 99% of per-tree time (1060.76 ms per tree); 256-token expansions were best among 128 to 1024.

## Limits

- Scope is math, one 1.5B model and one training set; benchmark tables carry no seeds or variance, the margins are about a point, and the ablation is a single run.
- The 5.7x and 72x comparisons are against the authors' own extension of DAPO. Table 2 names DeepSeek-R1-Distill-Qwen-1.5B as the starting model, while Appendix A.1 names Nemotron v2, an inconsistency within the paper; a GPU-hour cell is also garbled in the extraction.
- Verifiable rewards are required, and the frontier function and expansion width are hand-set heuristics rather than learned. The claim about fewer "wait" loops is based on 6 selected cases.

## See Also
- [[DAPO]] — prerequisite-for (Clip-Higher and the extended-training baseline)
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for
- [[Adaptive Branching MCTS]] — related (tree search at inference time)
- [[RLVR Pass@k Reasoning Boundary]] — related
- [[Outcome vs Process Reward Models]] — related (node-level credit without a learned step scorer)
