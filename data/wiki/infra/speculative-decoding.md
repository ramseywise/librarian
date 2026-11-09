---
title: Speculative Decoding
tags: [infra, concept]
summary: "Speculative decoding has a cheap drafter propose several tokens that the target model verifies in one parallel pass, with the rejection rule keeping outputs identical; this page collects the survey's reported speedups and three drafter variants that avoid a second model."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xu-2024-survey-resource-efficient-llm-multimodal.md
  - data/raw/papers/2026-11-07-liu-2025-tidar.md
  - data/raw/papers/2026-11-08-monea-2023-pass.md
  - data/raw/papers/2026-11-07-bercovich-2026-nemotron-labs-3-puzzle-75b.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch08-addressing-constraints.md
---

# Speculative Decoding

Decoding one token per forward pass leaves hardware idle at small batch. In speculative decoding, a drafter proposes γ tokens and the large model verifies them in a single parallel pass, accepting a prefix. A rejection rule makes the final result identical to decoding with the large model alone, which the survey of resource-efficient models (Xu et al., 2024) calls complete accuracy. See [[LLM Inference Economics]] for the prefill and decode split behind this.

## Reported speedups

The survey's figures are the cited papers' own claims, with hardware and baselines mostly unstated, so they are not comparable with each other: 2-3x on a T5X model for the original method, 2.13x wall-clock for SpecTr, 1.73x for Draft & Verify on Llama-2, and over 2x for LLMA. The survey lists Medusa, lookahead decoding and Draft & Verify as methods without a separate draft model.

## Drafters without a second model

- [[PaSS Parallel Speculative Sampling]] appends learned look-ahead embeddings to a frozen model: up to 30% faster on LLaMA 7B (self-reported), lossless.
- [[TiDAR Diffusion Drafting]] drafts with one-step diffusion in the same forward as verification and needs continual pretraining; speedups are at batch size 1 only (self-reported), and outputs are not guaranteed identical.
- [[Nemotron Puzzle Hybrid MoE Compression]] attaches a shared multi-token-prediction head; with it the compressed model reached 4.63x against 2.03x single-step, relative to the larger parent (self-reported, 8xB200, draft length 3).

## Worked vLLM example (Lakshmanan and Hapke, ch. 8)

With vLLM, Gemma 2 9B as target and Gemma 2 2B as draft at num_speculative_tokens=5, the chapter reads about 14.2% faster than the target alone (self-reported, read from a figure); hardware, prompts and run count are not stated (the numbers come from a repo script). The authors concede setting num_speculative_tokens too high can make it slower than running the target by itself, so it should be tuned.

## Limits

- Three of the five sources are single-paper claims on their own setups; the survey is secondary.
- The extraction notes the survey's description has a notation slip (it says the large model drafts) and that it covers work only to early 2024, using Medusa and lookahead as its examples.
- The acceptance-length and wall-time numbers behind these methods depend on model, temperature and batch size; PaSS reports larger gains at lower temperature.
- Worked vLLM example: single run, unstated hardware; the vLLM speculative_model argument has since changed.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (where the draft-and-verify lever sits among serving levers)
- [[KV Cache Reduction Methods]] — related (the survey's other decode-side levers)
- [[Speculative Decoding Variants]] — related (draft-model, EAGLE and Medusa variants from other sources)
- [[Medusa Decoding Heads]] — related (the survey's example of a drafter-free method)
