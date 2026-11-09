---
title: "DeepSeek-OCR Optical Context Compression"
tags: [context, pattern]
summary: "DeepSeek-OCR renders text as an image and encodes it into far fewer vision tokens; on a 100-page English test it decoded at 97% precision under 10x compression and about 60% near 20x (self-reported), evaluated as OCR only."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wei-2025-deepseek-ocr.md
---

# DeepSeek-OCR Optical Context Compression

DeepSeek-OCR (arXiv 2510.18234, preprint) tests whether a page of text can be held in fewer vision tokens than text tokens and still be read back. DeepEncoder is about 380M parameters: an 80M SAM-base stage, a 16x convolutional compressor and a 300M CLIP-large stage. The decoder is a 3B mixture-of-experts model with about 570M active parameters. Modes range from Tiny (64 vision tokens) and Small (100) to Gundam (795).

## Results (self-reported)

- Fox benchmark, English only, 100 pages of 600 to 1300 text tokens, Tiny and Small modes: precision 97% below 10x compression and about 60% near 20x. Per-bucket rows run from 96.5% at 10.5x down to 59.1% at 19.7x for 64 tokens.
- OmniDocBench English edit distance: Small (100 tokens) 0.221 against 0.287 for GOT-OCR2.0 (256 tokens); Gundam (795 tokens) 0.127 against 0.133 for MinerU2.0 (6790 tokens). Tiny 0.386, Base 0.137, Large 0.138.
- Throughput: 200k+ pages per day on one A100-40G and 33M pages per day on 20 nodes.

## Limits

- Internal inconsistency: Table 2 and Fig 1(a) do not match for the same compression buckets.
- OCR fidelity only: no retrieval or question-answering evaluation is given. Per-bucket page counts are small (4 to 28).

## See Also
- [[OCR-Memory Optical Context Retrieval]] — related
- [[Context Engineering]] — prerequisite-for
- [[Cache-Augmented Generation]] — related
- [[Donut OCR-Free Document Understanding]] — related
