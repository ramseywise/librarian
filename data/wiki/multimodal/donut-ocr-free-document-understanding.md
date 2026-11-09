---
title: Donut OCR-Free Document Understanding
tags: [multimodal, method]
summary: "Donut is an encoder-decoder Transformer that reads a document image and generates structured JSON directly, with no OCR engine, after pretraining to read text."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kim-2022-ocr-free-document-understanding-transformer.md
---

# Donut OCR-Free Document Understanding

The question is whether one end-to-end Transformer can turn a document image straight into structured output with no OCR engine, while keeping the accuracy and speed of OCR-based document understanding models. The hypothesis is that an encoder-decoder pre-trained to read text avoids the cost, inflexibility and error propagation of OCR.

## Mechanism

Donut combines a Swin-B visual encoder with a decoder made of the first four layers of multilingual BART. Pretraining is next-token cross-entropy on the task of reading all text in a page image, with IIT-CDIP pages carrying pseudo labels from CLOVA-OCR, plus synthetic pages from SynthDoG. For each downstream task (classification, information extraction, DocVQA) a task prompt makes the decoder emit a JSON token sequence. Tree outputs are scored with a TED-based accuracy: one minus the edit distance to the ground truth, divided by the distance from an empty tree, floored at zero.

## Results

- RVL-CDIP test accuracy is 95.30 at 752 ms against 95.25 at 1489 ms plus OCR for LayoutLMv2 (self-reported). Setup: 40K images, Donut 143M, 2560x1920 input, P40 GPU; LayoutLMv2 number from its own paper.
- On CORD, Donut gets 84.1 F1 with 90.9 TED accuracy at 1.2 s per image, where LayoutLMv2 gets 78.9 F1 and 82.4 accuracy at 1.7 s (self-reported). Setup: CORD test, baselines using CLOVA OCR.
- On the DocVQA test set Donut's ANLS is 67.5, under LayoutLMv2 (78.1) and LayoutLMv2-Large-QG (86.7) (self-reported). Setup: 176M model, fine-tuned on the train split only.
- Using just 10 percent of the CORD training set (80 samples), Donut still beats LayoutLMv2 (self-reported).
- As a pretraining task, reading text outperforms image captioning or classification, and real IIT-CDIP images matter for DocVQA while synthetic images suffice for information extraction; values are only in a figure.
- How accurate and how fast the OCR-based baselines are depends heavily on the OCR engine chosen.

## Limits

- Higher input resolution makes accuracy sturdier but costs more, and tiny text in large images is missed.
- On DocVQA it trails LayoutLMv2 and the QG-trained large model.
- Numbers come from single runs without seeds; the business card and receipt data are private.
- The speed comparison sets Donut on a P40 against API OCR timings, and baseline parameter counts leave out the OCR.
- The authors name a better pretraining objective as future work.

## See Also
- [[Vision-Language Model Training Families]] — related (a document-reading model trained end to end)
- [[DeepSeek-OCR Optical Context Compression]] — related (reading text from images)
