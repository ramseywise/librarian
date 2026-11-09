---
title: Medusa Decoding Heads
tags: [infra, concept]
summary: "Medusa adds several small feed-forward heads on the model's last hidden state, each predicting a further-ahead token, and verifies a tree of candidates in one pass with a tree attention mask; no separate draft model is needed."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-cai-2024-medusa.md
---

# Medusa Decoding Heads

Cai et al. ask whether additional prediction heads attached to the final hidden state of the language model, with candidates checked through tree attention, can accelerate decoding where speculative decoding would need a second draft model. K heads are added; head k predicts the token k+1 steps ahead as softmax(W2 (SiLU(W1 h) + h)), a single feed-forward layer with a residual connection, with W2 initialised from the LM head and W1 at zero. The top-s_k predictions of each head form a candidate tree (a Cartesian product, or a greedily optimised sparse tree), and one forward pass verifies all candidates under a tree attention mask.

Two recipes: Medusa-1 trains the heads on a frozen backbone; Medusa-2 trains heads and backbone together with LoRA or QLoRA, a combined loss L_LM + lambda0 L_MEDUSA-1, differential learning rates and a head warmup. Self-distillation provides training data in cases where the original data is missing or the model was tuned with RLHF. A typical-acceptance scheme replaces rejection sampling. The paper defines acceleration rate as average tokens decoded per step, overhead as per-step latency relative to vanilla decoding, and speedup as acceleration rate divided by overhead.

## Results (all self-reported)

- Setup: Vicuna-7B v1.5 with heads trained on ShareGPT, measured on MT-Bench at batch size 1 against a HuggingFace baseline. Result: 2.18x speedup with Medusa-1 and 2.83x with Medusa-2, with no quality loss for Medusa-1.
- Vicuna-13B, same setup: 2.33x (Medusa-1) and 2.83x (Medusa-2).
- Self-distilled models run lower: Vicuna-33B Medusa-2 reaches 2.35x (acceptance rate 3.01, overhead 1.27, MT-Bench quality +0.05, about 100k self-distilled samples); Zephyr-7B reaches 2.66x with quality -0.07.
- Speculative decoding with open-source draft models (Llama-68M/160M, Tiny-Llama, Tiny-Vicuna) gives 1.47x, 1.56x and 1.60x on Vicuna-7B/13B/33B, which is below Medusa-2 on 7B and 13B (MT-Bench, batch 1).
- Vicuna-7B ladder: heads without tree attention about 1.5x, with tree attention about 1.9x, optimised tree about 2.2x, Medusa-2 about 2.8x.
- Medusa-1 training for Vicuna-7B needs about 5 hours on a single A100 PCIE and 60k ShareGPT samples. Fine-tuning the backbone directly with the heads lowers MT-Bench quality (5.925 against a 6.17 baseline), while Medusa-1 scores 6.23 and Medusa-2 6.18.
- A sparse tree tuned to 64 nodes achieves a higher acceleration rate than a dense 256-node tree (Medusa-2 on Vicuna-7B, MT-Bench writing and roleplay categories).
- A simulation on a simplified Llama-7B block (A100 80GB PCIe, sequence 1024) finds speedup dropping once candidates pass roughly 64 tokens and once the batch is larger than 32.

## Limits

- Main experiments use batch size 1; larger batches appear only in the simulation, plus a note that TensorRT and TGI handle them.
- Self-distilled models see smaller speedups than ShareGPT-trained ones; for Vicuna-33B the authors suspect a mismatch in the data.
- Typical acceptance does not keep the original output distribution, which the authors consider unnecessary to match.
- No seeds, variance or hardware are given for the main speed results.
- Draft models in the speculative-decoding baselines are open-source substitutes for the proprietary originals.

## See Also

- [[LLM Inference Economics]] — related (speculative decoding is one of its latency levers)
- [[Multi-Query and Grouped-Query Attention]] — related (another decode-time speed method)
- [[DeepSpeed Inference and ZeRO-Inference]] — related
- [[Speculative Decoding Variants]] — prerequisite-for
- [[PaSS Parallel Speculative Sampling]] — alternative-to (look-ahead embeddings instead of added heads)
