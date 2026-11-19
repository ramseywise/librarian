---
title: "LLaDA Large Language Diffusion Model"
tags: [llm, architecture, concept]
summary: "LLaDA is an 8B masked diffusion language model trained from scratch with a 1/t-weighted masked-token loss and sampled by low-confidence remasking; the paper reports parity with LLaMA3 8B on some tasks and a better reversal-poem score than GPT-4o."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-nie-2025-large-language-diffusion-models.md
---

# LLaDA Large Language Diffusion Model

Nie and colleagues ask if a masked diffusion model trained from scratch can show what makes LLMs capable: scaling well, learning in context, and following instructions. Their hypothesis is that those capabilities stem from generative-modelling principles (maximum likelihood, Transformers, scale) rather than from the autoregressive factorisation. Numbers are self-reported.

## Mechanism

- A Transformer **without a causal mask** works as a mask predictor. A ratio t is drawn from U[0,1], every token is masked independently at that ratio, and the model is trained to recover the masked tokens under a loss that sums the log-probability of each masked position's original token, weighted by 1/t and negated; this upper-bounds the negative log-likelihood. For SFT only response tokens are masked and the loss is rescaled by L/l.
- The 8B model is pretrained on 2.3T tokens (0.13 million H800 GPU hours) and fine-tuned on 4.5M SFT pairs.
- **Sampling** is reverse diffusion from a fully masked sequence. **Low-confidence remasking** remasks the s/t fraction of predicted tokens with lowest confidence at each step. A block-diffusion variant (semi-autoregressive remasking) runs the reverse process in fixed-length blocks, autoregressive across blocks.
- The learning-rate scheduler is Warmup-Stable-Decay and classifier-free guidance was studied as an ablation, not used in the main results.

## Results

| Claim | Setup |
|---|---|
| MMLU 65.9; LLaMA3 8B Base scores 65.4. Training tokens: 2.3T versus 15T | Table 1, both re-evaluated under one protocol, likelihood-based, 5-shot, no CFG |
| GSM8K 70.3 against 48.7 for LLaMA3 8B Base | 4-shot; length 1024; sampling is pure diffusion with low-confidence remasking |
| BBH 49.7 against 62.1; HellaSwag 70.5 against 79.1 | LLaMA3 8B Base ahead; 3-shot and 0-shot |
| Matches 1B and 7B ARM baselines trained on the same data up to a 10^23 FLOPs compute budget on six tasks | FLOPs counted as 6ND; the matched comparison does not go beyond 10^23 |
| Reversal poem completion 45.6 against GPT-4o 34.3 (forward: 51.8 against 82.7); Qwen2.5-7B Instruct 38.0 | Instruct model, zero-shot, 496 pairs of Chinese poem sentences |
| Instruct GSM8K 69.4 (SFT alone), while LLaMA3 8B Instruct (SFT plus RL) gets 78.3 | 4-shot, pure diffusion sampling |
| Instruct GSM8K goes from 69.4 to 78.6 and Math from 31.9 to 42.2 with block-style sampling | block length 32 (8 for GSM8K) |
| Low-confidence remasking 70.0 against random remasking 21.3 on GSM8K | Base, length and steps 256 |
| Throughput is 1.5x (GSM8K) and 1.8x (Math) that of LLaMA3 8B using a KV cache, at comparable accuracy | single A100-80GB, batch 1, bf16, output 256, steps 32-256 |
| iGSM unseen math at 4 steps: 64.0 against 38.0 | 100 questions per step count, 4-shot, modulo-5 arithmetic |

Further numbers: GSM8K barely depends on generation length (length 256: 70.0; 512: 70.8; 1024: 70.3); memory 17.03 GB for 512 in and out against 16.70 GB for LLaMA3 without KV cache and 16.32 GB with; CFG raised ARC-C from 45.9 to 47.9. The paper says an earlier masked-diffusion study suggested 16x the ARM compute for equal likelihood, at 10^18 to 10^20 FLOPs, and extends to 10^20-10^23.

## Limits

- Length of the generation is something the user must set; the authors say an adaptive length would be preferable.
- LLaDA-versus-ARM comparisons at matched compute stay under 10^23 FLOPs, and the ARM baseline never reached 8B (a 7B with a different FFN and KV-head setup stood in).
- The model uses no specialised attention, position embeddings or KV cache, and the sampling algorithms are preliminary.
- With no RL alignment the Instruct model trails LLaMA3 8B Instruct; MMLU fell after SFT, which the authors put down to SFT data quality.
- The training data are closed, so gaps relative to LLaMA3 are credited to data without a test that isolates it.
- Each result is a single run, with no seeds or error bars.
- Autoregressive sampling of the Instruct model fails badly (GSM8K 0), pure diffusion needs the |EOS| confidence set to zero, and |EOS| padding in the SFT data ends generation early.
- The models covered are the LLaDA 8B releases from early 2025, which later work has superseded.

## See Also

- [[Block Diffusion Language Models]] — related
- [[MaskGIT Masked Generative Image Transformer]] — prerequisite-for
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[PAPO Process Rewards for Diffusion LLMs]] — related
