---
title: LoReFT Representation Finetuning
tags: [llm, fine-tuning, concept]
summary: "ReFT trains small interventions on a frozen model's hidden states instead of weight updates; LoReFT edits the residual stream inside a rank-r subspace and uses 15x to 65x fewer parameters than LoRA (self-reported), but is weak on arithmetic reasoning."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-wu-2024-reft.md
  - data/raw/papers/2026-11-06-tie-2025-survey-post-training-large-language.md
---

# LoReFT Representation Finetuning

Wu et al. (Stanford, arXiv 2404.03592v3, an under-review preprint) propose ReFT: learn interventions on hidden states at chosen positions while the language model stays frozen. Not to be confused with Reinforced Fine-Tuning (SFT warm-up then PPO on sampled chains of thought), which a post-training survey also abbreviates ReFT.

## Mechanism

LoReFT replaces a hidden state h with h plus R-transpose applied to (Wh + b - Rh), where the rows of R (r by d) are orthonormal. R, W and b are the only learned parts. It builds on distributed interchange interventions: where those swap in a source subspace value, LoReFT replaces it with a learned linear projection Wh + b. The edit is applied at p prefix positions and s suffix positions of the prompt, so inference pays for a fixed count of positions. DiReFT, a variant, scores lower. The method is implemented in the pyreft library (`get_reft_model` with a `ReftConfig`).

## Reported results (self-reported; baselines copied from other papers, not rerun)

- Commonsense (eight tasks, 170K examples, mean of 3 seeds): LLaMA-7B averages 80.2 for LoReFT (0.031% of parameters) against 78.1 for DoRA (0.838%) and 74.7 for LoRA (0.826%); Llama-3 8B 86.6 against 85.2 and 80.8. With epochs matched to DoRA's step count LoReFT still averaged 79.5 (7B) and 83.1 (13B).
- Instruction following: Llama-2 7B trained on Ultrafeedback, Alpaca-Eval v1.0 against text-davinci-003 with a GPT-4 judge: 85.60 for LoReFT (0.0039%) against 80.93 full fine-tuning, 81.48 LoRA and 81.69 RED; mean of 2 seeds. With 1K examples it scores 81.91 in 18 minutes on one A100 40G, about 1 MB on disk.
- GLUE: RoBERTa-base scores 84.2 (0.015% of parameters), with LoRA at 84.7 and full finetuning at 85.6; RoBERTa-large 88.2 against 88.1 and 88.6.
- Arithmetic is a loss: LLaMA-7B average 42.6 against 46.9 for LoRA (GSM8K 26.0 against 37.5). It does beat prefix-tuning. The authors guess greater length reduces the intervention's effect.
- Ablation: dropping orthogonality or the difference term changes arithmetic accuracy little at equal parameters (42.6, 42.9, 42.4); input-independent versions are clearly worse (37.1 and 31.3).
- Author advice: intervene on multiple positions, start on all layers then shrink, higher rank may not help (start at 4 or lower than 32), tie intervention weights.
- Demonstrations: a rank-1 input-independent intervention at one layer stores up to 2,048 tokens of Alice in Wonderland with 100% recovery (LLaMA-1 7B, 4,097 parameters; random token sequences only up to 128); different orthogonal subspaces trained on different tasks combine (qualitative only); five examples adapt Llama-2-Chat to imitate GOODY-2 (qualitative).
- Overhead: interventions cannot be merged into weights; for 10 layers at rank 8 applied to the final prompt token and 256 generated tokens, the added time is about 0.05 second.

## Limits

- Mostly LLaMA-family models; Llama-3 8B only on commonsense; the space of hyperparameters is large and the search is manual. The authors have no explanation for why ReFT works.
- Baselines in the commonsense, arithmetic and instruction tables come from other papers; the authors tuned on dev sets and state that earlier PEFT papers tuned against test sets.
- The conclusion's claim of beating all existing PEFTs is stronger than the tables support, given arithmetic. On GLUE, LoReFT falls short of LoRA with RoBERTa-base, and its median trails VeRA and LoRA in an appendix table.
- Dated: 2024 models only; nothing on RL or preference optimisation.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family overview)
- [[DoRA Weight-Decomposed Low-Rank Adaptation]] — alternative-to (a weight-space method it is compared with)
- [[BitFit Bias-Term Fine-Tuning]] — related (a baseline in the paper)
- [[Prefix-Tuning and Prompt Tuning]] — alternative-to (an input-side method it beats on arithmetic)
