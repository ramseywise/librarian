---
title: LLaMA-Adapter Zero-Initialized Attention
tags: [llm, fine-tuning, concept]
summary: "LLaMA-Adapter prefixes learnable prompts to the top layers of a frozen LLaMA and scales their attention by a gate that starts at zero, so training does not disturb the model early; 1.2M trainable parameters (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhang-2023-llama-adapter.md
---

# LLaMA-Adapter Zero-Initialized Attention

Zhang et al. (ICLR 2024 version, arXiv 2303.16199) turn a frozen LLaMA-7B into an instruction follower by training only a small set of prefix prompts. Their hypothesis is that randomly initialised prompts disturb the pretrained model early in training, so the instruction signal should be injected progressively.

## Mechanism

Learnable prompts of length K are prepended to the word tokens in the top L layers. The attention scores over the prompt positions get a separate softmax, scaled by tanh(g_l); the gate g_l begins at zero and is learned per head. The scores over the ordinary tokens keep a plain softmax, and the two parts are concatenated. A multimodal variant projects frozen CLIP image features and adds them to the prompts elementwise.

## Reported results (self-reported; LLaMA-7B unless stated)

- Cost: 1.2M trainable parameters, about one hour on 8 A100 GPUs on 52K Alpaca data for 5 epochs, against 3 hours for Alpaca 7B and 1.5 hours for Alpaca-LoRA at 4.2M parameters.
- Gate ablation, on multimodal ScienceQA validation (K=10, L=30): random initialisation reached 40.77%, near random choice (39.83); zero initialisation was 43.08 points higher.
- Multimodal LLaMA-Adapter (1.8M tuned parameters) scored 85.19 on ScienceQA test against 83.99 for GPT-4 chain of thought; the text-only variant scored 78.31 and the visual condition added 6.88.
- On ScienceQA validation, with LLaMA-7B and prompts inserted into the last L layers, L=30 gave 83.85 accuracy against 81.03 for all 32 and 55.95 for 10.
- Open LLM benchmark average (ARC, HellaSwag, MMLU, TruthfulQA, all trained on Alpaca data): 52.2 against 49.23 for Alpaca and 50.73 for Alpaca-LoRA; LoRA at ranks 2 to 16 averaged 50.7 to 50.9. MMLU alone was lower than Alpaca-LoRA (34.9 against 37.1).
- Zero-init attention was also applied to ViT-B/16 on VTAB-1k (Natural 81.74 against 78.48 for VPT) and RoBERTa-large on SQuAD 2.0 (F1 87.2 against 85.5 for P-tuning v2, 89.4 for full).
- MME perception: 973 against 503 for LLaVA and 867 for MiniGPT-4, with a two-stage training; adding 204K VQAv2 examples raised total MME from 1222 to 1618.

## Limits

- No seeds, variances or significance tests. Optimiser, schedule, sequence length and precision are not stated.
- Instruction-following quality was judged by GPT-4 on 80 questions, with win counts only in a figure.
- The zero-init ablation was run on multimodal ScienceQA, not on language instruction following.
- Internal tension: the layer ablation shows 30 layers beating all 32, while the text elsewhere recommends inserting at every layer as a generally sound choice.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for (the family overview)
- [[Prefix-Tuning and Prompt Tuning]] — prerequisite-for (layer-wise prompts that this adds a gate to)
- [[LLaVA Visual Instruction Tuning]] — alternative-to (a competing way to give LLaMA visual instruction following)
- [[AdapterDrop Efficient Adapters]] — related
