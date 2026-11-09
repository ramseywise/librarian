---
title: Chameleon Mixed-Modal Early Fusion
tags: [multimodal, concept]
summary: "Chameleon trains one Llama-2-style decoder from scratch on text, code and VQ-quantised image tokens in a shared vocabulary, with QK-norm and norm reordering needed for stable training (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-team-2024-chameleon.md
---

# Chameleon Mixed-Modal Early Fusion

The Chameleon Team (FAIR at Meta, 2024) asks whether one transformer over tokens, that learns from scratch on text and image tokens mixed together (early fusion), can stay stable at scale while both reading and producing documents that mix text and images. **Early fusion** means all modalities are projected into a shared representation from the start, in contrast to bridging a frozen encoder to a frozen LLM.

## Mechanism

- A VQ tokenizer turns each image into 1024 tokens from an 8192-entry codebook; images share one 65,536-token BPE vocabulary with text. The 7B and 34B Chameleon models are decoders in the Llama-2 style, trained from scratch and then lightly SFT-tuned.
- Stability needed **QK-norm** (layer norm on queries and keys inside attention), z-loss, dropout for 7B, and a Swin-style reordering of normalisation for 34B (norm applied to the output of attention and FFN instead of the input). Without QK-norm the 7B model diverges (self-reported). The instabilities appeared late and above 8B parameters and 1T tokens, and the recipe was found empirically.
- The 34B model used 3072 concurrent A100 80GB GPUs.

## Results (self-reported)

- Pairwise human evaluation on 1,048 prompts with 3 annotators compares against Gemini Pro and GPT-4V, each with DALL-E 3 images added; the extraction records Chameleon-34B as preferred over Gemini and with a win rate against GPT-4V (self-reported).
- On COCO Karpathy test, the pretrained Chameleon-34B with 2 shots gets a higher CIDEr than Flamingo-80B and IDEFICS-80B at 32 shots, and the SFT model gets 140.8 zero-shot (self-reported).
- On text, the 34B model beats Llama-2 70B on GSM8K (8-shot, maj@1) but falls short of Mixtral 8x7B and Gemini-Pro on MMLU (self-reported).
- Safety evaluation covered 20,000 crowdsourced prompts and 445 red-team interactions; the red team rated 1.6% of responses unsafe and 4.5% unsure (self-reported).

## Limits

- The image tokenizer reconstructs text-heavy images poorly, which caps OCR-heavy tasks.
- The human-evaluation prompts are crowdsourced and leave out OCR and infographic tasks; the baselines are text-only API models paired with DALL-E 3, not native mixed-modal models. Annotators agree only weakly (Krippendorff's alpha 0.338 for task fulfilment).
- Safety tuning is SFT only. No image-generation metric such as FID is reported, only human evaluation and samples.
- Whether code, weights and data are available is not stated; no seeds or error bars; layer count, hidden size and heads are not stated.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Emu Generative Pretraining in Multimodality]] — alternative-to
- [[VQGAN Taming Transformers]] — prerequisite-for
- [[Flamingo Gated Cross-Attention VLM]] — alternative-to
