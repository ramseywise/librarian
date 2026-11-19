---
title: "Block Diffusion Language Models"
tags: [llm, architecture, concept]
summary: "BD3-LM is autoregressive over blocks of tokens and discrete diffusion within each block, giving variable-length generation and KV caching; data-driven clipped noise schedules cut training-loss variance and the perplexity gap to autoregressive models."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-arriola-2025-block-diffusion.md
---

# Block Diffusion Language Models

Arriola and colleagues ask whether a language model that sits between autoregressive and discrete diffusion can generate sequences of any length, use KV caching, and beat earlier diffusion models on perplexity. Their hypothesis: gradient variance contributes strongly to the perplexity gap separating diffusion from autoregressive (AR) models. Numbers are self-reported.

## Mechanism

- **BD3-LM**, the block discrete denoising diffusion language model: the sequence is cut into blocks of L' tokens, and p(x) multiplies, over blocks, a masked-diffusion conditional that sees the earlier blocks. One transformer with block-causal attention over the concatenated noisy and clean sequence parameterises it, so training uses the whole batch of tokens in a single vectorised forward pass.
- A base model is first pretrained with L' = L, then fine-tuned for each block size using a learned, clipped range of mask rates.
- **Clipped noise schedules:** data-driven schedules lower the variance of the training objective. With L' = 1 on LM1B (16B tokens), a full-masking schedule closes a 2-point perplexity gap to AR (AR 22.88) and variance after 328M tokens falls from 1.52 (NELBO) to 0.11. For L' = 4, a clipped U[0.45, 0.95] schedule reduces variance from 23.45 to 6.24 relative to a linear schedule (linear perplexity 30.18).

## Results

| Claim | Setup |
|---|---|
| Best diffusion test perplexity on OWT at L' = 4, still behind AR: AR gets 17.54, MDLM <=22.98 and SEDD <=24.10 | 110M transformer on OpenWebText, 524B tokens, context length 1024, GPT2 tokenizer |
| LM1B perplexity <=28.23 against MDLM <=31.78 and AR 22.83; up to 13% better than MDLM | 110M model, 65B tokens, wrapped context of 128, bert-base-uncased tokenizer |
| Generative perplexity (scored by GPT2-Large) 25.7, versus MDLM 46.8, SEDD 52.0 and AR 14.1 at L = 1024; 23.6 against 41.3 and AR 13.2 at L = 2048 | 300 samples, OWT models, nucleus p = 0.9 |
| SSD-LM (400M): Gen. PPL 37.2 at 1K steps per block with 40K NFEs; 281.3 at T = 25 | L = 1024 |
| L' = 16 generates up to 9982 tokens (median 798) against SEDD max 1024 | 500 samples |
| Zero-shot Pubmed perplexity 42.52 against AR 48.59 | OWT-trained L' = 4 |
| Vectorised training 20-25% faster than two forward passes; FlexAttention mask up to about 5x faster than naive attention | training; single A5000, L = 1024, batch 16 |

## Limits

- Training costs more than regular diffusion training; the vectorised algorithm keeps it under 2x diffusion training speed.
- Because blocks come out one after another, small blocks may inherit AR's limits on speed and controllability; the right block size depends on the task.
- Perplexity remains behind AR (OWT 20.73 against 17.54 at best).
- The extraction gives the AR LM1B perplexity as 22.88 (L' = 1, 16B tokens) and as 22.83 (65B tokens) and does not reconcile the two.
- Only 110M-parameter models were trained, with no seeds or run-to-run variance and no wall-clock inference benchmark.

## See Also

- [[LLaDA Large Language Diffusion Model]] — related (LLaDA's block-style sampling is supported without retraining, per the LLaDA extraction)
- [[Transformer Architecture]] — prerequisite-for
- [[PAPO Process Rewards for Diffusion LLMs]] — related
