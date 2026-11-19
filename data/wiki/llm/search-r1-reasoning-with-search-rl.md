---
title: Search-R1 Reasoning with Search RL
tags: [llm, agent-training, pattern]
summary: "Search-R1 trains an LLM with outcome-only reinforcement learning to interleave reasoning with live search calls, masking retrieved text out of the loss; on seven QA sets it beat RAG and prompting baselines, and removing the mask cost 0.088 average exact match at 7B (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-jin-2025-search-r1.md
---

# Search-R1 Reasoning with Search RL

Search-R1 (Jin, Zeng, Yue and colleagues, COLM 2025) asks whether a model can learn, from a final-answer reward alone, to alternate between reasoning and repeated calls to a real search engine. The authors hypothesise that prompting a reasoning model to use search is suboptimal, and that RL with an outcome reward plus loss masking of retrieved tokens beats RAG, prompting, SFT and RL that has no search. The paper presents the method as an extension of DeepSeek-R1-Zero-style RL to a search-augmented setting.

## Mechanism

- **The search engine is part of the environment.** The policy emits `<think>`, `<search>` and `<answer>` segments, and results from the search call are wrapped in `<information>` tags.
- **Retrieved-token loss masking.** Only tokens the LLM itself generated enter the policy-gradient objective; the retrieved text is left out. The same rule appears in [[Post-Training for Agents]] as "loss-mask environment tokens".
- **Reward.** Exact match between the predicted and gold answer, with no format or process reward.
- **Setup.** Training data is NQ and HotpotQA merged. Models are Qwen2.5 3B and 7B (14B in the appendix). The retriever is E5 over a 2018 Wikipedia dump, with 3 passages per search and a maximum of 4 action turns. PPO is the default algorithm and GRPO the alternative.

## Results (self-reported)

Every method shares the retriever, training data and base models; evaluation covers seven QA datasets.

| Finding | Number | Setup |
|---|---|---|
| Relative gain over RAG baselines | 24% (7B), 20% (3B) | average over seven datasets |
| Average exact match, Search-R1-base | 0.431 vs 0.304 for RAG | Qwen2.5-7B, PPO; the RAG baseline uses the instruct model |
| Rejection sampling with the same loop | 0.348 | Qwen2.5-7B, five candidates per prompt, correct trajectories fine-tuned |
| Without loss masking | 0.343 (7B), 0.262 (3B) vs 0.431 and 0.303 | PPO, base models |
| PPO vs GRPO | 0.431 vs 0.350 (base); 0.385 vs 0.396 (instruct) | Qwen2.5-7B, GRPO group size 5 |
| Top-k passages | 0.375 (k=1), 0.431 (k=3), 0.400 (k=5) | Qwen2.5-7B-Base, PPO, step 500 |
| GRPO group size | 0.410 at size 1, 0.350 at size 5 | Qwen2.5-7B-Base, 500 steps |
| 14B | 0.479 | same setup as the main results |

GRPO converged faster than PPO but its reward collapsed over longer training, while PPO stayed stable. Instruct models started higher and converged faster, yet base and instruct reached very similar final training reward.

## Limits

- One run per configuration, with no seeds, variance or significance tests.
- The paper does not give training set size, optimiser, precision or run time.
- Only an exact-match reward is used; format rewards and richer rewards are left to future work.
- When GRPO diverged, checkpoints were chosen from the training-reward curve (the group-size study used the last valid checkpoint).
- The action budget is fixed at 4 turns, and the corpus and retriever are one Wikipedia dump and E5.
- Listed as future work: other search strategies, retrieval triggered by uncertainty, further tools and multimodal reasoning.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Search-o1 Reason-in-Documents]] — alternative-to (inference-time search inside a reasoning model, no RL; a baseline in this paper)
- [[ReAct Synergizing Reasoning and Acting]] — prerequisite-for
- [[Dr. Zero Self-Evolving Search Agents]] — extends (replaces the human QA training data with a self-generated curriculum)
- [[DAPO]] — related
- [[SEM First-Answer-Gated Search Reward]] — extends (first-answer-gated reward to cut needless search)
