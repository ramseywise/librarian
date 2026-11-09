---
title: Flickr30k Entities
tags: [multimodal, reference]
summary: "Flickr30k Entities adds 244k coreference chains and 276k boxes to the Flickr30k captions and defines a phrase-localisation benchmark; a CCA plus detector, size and colour baseline reaches 50.89 Recall@1, yet barely improves image-sentence retrieval (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-plummer-2015-flickr30k-entities.md
---

# Flickr30k Entities

Plummer et al. (arXiv v4, 2016; preliminary ICCV 2015 version) test whether box-level ground truth tying caption phrases to image regions can be gathered at scale, and how well methods can localise the entities a caption mentions. Crowd workers, through small atomic tasks, join noun-phrase mentions from the five captions of every Flickr30k image into coreference chains, then draw boxes for each chain. The result is 244,035 chains and 275,775 boxes across 31,783 images (self-reported). Chunking errors and coreference errors each stay below 1%, which the authors translate into some error in about 8% of images.

## Benchmark and baseline

Phrase localisation asks for a box given an entity mention. Scoring is Recall@K, counting a hit at IoU of 0.5 or more, over 200 EdgeBox proposals and with ground-truth noun-phrase chunks. The baseline maps regions and phrases into a shared space with CCA (HGLMM Fisher vectors; VGG19 or Fast R-CNN features), and then adds a colour classifier, a size prior and PASCAL detector scores.

## Results (self-reported)

- The full model reaches 50.89 Recall@1. Switching region features from VGG19 to Fast R-CNN raises CCA alone from 30.83 to 41.77, and averaging in detector scores gives 43.84.
- The size prior contributes roughly 5.4 points. Simply choosing the largest proposal, whatever the phrase, already reaches 24%.
- Body parts prove the hardest category, at 17.21 Recall@1 for the full model, and just 50.48% of them have any proposal reaching IoU 0.5 within the 200.
- Bringing region-phrase scores into whole-image CCA nudges image annotation Recall@1 from 36.5 to 37.5. For image search Recall@1, the result is 25.8, compared with 25.7 for a basic VGG variant.

## Limits

- Only mentioned entities are annotated, so a valid region that no caption mentions is scored as wrong; for that reason the authors dropped average precision as unreliable.
- Scoring ignores the surrounding sentence, phrases that map to several boxes get merged into one, and the ceiling on proposal recall bounds all results.
- Images focus on people and animals. Results are single-run; competing results use 100 proposals against 200 here. Automatic chunking lowers recall by about 3%.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Visual Genome]] — related (another dense region-grounding dataset)
- [[Microsoft COCO]] — related
- [[Deep Visual-Semantic Alignments]] — related (also aligns sentence fragments with image regions)
