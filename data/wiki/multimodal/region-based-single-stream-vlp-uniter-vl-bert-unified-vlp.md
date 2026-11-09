---
title: Region-Based Single-Stream VLP (UNITER, VL-BERT, Unified VLP)
tags: [multimodal, comparison]
summary: "Three 2019-2020 detector-region pretraining models compared: UNITER's conditional masking and optimal-transport alignment, VL-BERT's finding that sentence-image matching hurt, and Unified VLP's single shared encoder-decoder switched by attention mask (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-chen-2020-uniter.md
  - data/raw/papers/2026-11-07-su-2019-vl-bert.md
  - data/raw/papers/2026-11-08-zhou-2020-unified-vision-language-pre-training.md
---

# Region-Based Single-Stream VLP (UNITER, VL-BERT, Unified VLP)

All three models feed Faster R-CNN or Fast R-CNN region features plus text tokens into one BERT-style Transformer and pretrain it on image-text pairs with masked prediction. They differ in which pretraining tasks they keep.

## UNITER (Chen et al., 2020)

- Single-stream Transformer over region features (plus a 7-dimensional box vector) and WordPiece tokens, pretrained on 5.6M in-domain and 4M out-of-domain pairs with masked language modelling, masked region modelling (three variants), image-text matching and an optimal-transport **word-region alignment** task. One task is sampled per mini-batch.
- **Conditional masking** masks one modality and leaves the other intact. Removing it lowers the Meta-Sum, the sum of scores across benchmarks (a single-run UNITER-base ablation) (self-reported).
- Image-text matching alone and masked language modelling alone are the strongest single tasks; masked region feature regression alone is weak. In-domain data beats out-of-domain despite fewer images, and both together are best (self-reported).
- With Conceptual Captions as its only pretraining data, UNITER-base scores above ViLBERT and, for VQA test-dev, above VL-BERT-base, with 86M parameters where LXMERT has 183M and ViLBERT 221M (self-reported).

## VL-BERT (Su et al., ICLR 2020)

- BERT extended with RoI tokens (appearance feature plus box geometry), pretrained on Conceptual Captions plus BooksCorpus and Wikipedia text, with masked RoI classification using linguistic clues. It has no sentence-image relationship task, and the Fast R-CNN detector is tuned jointly with the rest.
- Adding sentence-image relationship prediction lowered VCR, VQA and RefCOCO+ accuracy in the BASE ablation at half fine-tuning epochs. The authors guess unmatched negative pairs cause it; this is untested (self-reported). This is the opposite of UNITER's keeping image-text matching, and the extraction records it as contradicting ViLBERT's two-stream claim.
- VL-BERT-LARGE is the first single model on the VCR leaderboard; it trails LXMERT on VQA test-std, which the authors attribute to LXMERT's VQA-style pretraining data (self-reported).

## Unified VLP (Zhou et al., AAAI 2020)

- One BERT-base Transformer, starting from UniLM weights, receives the tokens together with 100 region embeddings; each batch switches between a bidirectional attention mask and a left-to-right seq2seq one. Fine-tuning uses seq2seq for captioning and bidirectional for VQA.
- Flickr30k test CIDEr is 67.4 against 56.8 for the no-VLP baseline; COCO CIDEr rises from 114.3 to 116.9 with cross-entropy only (self-reported).
- Bidirectional-only pretraining gave the best VQA and seq2seq-only the best Flickr30k captioning among variants (self-reported).

## Limits

- UNITER: pretraining hyperparameters are not stated; ablations are single runs with row gaps often under 1 point; the detector saw RefCOCO val and test images, so referring-expression numbers are contaminated; the text and Table 3 disagree on whether UNITER-base beats others on VQA.
- VL-BERT: layer counts and sizes are given only by reference to BERT; ablation gaps are at most 1.2 points; the text says the text-only corpus helps on all three tasks, but in the table VQA and RefCOCO+ do not change.
- Unified VLP: joint training is slightly worse than task-specific pretraining; its VQA state-of-the-art claim ignores LXMERT and ViLBERT rows in its own table.
- All three depend on a pretrained detector and report no seeds or variance.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — alternative-to
- [[SimVLM PrefixLM Pretraining]] — related
- [[ViLT Patch Projection Vision-Language Transformer]] — related
