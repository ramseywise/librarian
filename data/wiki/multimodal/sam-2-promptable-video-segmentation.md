---
title: SAM 2 Promptable Video Segmentation
tags: [multimodal, concept]
summary: "SAM 2 extends Segment Anything to video with a streaming memory over an MAE-pretrained Hiera encoder and a 50.9K-video SA-V dataset; it reports better accuracy with over 3x fewer interactions than SAM plus tracker baselines (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-sam-2-2024.md
---

# SAM 2 Promptable Video Segmentation

The SAM 2 paper (preprint, no venue stated in the PDF) extends promptable image segmentation to video. In Promptable Visual Segmentation (PVS), prompts of points, boxes or masks can land on any frame, and the output is a masklet, meaning the object's mask followed through time. Image segmentation and semi-supervised VOS fall out as special cases.

## Mechanism

- Keeps the prompt encoder and two-way mask decoder of the original model, swaps the image encoder for an MAE-pretrained Hiera, and adds memory attention that conditions each frame on a FIFO memory bank holding spatial memories and object pointers. Images are single-frame videos.
- The model starts from SA-1B pretraining, then trains on video and images together, with simulated interactive prompting. The video side uses SA-V, internal data and optionally open VOS sets. Loss terms are weighted 20:1:1:1 for focal, dice, IoU and occlusion.
- A data engine keeping the model in the loop, run as three phases plus an automatic stage, produces SA-V. It holds 50.9K videos, 642.6K masklets and 35.5M masks (196.0 hours, 4.2M frames). The data is released under CC BY 4.0 and the code under Apache 2.0.

## Results (self-reported)

- For interactive video segmentation, tested zero-shot on 9 datasets with 3 clicks per frame and Hiera-B+ at 1024, accuracy is higher while interactions drop by over 3x relative to SAM+XMem++ and SAM+Cutie baselines.
- In a controlled study of 169 videos and 452 masklets, annotation took 37.8 s per frame with SAM alone, 7.4 s in phase 2, and 4.5 s with SAM 2 in the loop, an 8.4x speedup.
- Image segmentation (SA-23, 1-click mIoU, SA-1B only): Hiera-B+ beats the ViT-H model while 6x faster; 130.1 FPS against 21.7 (A100, batch of 10, bfloat16). Trained on the mix, 61.4 mIoU on 23 datasets; on 14 new video datasets treated as images, 69.6 against 59.1.
- Semi-supervised video segmentation with a first-frame mask: SAM 2 Hiera-L reaches MOSE val J&F 77.9 against 71.7 for Cutie-base+, and SA-V val 77.9 against 61.4 for the best prior work; real-time at 43.8 FPS (B+) and 30.2 (L) on one A100. Over 17 zero-shot datasets: 1-click 64.7, 3-click 75.3, mask prompt 79.3.
- Ablation findings: data from the engine adds 12.1% across 9 zero-shot datasets compared with video-only training. Accuracy follows a power law in SA-V size. Going from 512 to 1024 resolution raises 70.7 to 72.3 while running at 0.22x speed. On SA-V val, adding object pointers moves the score from 64.5 up to 68.3, a gain of 3.8.
- On a fairness check using EgoExo4D with 3 clicks, 1-click J&F is 81.9 for male and 75.1 for female subjects. Training used 256 A100 GPUs over 108 hours, at 3.89 tCO2e.

## Limits

- The model can lose or mix up objects at shot changes, in crowds, after long occlusions and in long videos. Fine, fast-moving details and look-alike neighbours are difficult. Objects are handled one at a time, with no communication among them.
- The data engine still relies on human verification. Not scaled beyond Hiera-L. DAVIS interactive scoring may penalise part-level first clicks; OVIS is not strictly zero-shot. The 1-click gender gap is partly attributed to prompt ambiguity.
- No seeds, variance or significance tests, and no arXiv id or venue in the PDF.

## See Also
- [[Segment Anything SAM and SA-1B]] — prerequisite-for
- [[SAM 3 Promptable Concept Segmentation]] — extends
- [[Masked Autoencoders Pixel Reconstruction]] — prerequisite-for
