---
title: DocVQA
tags: [multimodal, concept]
summary: "DocVQA pairs 12,767 document page images with 50,000 extractive questions and scores answers with ANLS; scene-text VQA models and text-only BERT readers fall well short of humans, especially on layout, figures and handwriting (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-mathew-2021-docvqa.md
---

# DocVQA

Mathew, Karatzas and Jawahar present a question-answering dataset over document images, and measure how far humans sit from current models, both scene-text VQA ones and reading-comprehension ones. The pages are drawn from the UCSF Industry Documents Library. Remote workers selected and annotated them across three stages, and each answer is a span lifted from the page.

## Dataset and metric

The set has 12,767 images from 6,071 documents and 50,000 questions, categorised by reasoning requirement; the test split holds 5,188 questions (self-reported). Answers are scored by ANLS, Average Normalized Levenshtein Similarity, which is designed so that small mismatches caused by OCR errors are not heavily penalised.

## Baselines

The paper tries heuristics (a random OCR token, the majority answer), upper bounds (an answer being a substring or subsequence of the serialised OCR text, or in an answer vocabulary of 4,341 items), LoRRA and M4C run through the MMF framework, and BERT question-answering models fine-tuned on SQuAD-style serialised OCR text. The best baseline is the BERT-large whole-word-masking model fine-tuned first on SQuAD 1.1 and then on DocVQA. The extraction records that without DocVQA fine-tuning this model scores far lower, and that M4C's ANLS improves by about 50% when its dynamic vocabulary grows from 50 to 500 while LoRRA does not benefit (self-reported). The extraction leaves out the exact accuracy and ANLS figures, so none are given here.

## Limits

- Because answers are spans taken from the page, abstractive and numeric-reasoning questions fall outside the benchmark. An OCR substring upper bound of 87% also limits text-only models.
- All baselines depend on one commercial OCR and none are layout-aware pretrained document models.
- Human scores come from a handful of volunteers at the authors' institution. Runs are single, with no seeds or variance reported, and per-question-type results exist only as a bar chart.
- By the authors' account, models are weakest where a question depends on document structure, figures, photographs or handwriting.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[TextVQA and LoRRA]] — prerequisite-for (supplies the LoRRA baseline)
- [[OCR-VQA]] — related (domain-specific text-reading VQA)
- [[ChartQA and VisionTaPas]] — related (domain-specific VQA over charts)
