---
title: DreamLLM Interleaved Comprehension and Creation
tags: [multimodal, concept]
summary: "DreamLLM trains a Vicuna-7B to read and generate images and interleaved documents end to end, using learnable dream queries and score distillation through a frozen Stable Diffusion decoder."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-dong-2023-dreamllm.md
---

# DreamLLM Interleaved Comprehension and Creation

DreamLLM aims for a multimodal language model that both comprehends and creates raw images and interleaved documents. Its hypothesis is that modelling image and text posteriors in raw space, rather than aligning outputs to CLIP, lets creation and comprehension help each other. The model is Vicuna-7B with a frozen CLIP-L/14 encoder (linear projector) for input and a frozen SDv2.1 as image decoder, conditioned through 64 learnable dream queries and a linear projector. A dream token marks where images go. The frozen diffusion decoder's noise-prediction loss, used as score distillation, sends gradients back into the LLM, the queries and the projectors. Training has three stages: alignment, interleaved generative pretraining, and SFT (about 6, 10 and 1.5 hours on 128 A800 GPUs).

## Reported results (self-reported)

- Zero-shot MS-COCO FID 8.46 (8 samples per prompt, CLIP-score ranking, CFG 2.0) (self-reported), against Emu-13B at 11.66, GILL-8B at 12.20, CM3Leon-7B at 10.82, and the frozen SDv2.1 decoder by itself at 12.43. On long-caption LN-COCO: 20.53 against 34.26.
- Dream-query count: 64 gives FID 8.46, 32 gives 9.56, 128 gives 14.24. Creation-only training reaches 8.50 (8.57 with a CLIP alignment loss).
- Adding the CLIP alignment loss to joint training made it fail to converge.
- Joint learning gives MM-Vet 35.9 and VQAv2 56.6, against 34.4 and 54.3 for comprehension-only, a small delta from single runs. Zero-shot VQAv2 is 56.6, +16.6 over Emu-13B (40.0). MMBench dev is 49.9 in the tables.
- Against a rewrite-then-generate baseline: COCO FID 8.46 against 11.91, VQAv2 56.6 against 54.2.
- Document-conditioned image synthesis FID 36.62 against 74.77 for SD (15K held-out documents). In human evaluation 60.68% of generated documents were judged supported against 77.24% for ground truth.
- Latency over SD is 3.65 s against 3.46 s at 50 steps. MMLU falls from 45.0 to 41.8.

## Limits

- Only 7B tested. MMC4 data is noisy, hurting style; image consistency is weak; it fails on multi-image compositional prompts. Image quality is bounded by the frozen decoder.
- Synergy evidence rests on small ablation deltas from single runs; the human-eval rubric is unspecified.
- Internal inconsistency: the abstract gives MMBench as 49.1 while the tables give 49.9.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[Emu Generative Pretraining in Multimodality]] — alternative-to
- [[MMBench]] — related (benchmark used)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (input encoder)
