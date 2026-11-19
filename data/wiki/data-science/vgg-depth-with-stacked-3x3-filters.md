---
title: "VGG Depth with Stacked 3x3 Filters"
tags: [data-science, pattern]
summary: "VGG fixes every other design choice, uses only 3x3 convolutions and varies depth from 11 to 19 weight layers; the paper reports error falling until 16 to 19 layers and a 6.8% top-5 test error for a two-model ensemble on ILSVRC-2014 (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-simonyan-2014-very-deep-convolutional-networks-large.md
---

# VGG Depth with Stacked 3x3 Filters

Simonyan and Zisserman (ICLR 2015) ask how depth alone affects accuracy when everything else is held fixed and every filter is 3x3. They train six configurations (A to E, plus A-LRN) from 11 to 19 weight layers on ILSVRC-2012 with SGD and scale jittering. Config C adds 1x1 convolutions, and A-LRN adds local response normalisation.

## Mechanism

Three stacked 3x3 layers use 27C^2 weights, against 49C^2 for a single 7x7 layer (81% more), with C channels in and out. Training scale S is the smallest side of the rescaled image from which the input is cropped, and test scale Q is the size the test image is rescaled to. Scale jittering samples S from a range for each training image.

## Results (self-reported)

- Ensembling networks D and E (trained with S in [256;512], tested at Q = 256, 384 and 512 with multi-crop plus dense evaluation) gives 6.8% top-5 test error in ILSVRC-2014 classification. The submitted 7-net ensemble (dense evaluation) got 7.3%, second place.
- Single-model validation error falls from 11 layers (A) to 16 to 19 (D, E), then saturates (config E, S in [256;512], Q=384).
- Scale jittering in training beats a fixed S at a single test scale (config D).
- Adding local response normalisation brings no gain (A-LRN against A, S=Q=256). Config C beats B, so 1x1 layers help, while D beats C, so 3x3 layers help more.
- A shallower net made from B by using five 5x5 layers has top-1 error 7% above B's (centre crop).
- Dense and multi-crop evaluation together improve over either alone.
- One VGG net is 0.9% better in top-5 test error than one GoogLeNet (multi-crop and dense).
- Localisation: 25.3% top-5 test error, first place, from config D with per-class regression, all layers fine-tuned, fusing S=256 and S=384 models.
- Frozen features: stacking the 4096-D penultimate features of Net-D and Net-E under a linear SVM gives 89.7 mAP on VOC-2007, without fine-tuning.
- Parameters run from 133M (A) to 144M (E). Training one net took 2 to 3 weeks on four Titan Black GPUs, and synchronous data parallelism gave a 3.75x speedup on 4 GPUs.

## Limits

- Error levels off by 19 layers on ImageNet. The authors suggest more depth could pay off on bigger datasets but never test that.
- Single runs, with no seeds or variance for ILSVRC results.
- Deeper nets were initialised from shallow net A; the authors later found that Glorot initialisation removes this need.
- Why multi-crop plus dense beats either one is explained by boundary conditions only as a hypothesis.
- Localisation used neither scale jittering nor OverFeat's resolution enhancement.
- About 140M parameters, mostly in the fully connected layers; the extraction notes that residual networks superseded the design, which this paper does not cover.
- Some VOC rivals were pre-trained on larger sets.

## See Also
- [[Residual Connections and the Degradation Problem]] — related
- [[ILSVRC ImageNet Challenge]] — related
- [[Compound Scaling of Depth, Width and Resolution (EfficientNet)]] — related
- [[R-CNN Region Proposals with CNN Features]] — related (its 16-layer O-Net is this network)
