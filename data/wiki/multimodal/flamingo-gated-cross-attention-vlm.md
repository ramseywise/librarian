---
title: Flamingo Gated Cross-Attention VLM
tags: [multimodal, concept]
summary: "Flamingo keeps a pretrained vision encoder and a Chinchilla language model frozen and trains a Perceiver Resampler plus tanh-gated cross-attention layers on interleaved web data, giving few-shot prompting on image and video tasks (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-alayrac-2022-flamingo.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch03-multimodal-architectures.md
---

# Flamingo Gated Cross-Attention VLM

Alayrac et al. (NeurIPS 2022, arXiv 2204.14198) ask whether a model that connects a vision encoder and a language model, both frozen, and is trained on web pages mixing images with text, can learn new vision-language tasks from only a few examples supplied in the prompt. The paper lists [[Frozen Visual Prefix Few-Shot Learning]] as the work it extends.

## Mechanism

- A contrastively pretrained NFNet-F6 encoder feeds a **Perceiver Resampler**, which uses learned latent queries to compress image or video features of any count down to 64 tokens for the language model to see.
- New gated cross-attention dense layers are inserted between the layers of a frozen Chinchilla LM, in 1.4B, 7B and 70B variants. Each carries a tanh gate initialised at 0, so the frozen LM is unchanged at the start of training.
- Training uses a weighted next-token loss over M3W (interleaved web pages), ALIGN, LTIP and VTP. Evaluation uses prompting alone across 16 benchmarks; one held-out subset played no part in design choices.
- **RICES** selects in-context examples by retrieving support images that are similar under frozen encoder features.

## Results (self-reported)

- Flamingo-80B, prompted with 32 examples and given no weight updates, exceeds fine-tuned state-of-the-art results on six of the 16 benchmarks (only 15 are comparable, as one has no fine-tuned result) using about 1000x less task-specific data (self-reported).
- Ablations on the 3B model, scored as an Overall number against a 70.7 baseline (self-reported): fine-tuning the pretrained LM gives 62.7; training the LM from scratch 57.8; dropping M3W 53.4; dropping image-text pairs 60.9; round-robin dataset sampling instead of gradient accumulation 62.9; no tanh gating 66.5, with instability.
- In an ablation on Flamingo-3B, inserting gated cross-attention only every 4th block gave a step time of 1.02 s against 1.74 s (66% faster) and 68.8 Overall against 70.7, 1.9 lower (self-reported). This is an ablation row, not the final model.
- The NFNet-F6 encoder scores 70.7 against 64.9 for CLIP ViT-L/14, and attending only to the most recent image scores 70.7 against 63.5 for attending to all previous images (3B ablation, self-reported).
- Training the largest model took 15 days on 1536 TPUv4 chips (self-reported).
- Of 185M M3W images, 1314 candidates matched eval sets, 125 of them exact duplicates (self-reported). A COCO CIDEr gap between female and male subjects at 32 shots was not significant, with the lowest p-value 0.25 over four comparisons (self-reported).

The textbook chapter on multimodal architectures reports the same design but places the cross-attention layers every 7th layer in the 80B model, and gives its own ablation scores (68.4 to 46.9 without M3W, 56.5 without image-text pairs) with no metric stated; those numbers are reported from the paper, not rerun.

## Limits

- Inherits LM weaknesses: hallucination and poor length generalisation (long VisDial prompts of 4096-8192 tokens run past the 2048-token training length, so shots were capped at 16).
- On classification it trails contrastive models, its own vision encoder among them.
- Few-shot results shift with the order and format of the examples, level off past 32 shots, and make inference costlier as shots grow.
- Each model was trained a single time, so there are no error bars, and model selection biases the DEV benchmarks.
- Code, weights and data are not released; English only; M3W is not deduplicated, nor are VizWiz, HatefulMemes and TextVQA.
- The bias study is preliminary and the 2022 state-of-the-art comparisons have dated.
- The every-4th-block row is a Flamingo-3B ablation; the book chapter (ch03) reports the 80B final design as cross-attention every 7th layer, chosen after hardware considerations. The sources describe different models and the paper extraction gives no interval for the 80B model.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Frozen Visual Prefix Few-Shot Learning]] — prerequisite-for
- [[OBELICS Interleaved Web Document Dataset]] — extends (open reproduction of the M3W-style data)
- [[BLIP-2 Q-Former Bridging]] — alternative-to
- [[Vision-Language Model Training Families]] — related
- [[LENS Frozen LLM with Vision Modules]] — alternative-to
- [[SimVLM PrefixLM Pretraining]] — related
- [[Contrastive and Masked Vision-Language Pretraining]] — related (Kosmos-1 comparison)
