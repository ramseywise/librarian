---
title: ViLBERT Co-Attention Two-Stream Pretraining
tags: [multimodal, concept]
summary: "ViLBERT runs separate BERT-style text and image-region streams that exchange keys and values through co-attention layers, pretrained on Conceptual Captions and transferred to four vision-language tasks."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lu-2019-vilbert.md
---

# ViLBERT Co-Attention Two-Stream Pretraining

ViLBERT treats visual grounding as a task-agnostic capability learned on paired image-text data. It has two parallel streams in the style of BERT, one for text (initialised from BERT-BASE) and one for vision (over Faster R-CNN region features). They interact through co-attentional transformer layers (Co-TRM), in which each stream's keys and values are passed to the other stream's attention block. Pretraining uses about 3.1M Conceptual Captions pairs with two proxy tasks: masked multi-modal modelling (for regions, a KL loss to the detector's class distribution) and multi-modal alignment prediction. Each task then fine-tunes the whole model with only a classifier added.

## Reported results (self-reported)

The extraction gives directions and a few numbers.

- Full ViLBERT sets state of the art on VQA 2.0 test-dev (over DFAF), VCR Q to AR on val (over R2C), RefCOCO+ (over MAttNet) and image retrieval R1 on a 1,000-image test (over SCAN).
- Pretraining improves results across tasks by 2 to 13 percent against the same architecture without pretraining.
- A pretrained single-stream variant scores below pretrained ViLBERT on VQA.
- Zero-shot retrieval, with no Flickr30k fine-tuning, still beats the prior fine-tuned state of the art on R1 (self-reported). Zero-shot R1 grows with pretraining data (31.86 at 100% of Conceptual Captions); VQA grows monotonically (70.30 at 50%, 70.55 at 100%) (self-reported).
- Depth: an 8-layer visual stream helps retrieval, while VCR and RefCOCO+ prefer shallower models (the extraction gives 54.04 for a 2-layer versus 6-layer comparison without saying which depth it belongs to) (self-reported).

## Limits

- No seeds, variance or significance tests.
- Text generation is unsolved: the authors say how to decode from the bidirectional model is unclear.
- The single-stream variant was not evaluated on retrieval because it cannot cache representations.
- Uses BERT-BASE for cost reasons; detector features are fixed and detector cost, thresholds and several fine-tuning details are unspecified.
- Captions from the pretrained model are editorialised by the alt-text data.

## See Also
- [[Contrastive and Masked Vision-Language Pretraining]] — related (the family comparison)
- [[ViLT Patch Projection Vision-Language Transformer]] — extends (removes the detector and the second stream)
- [[ALBEF Align Before Fuse]] — extends
- [[Region-Based Single-Stream VLP (UNITER, VL-BERT, Unified VLP)]] — alternative-to
- [[Multimodal Architectures Survey (Image-Text)]] — related
