---
title: Kosmos-2 Grounded Multimodal LLM
tags: [multimodal, concept]
summary: "Kosmos-2 continues KOSMOS-1 training on GRIT, a web-scale set of grounded image-text pairs, writing bounding boxes as discrete location tokens so one language model can ground phrases and accept boxes as input (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-peng-2023-kosmos-2.md
---

# Kosmos-2 Grounded Multimodal LLM

Peng et al. (2023) ask whether a multimodal LLM can emit bounding boxes for text spans (grounding) and accept boxes as input (referring) by training on web-scale grounded pairs, without losing language and vision-language skills.

## Mechanism

- **GRIT** (Grounded Image-Text pairs) is built from COYO-700M and LAION-2B, with GLIP pseudo-labels kept at confidence above 0.65.
- Each box is quantised onto a 32x32 grid and represented by **location tokens** added to the vocabulary; they follow the text span in a format resembling a Markdown link, with the span first and then the box-corner tokens.
- Training starts from KOSMOS-1 weights with next-token prediction over text, caption pairs, interleaved data and GRIT, then instruction tuning on a mixture drawn from LLaVA-Instruct, Unnatural Instructions and FLANv2, plus grounded instructions built from GRIT. Pretraining covered about 25B tokens over 60k steps and ran roughly a day on 256 V100s (self-reported).

## Results (self-reported)

- Zero-shot Flickr30k Entities test R@1 is 78.7 against 18.9 for GRILL, the other zero-shot model; on validation it falls below fine-tuned FIBER (87.1) and GLIP (86.7) (self-reported).
- On RefCOCOg test, zero-shot accuracy is 61.65 versus 47.5 for GRILL (IoU above 0.5), but zero-shot RefCOCO validation is 52.32, well under fine-tuned FIBER at 90.68 (self-reported).
- Zero-shot referring-expression generation on RefCOCOg reaches CIDEr 60.3 against 59.2 for fine-tuned SLR; few-shot with k=4 gives 62.3 (self-reported).
- Zero-shot Flickr30k captioning CIDEr is 66.7 against 65.2 for KOSMOS-1; VQAv2 test-dev is 45.6 against 46.7. Both are without instruction tuning (self-reported).
- Language tasks stay comparable to KOSMOS-1: BoolQ rises from 56.4 to 62.0 while CB falls from 44.6 to 30.4 (self-reported).

## Limits

- Testing is mostly zero-shot, and the model sits well under fine-tuned specialists on RefCOCO and RefCOCO+, which the authors put down to short referring expressions.
- With no proposals or queries in the model, R@5 and R@10 add little over R@1.
- No instruction-tuned numbers are reported, and there are no seeds, no variance and no ablation of the GRIT filtering thresholds.
- Pseudo-label noise is not quantified; only boxes are supported, quantised at 224x224 input.
- Grounded VQA and captioning are shown only in qualitative figures.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Qwen-VL Fine-Grained Perception VLM]] — related (also adds grounding)
- [[Emu Generative Pretraining in Multimodality]] — related
- [[Flamingo Gated Cross-Attention VLM]] — related
- [[Contrastive and Masked Vision-Language Pretraining]] — related (covers Kosmos-1)
- [[LENS Frozen LLM with Vision Modules]] — related
