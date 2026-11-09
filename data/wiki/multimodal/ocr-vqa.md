---
title: OCR-VQA
tags: [multimodal, concept]
summary: "OCR-VQA-200K has 207,572 book-cover images and about 1M template-based questions about title, author, genre, year and edition; an OCR-plus-CNN baseline reaches 48.3% accuracy (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-mishra-2019-ocr-vqa.md
---

# OCR-VQA

Mishra et al. (ICDAR 2019) propose a task in which questions on book covers are answered by reading the cover's printed text. They contribute a dataset, OCR-VQA-200K, and a baseline that combines OCR with VQA.

## Dataset and baseline

The dataset has 207,572 images, 1,002,146 QA pairs, 32 genres and 4.83 questions per image, with 320,794 unique answers; questions average 6.46 words and answers 3.31 (all self-reported). Questions are template or paraphrase based and derived from cover metadata. The baseline finds up to five text blocks, applies OCR, tags entities, and passes VGG-16 image features, a BLSTM question encoding, word2vec and the block features into a 51-way softmax classifier. For titles and authors it predicts which block holds the answer rather than generating text.

## Results (self-reported)

- The best variant, block plus CNN plus word2vec features, reaches 48.3% overall accuracy. Block features alone give 42.0%, CNN features alone 14.3%, and block plus CNN 41.5%, slightly below block alone.
- By question type: binary 58.2%, book title 48.5%, year 46.2%, author name 42.9%, edition 42.5%, genre 22.0% (hardest).
- Validation-set title recall with edit-distance correction is 0.83 for TextSpotter against 0.43 for Tesseract and 0.50 for CRNN; without correction TextSpotter gets 0.53.

## Limits

- Book covers only; answers come from metadata, so title and author correctness depends on the metadata matching the cover, and some answers are NULL.
- The edit-distance correction uses a lexicon of every title and author in the set, which inflates the recall table.
- The split description swaps test and validation, and the accuracy tables do not say which split they use. No seeds or variance.
- The authors concede that scene-text VQA and TextVQA appeared after their submission.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[TextVQA and LoRRA]] — related (concurrent work on reading text for VQA)
- [[DocVQA]] — related
