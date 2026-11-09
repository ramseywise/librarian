---
title: SPAE Semantic Pyramid AutoEncoder
tags: [multimodal, concept]
summary: "SPAE turns an image into a pyramid of words from a frozen LLM's own vocabulary, coarse semantics first, so a frozen LLM can classify, caption, answer questions about and generate images by in-context learning; understanding peaks at 21 tokens (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yu-2023-spae.md
---

# SPAE Semantic Pyramid AutoEncoder

Yu et al. (arXiv 2306.17842, NeurIPS 2023) convert between pixels and lexical tokens drawn from a frozen LLM's vocabulary, with no backpropagation through the LLM. Setup throughout: SPAE trained standalone, PaLM 2-L and GPT-3.5 as the frozen LLMs, 128x128 images, 6 layers.

## Mechanism

- The pyramid stacks six layers; layer sizes are 2^k by 2^k tokens with k running 0, 1, 2, 3, 4 and then 4 again, so the running token totals are 1, 5, 21, 85, 341 and 597. Upper layers hold semantics and lower layers hold appearance.
- CLIP ViT-L/14 scores semantics, with a semantic loss on the first five layers.
- **Streaming Average Quantization** replaces residual quantization, which the authors found fits a frozen codebook worse; the embedding at each layer is the average of the token embeddings so far.
- Generation: direct generation worked on 32x32 MNIST (each digit 37 tokens), where the LLM completes a query such as "an image of 1+7" by producing an 8. Larger images use in-context denoising with progressive decoding; single-step decoding fails and VQGAN and LQAE tokenizers also fail the procedure.

## Results (self-reported)

- Few-shot mini-ImageNet, 2-way: SPAE-PaLM averages 77.74 with 2 layers (5 tokens) and 79.03 with 3 layers (21 tokens), versus 53.97 for LQAE and 51.3 for Frozen; in the 5-way case it gets 61.86 versus 29.04. According to the authors, the GPT rows and PaLM rows should not be read as a comparison of the two LLMs.
- Holding GPT-3.5 fixed, SPAE-GPT outscores LQAE (69.51 vs 53.97, 2-way) while using 5 tokens where LQAE uses 256.
- Extra tokens do not improve understanding. The 2-way average by token count: 1 token gives 70.31, 5 gives 77.74, 21 gives 79.03, 85 gives 76.76, 341 gives 71.51, and 597 gives 59.19.
- Captioning needs more tokens; reasonable captions appear from 4 layers (85 words), complex scenes may need all 597 (qualitative, on COCO).
- On Real-Fast-VQA with 1, 3 and 5 inner shots, SPAE scores 14.3, 15.9 and 15.1 where Frozen scores 7.8, 10.1 and 10.5.
- ImageNet 128x128 reconstruction FID is 4.41 at 597 tokens against 5.48 for a 256-token VQGAN, and 9.49 at 341 tokens.
- Ablation (5-way 1-shot): plain VQ 19.6%; frozen codebook alone 19.5%; adding semantic loss 46.2%. Removing the perceptual loss raises layer-3 accuracy (69.5%) but sends FID to 40.47.
- Leaving the 20 mini-ImageNet classes out of tokenizer training drops 2-way accuracy for the two best settings to 72.93 and 74.98.

## Limits

- The authors say the frozen language codebook needs more tokens for equal reconstruction, in-context learning is capped by sequence length (an 8K context holds under a dozen 128x128 images), and quality is far from text-to-image models.
- Generation results are qualitative; no FID or human evaluation. The extraction notes that the few-shot baselines (Frozen, LQAE) are 2021-2023 systems, so the state-of-the-art claim holds only in the frozen-LLM in-context setting.
- Not tested: prompt or adapter tuning, which the authors expect to help. Possible train/test overlap is only partly addressed. For image-to-video only four samples fit in context.
- Generated tokens occasionally include slang or words with inappropriate connotations.
- The extraction notes garbled equations and table headers, and that the text cites Tab. 3 for ablations that are in Tab. 4.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[Emu Generative Pretraining in Multimodality]] — alternative-to
- [[Vision-Language Model Training Families]] — prerequisite-for
