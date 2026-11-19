---
title: SEM First-Answer-Gated Search Reward
tags: [llm, agent-training, pattern]
summary: "SEM trains a search-using model with GRPO to answer first and search only if the first answer is wrong, by paying reward only on a correct no-search first answer or on a post-search answer after a wrong one; the paper reports a very low search ratio on questions that need none (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-sha-2025-sem.md
---

# SEM First-Answer-Gated Search Reward

SEM (Sha et al., Ant Group, May 2025) targets a model that searches even when it already knows the answer. Its reward is neither a per-call cost nor a budget. It works as a binary gate on the correctness of the first answer.

## Mechanism

The output template is: think, a preliminary `<answer>`, optionally a search and its result, think, a final `<answer>`. With `a1` the first answer and `a2` the post-search answer:

- Reward is zero when the structure is invalid (bad format or tag order).
- If F1(a1) reaches a threshold tau with no search and a single think/answer, the reward is F1(a1). A search after a correct first answer pays 0; that is the penalty.
- If F1(a1) is below tau and the search-result format is valid, the reward is F1(a2).

Training uses GRPO on a balanced mix of MuSiQue (questions the model is expected not to know, so searching is right) and MMLU (questions it is expected to know). The known/unknown label is implicit in the data source. Built on ReSearch, Verl and FlashRAG with Qwen2.5-7B-Instruct and 14B-Instruct; 8 A100s, batch size 8, 200 steps. The value of tau and the mix sizes are not stated.

## Reported results (self-reported)

Setup: single run per cell, retrieval over wiki18-100w via FlashRAG, baselines Naive RAG and ReSearch retrained on the authors' data. EM is exact match, SR is search ratio.

| Benchmark (7B) | SEM EM / SR | Naive RAG EM / SR | ReSearch EM / SR |
|---|---|---|---|
| MMLU | 70.88 / 1.77% | 12.48 / 47.98% | 69.84 / 0.00% |
| HotpotQA | 35.84 / 97.54% | 18.01 / 88.52% | 21.75 / 0.08% |

- MuSiQue 7B: SEM 15.59 EM at 97.35% SR against 7.19 for Naive RAG. At 14B, HotpotQA SEM 40.42 EM vs 35.11 (Naive RAG) and 33.29 (ReSearch); MuSiQue, 20.56 for SEM, 13.52 for Naive RAG and 14.43 for ReSearch.
- Out of domain on GSM8K the picture is mixed: at 14B SEM scores 79.37 at 0.76% SR, against 83.93 for Naive RAG (14.71% SR) and 50.41 for ReSearch (55.19%); at 7B ReSearch scores 82.63 at 0% SR against SEM's 71.79 at 14.63%.
- Training curves: the paper says ReSearch fluctuates more and gains more slowly, especially at 7B.

## Limits

- One run per cell, only Qwen2.5 at 7B and 14B, no ablations (no reward term, threshold or data-mix test), and Search-R1 is not compared; efficiency is measured only as search ratio, with no cost or latency.
- ReSearch ends at 0.08% SR on HotpotQA at 7B, so the baseline is effectively broken in this setup; the authors blame the data mix for "gradient explosion" without showing it.
- The reward assumes a correct first answer is possible without retrieval, and the known/unknown split is by dataset, with no calibration of what the model actually knows.
- The text contradicts its tables: it says SEM is superior on all benchmarks, but at 14B the LLM-judge score on HotpotQA is 58.43 against 59.55 for Naive RAG; it says the 7B model searched 0.76% on GSM8K, but that is the 14B figure (7B is 14.63%); and Table 2 lists the same Naive RAG EM of 12.48 for MMLU and for GSM8K at 7B, which may be a copy error.
- The GSM8K transfer is described as trained on MMLU only, though training used MuSiQue plus MMLU.
- Case studies use placeholder retrieval text; the authors state no limitations.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[DAPO]] — related (GRPO-family training recipe)
- [[Tool-N1 Binary-Reward Tool-Calling RL]] — alternative-to (a different reward shape for tool use)
- [[HotpotQA]] — related
- [[MuSiQue Multihop QA]] — related
- [[Search-R1 Reasoning with Search RL]] — alternative-to (a different way to train search use)
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for
