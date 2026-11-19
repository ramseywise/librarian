---
title: Qwen and Qwen2.5 Technical Reports
tags: [llm, pretraining-and-data, reference]
summary: "Qwen (2023) and the open-weight Qwen2.5 (2024) are decoder families trained on up to 3T and 18T tokens, notable for training-free context extension (dynamic NTK, LogN, window attention) and, in Qwen2.5, a staged recipe of SFT, DPO and GRPO plus a 1M-token Turbo variant; all figures self-reported."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bai-2023-qwen-technical-report.md
  - data/raw/papers/2026-11-07-qwen-2024-qwen2-5-technical-report.md
---

# Qwen and Qwen2.5 Technical Reports

## Qwen (Bai et al., 2023)

- Models: base 1.8B, 7B and 14B trained on up to 3T tokens; Qwen-Chat, aligned by SFT and then RLHF with PPO, and able to use tools and act as an agent; Code-Qwen and its chat version (7B, 14B); Math-Qwen-Chat (7B, 14B).
- Architecture: a modified LLaMA-style transformer with RoPE positions, untied embeddings (picked from preliminary experiments, costing memory) and a BPE vocabulary of roughly 152K entries that starts from tiktoken's cl100k_base and adds Chinese and other multilingual tokens. The claim that a bigger vocabulary helps rests on unreported preliminary experiments.
- Base results (5-shot, Table 2): Qwen-14B gets 66.3 on MMLU and 72.1 on C-Eval; Qwen-7B gets 58.2 on MMLU.
- Training-free context extension: Qwen-7B was trained at context 2048. On arXiv text, dynamic NTK interpolation combined with LogN and window attention reaches perplexity 3.49 at 8192 tokens; for Qwen-14B the combination is contrasted with 334.65 at 8192 when none are used.

## Qwen2.5 (Qwen Team, 2024)

- Data and models: pre-training data rose from 7T to 18T tokens with model-based filtering. The open dense models span 0.5B to 72B; Turbo and Plus are MoE models behind an API, with sizes and expert counts unstated. In the open-weight table the 0.5B, 1.5B and 3B models tie embeddings and the 7B and larger do not; the layer counts are 24, 28, 36, 28, 48, 64 and 80; and the number of GQA key-value heads is 2, 2, 2, 4, 8, 8 and 8.
- Base results (5-shot): Qwen2.5-72B reaches 86.1 on MMLU, against 84.2 for Qwen2-72B and 85.2 for Llama-3-405B. Qwen2.5-7B, with 6.5B non-embedding parameters (Gemma2-9B has 8.2B), gets 74.2 MMLU, 49.8 MATH and 57.9 HumanEval. Qwen2.5-72B-Instruct gets 83.1 on MATH and 81.2 on Arena-Hard.
- Context: the last pre-training stage lengthens sequences from 4,096 to 32,768 and lifts the RoPE base from 10,000 to 1,000,000 (ABF). Turbo reaches 1M tokens through progressive extension plus YARN and DCA at inference, with 100% passkey retrieval at 1M. MInference-based sparse attention reduces attention compute 12.5x at 1M tokens and speeds time to first token 3.2 to 4.3x. On RULER (128K claimed length) Qwen2.5-72B-Instruct averages 95.1 with DCA plus YARN against 90.8 without, and 88.4 against 67.0 at 128K.
- Post-training: SFT on more than 1M examples (2 epochs, sequence length 32,768, learning rate decaying 7e-6 to 7e-7, weight decay of 0.1, gradient clipping at 1.0); offline RL with about 150,000 DPO pairs (1 epoch, learning rate 7e-7); online GRPO with 8 responses per query and a global batch of 2048. The 72B reward model gets 91.59 on Reward Bench (94.10 for Llama-3.1-Nemotron-70B-Reward) and the best PPE objective average, 69.85.
- Decontamination of pre- and post-training data: a training sequence is removed when its longest common subsequence with a test sequence is 13 tokens or more and covers at least 0.6 of the shorter sequence.

## Limits

- Qwen: baseline figures were lifted from other reports and OpenCompass, so their prompts and settings may differ from the authors' own. The authors admit conventional benchmarks cannot accurately gauge aligned chat models. Compute, hardware, wall-clock time and seeds are unreported and the pretraining data is unreleased. The perplexity extension evidence is limited to arXiv text and does not show far context being used.
- Qwen2.5: no ablation separates the effect of data size, filtering or any post-training stage; pre-training hyperparameters, hardware and compute are missing, and the scaling-law findings come without numbers. Per-size token counts are not given (18T is the figure for the series). The authors admit reward-model benchmark scores fail to predict RL model quality and that cultural nuance (BLEnD) needs more work.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Multi-Query and Grouped-Query Attention]] — prerequisite-for (the key-value head sharing in the Qwen2.5 table)
- [[GRPO Group Relative Policy Optimization]] — prerequisite-for (the online RL stage)
- [[Preference Optimization Algorithms]] — prerequisite-for (the DPO stage)
- [[MMLU, C-Eval and CMMLU Knowledge Exams]] — related
- [[Sliding Window Attention and Rolling Buffer Cache (Mistral 7B)]] — related (another open-weight report)
- [[Mixture-of-Experts Routing and Scaling]] — related (the Turbo and Plus models are MoE)
