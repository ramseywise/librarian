---
title: OBELICS Interleaved Web Document Dataset
tags: [multimodal, concept]
summary: "OBELICS is an open dataset of 141M filtered Common Crawl documents with 353M images and 115B tokens, used to train the Flamingo-style IDEFICS models and to show interleaved documents beat image-text pairs for few-shot use (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-laurencon-2023-obelics.md
---

# OBELICS Interleaved Web Document Dataset

Laurencon et al. (2023) ask whether Common Crawl can yield an open, web-scale collection of filtered documents that interleave images and text, and whether it can train large multimodal models that compete well. A multimodal document is a succession of text paragraphs interleaved with images, such as a web page.

## Pipeline

- 25 Common Crawl dumps go through English, deduplication and quality text filters, are simplified to HTML, then interleaved text and images are extracted with node, paragraph and document filters, followed by deduplication and responsible-use filtering.
- The funnel runs 41.2B documents to 1.1B, 365M (1.4B images) and finally 141M documents with 353M images, of which 298M (84.3%) are unique; the text totals 115B tokens against 43B for mmc4, whose images are 60.6% unique (self-reported).
- Just 55% of the 3.6B image links could be downloaded. Deduplicating paragraphs inside each domain strips about 15% of the text, and the opt-out filter applied via the Spawning API took out 0.047% of images. The median document has 1 image and 677 tokens, capped at 30 images.
- Tighter filters leave fewer documents without raising quality, so the authors advise starting from a random subset.

## Results (self-reported)

- With 9B Flamingo-style models, web documents reach the same aggregated 4-shot performance as image-text pairs with an order of magnitude fewer images (read from a figure). During training the LAION-only model gets worse on VQA and the OBELICS model does not, though the pair-trained model holds a small lead on captioning, classification and OCR. A 50/50 mixture beats either alone (self-reported).
- Aggregated, IDEFICS-9B outperforms OpenFlamingo-9B (trained on mmc4) but stays behind Flamingo-9B. IDEFICS-80B gets 32-shot COCO CIDEr 116.6 against 113.8 for Flamingo-80B and 0-shot VQAv2 60.0 against 56.3, but trails on HatefulMemes at 32 shots (self-reported).
- Manual inspection of 250 documents: 90% have images clearly related to the text, 30% contain written words in images, 46% contain faces, 7% have content the filters missed, about 3% have watermarks and none showed NSFW images (self-reported).

## Limits

- Single runs without error bars. At 80B and 32 shots, IDEFICS wins or ties on just 4 of 8 tasks.
- Filters are heuristic; PII was not intentionally removed; the NSFW classifier wrongly flags portraits of women and of people of color; the opt-out process cannot cover everything, and consent was not explicitly sought.
- The bias evaluation accompanies the model release and does not appear in the paper.
- Data and size are confounded in the model comparison, since the IDEFICS mixture adds Wikipedia documents, LAION and PMD as well.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[LAION-5B Open CLIP-Filtered Image-Text Dataset]] — alternative-to
- [[Flamingo Gated Cross-Attention VLM]] — prerequisite-for
