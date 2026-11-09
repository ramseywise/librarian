---
title: ChartQA and VisionTaPas
tags: [multimodal, concept]
summary: "ChartQA offers 9,608 human-written and 23,111 machine-generated questions on real charts; a pipeline that extracts a data table and feeds it to VisionTaPas or T5-style models reaches at best 51.84% overall, and human-written questions are far harder (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-masry-2022-chartqa.md
---

# ChartQA and VisionTaPas

Masry et al. (Findings of ACL 2022) build a benchmark of questions about real charts that need visual and logical reasoning, where a model may first have to recover the underlying data table from the picture.

## Benchmark and pipeline

ChartQA-H has 4,804 charts and 9,608 human-written questions; ChartQA-M has 17,141 charts and 23,111 T5-generated questions built from Statista summaries. Charts come from Statista, Pew, OWID and OECD. The chart-to-table step builds on ChartOCR with CRAFT text recognition and emits a structured table. That table accompanies the question, and optionally image features, into T5, VL-T5, TaPas or VisionTaPas. VisionTaPas pairs a ViT image encoder with TaPas through a cross-modality encoder of 4 layers, and adds difference and ratio operations. Answers are scored by relaxed accuracy, allowing a 5% error on numbers (benchmark and pipeline figures self-reported).

## Results (self-reported; ChartQA test)

- Among the four benchmark models run with extracted tables, VisionTaPas does best. VL-T5 pretrained on PlotQA and then fine-tuned goes from 41.56% to 51.84% overall, the paper's top figure.
- VisionTaPas scores 29.60% on the human-written half and 61.44% on the machine-generated half. With the gold data table it reaches 61.84% against 45.52% with the extracted table.
- Chart-to-table extraction is 83.85% accurate on ChartQA against 95.05% on FigureQA and 89.98% on DVQA.
- A fixed-vocabulary classifier, PReFIL, scores 4.8% on ChartQA. On DVQA test VisionTaPas reaches 94.54% with OCR.
- On 200 human-written questions, those combining compositional and visual reasoning prove hardest at 16.21%, against 60.00% for plain data retrieval. Split by chart type, VisionTaPas manages 49.80% on bar charts, 38.20% on line charts and 24.41% on pie charts.
- Exact agreement between annotators was 61.04% (78.55% once typos are forgiven). Of 1,250 machine-generated pairs checked, 86.64% were correct and answerable.

## Limits

- No nested operations; only bar, line and pie charts; log-scale charts are unsupported, and Pew charts have no gold tables.
- The modular pipeline is error-prone (a 16-point drop against gold tables), and data and visual features are combined separately.
- Single runs without variance. The extraction notes the pipeline predates end-to-end multimodal LLMs. The text says 79.4% of bar charts are simple and 29.6% complex, which sums to over 100%.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[DocVQA]] — related (document-image counterpart)
- [[OCR-VQA]] — related
