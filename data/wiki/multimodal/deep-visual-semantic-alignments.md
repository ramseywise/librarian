---
title: Deep Visual-Semantic Alignments
tags: [multimodal, concept]
summary: "Karpathy and Fei-Fei embed image regions and sentence fragments in one space, infer word-to-region alignments, and use them to train a multimodal RNN captioner that also describes regions (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-karpathy-2015-deep-visual-semantic-alignments-generating.md
---

# Deep Visual-Semantic Alignments

Karpathy and Fei-Fei use sentences written for whole images as weak labels whose image locations are unknown, and proceed in two stages.

## Mechanism

- **Alignment.** 20 region features per image from an R-CNN and a bidirectional RNN over words are embedded in one space. The image-sentence score sums, over words, the best-matching region dot product. A max-margin ranking loss trains it, and a chain-structured MRF decodes word-to-region alignments. It builds on an earlier fragment-embedding objective, with the BRNN replacing dependency trees.
- **Generation.** A plain multimodal RNN sees the image only at its first step. It is trained either on whole images (VGGNet features) or on inferred region and snippet pairs. According to the extraction, the Karpathy split label does not occur anywhere in the paper.

## Results (self-reported)

- The BRNN beats a DeFrag reimplementation (19.2) and dependency-tree edges (20.0) on Flickr30K annotation recall at 1 (average of the top 5 validation models, AlexNet-class features). On MSCOCO recall falls as the test set grows from 1,000 to 5,000 images. Most exact retrieval and caption figures are stripped in the extraction.
- Caption generation (full image, VGGNet, 5 references): CIDEr against 38.3 for a nearest-neighbour baseline; at beam size 1, 25% of captions appear verbatim in training and CIDEr is 0.61 instead of 0.66 at beam 7.
- Region level: 9,000 snippets collected for 200 COCO test images, with human agreement at BLEU-4 22.0.

## Limits

- The two models are trained separately rather than end to end, and the image enters only as an additive bias at a single fixed resolution. The appendix lists further gaps: nothing counts explicitly, region captions lack context, and rare concepts are handled poorly.
- The authors report finding, after submission, that LSTMs did better than their RNN throughout. Retrieval uses AlexNet-class features, whereas captioning uses VGGNet.
- The extraction notes that Table 2's caption gives 1,000 test images although the COCO test split has 5,000. Several settings are unstated (learning rate, dropout, weight decay, epochs, MRF beta), and the PDF names no venue.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Flickr30k Entities]] — related (a region-phrase grounding dataset)
- [[Microsoft COCO]] — related
- [[Visual Genome]] — related
