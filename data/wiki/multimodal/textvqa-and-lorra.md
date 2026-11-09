---
title: TextVQA and LoRRA
tags: [multimodal, concept]
summary: "TextVQA is a crowd-sourced VQA set on Open Images photos whose questions need reading text in the image; the LoRRA model adds frozen OCR and a copy mechanism and reaches 27.63% test accuracy (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-singh-2019-towards-vqa-models-that-can.md
---

# TextVQA and LoRRA

Singh et al. (arXiv, v2 May 2019) study whether VQA models can handle questions that demand reading and reasoning over text within an image. Their contributions are a dataset, TextVQA, and a model, LoRRA (Look, Read, Reason and Answer). LoRRA reads through a separate OCR component, rather than expecting one monolithic VQA network to learn reading from answer supervision.

## LoRRA

LoRRA extends the Pythia v0.3 VQA model with Rosetta, a frozen OCR module. Attention runs over the OCR tokens, and M dynamic slots are added to the answer space so one OCR token can be copied out as the answer. The loss is binary cross-entropy on the logits, and an MLP over the concatenated VQA and OCR outputs gives the final score.

## Results (self-reported)

- Best LoRRA reaches 26.56% on TextVQA validation (mean of 5 seeds, small answer vocabulary) and 27.63% on test, against 14.0 for Pythia with image and question only.
- Without OCR, the VQA models Pythia v0.3 and BAN reach 13.04% and 12.3% on validation. Giving Pythia the OCR tokens but no copying yields 18.35%, while predicting only by copying OCR tokens yields 20.06%.
- The OCR upper bound on validation is 37.12%, and the upper bound combining the large answer vocabulary with OCR is 67.56%. Human accuracy is 85.01 on validation.
- 44.9% of LoRRA's validation predictions are copied from OCR tokens; when copying, the answer is fully right 27% of the time and partly right 11%.
- With LoRRA added, Pythia's VQA 2.0 test-dev result moves from 68.71 up to 69.21, a rise of 0.5. On VizWiz test, Pythia v0.3 gets 54.72% and BAN 51.40.
- Baselines given only the question or only the image get 8.09% and 6.29%, which the authors take as a sign of little bias.

## Limits

- The copy mechanism outputs a single OCR token, but 8.9% of questions need several tokens.
- Results hinge on OCR quality, because Rosetta breaks down on text that is rotated, occluded or unstructured. The model also shows biases; for example, city questions tend to get "new york" as the answer.
- Test accuracy is given for only some models; hardware is not stated; there is no variance for the +0.5 VQA 2.0 gain. Later text-VQA models and OCR-free models supersede LoRRA.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[VQA v2 Balanced Dataset]] — prerequisite-for (the VQA 2.0 data it also evaluates on)
- [[VizWiz Grand Challenge]] — prerequisite-for (a source of motivation and an evaluation set)
- [[DocVQA]] — extends (uses LoRRA as a baseline on document images)
- [[OCR-VQA]] — related (concurrent reading-based VQA dataset)
- [[Faster R-CNN]] — related
