---
title: "ControlNet Spatial Conditioning"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "ControlNet adds spatial conditions such as edges, depth, pose or segmentation to a pretrained Stable Diffusion model by training a copy of its encoder and joining it to the locked model through zero-initialized convolutions."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhang-2023-adding-conditional-control-text-image.md
  - data/raw/papers/2026-11-08-prompt-engineering-for-generative-ai-ch09-advanced-image-generation-stable-diffu.md
---

# ControlNet Spatial Conditioning

The paper asks how to give a big pretrained text-to-image diffusion network extra spatial inputs without damaging it, even from a small condition dataset. The hypothesis is that locking the pretrained weights, training a copy of the encoder and linking the two through zero-initialized convolutions lets conditions be learned with no harmful noise and no forgetting.

## Mechanism

The pretrained Stable Diffusion U-Net stays frozen. A trainable copy of its 12 encoder blocks and middle block takes the condition (passed through a small 4-convolution encoder) and returns its features to the frozen network via **zero convolutions**: 1x1 convolutions that begin with all weights and biases at zero. Training keeps the usual noise-prediction loss and blanks 50% of prompts. **CFG resolution weighting**, a change to guidance, adds the condition to the conditional prediction only, scaling each connection by 64 over its feature-map size. Released models cover edge maps (Canny), Hough lines, scribbles, body key points, segmentation, surface normals, depth and cartoon line drawings.

## Results

- User studies (12 users, 20 unseen sketches): the zero-convolution version is preferred over PITI, SGD and ControlNet-lite for quality and fidelity (self-reported).
- A depth ControlNet trained on 200k samples (one RTX 3090Ti, 5 days) was not distinguishable by 12 users from SDv2 Depth-to-Image, which was trained on over 12M images (200 images) (self-reported).
- ADE20K segmentation conditioning: ControlNet gives the best FID among segmentation-conditioned methods; Stable Diffusion unconditioned is 6.09. Segmentation re-detected by OneFormer has IoU 0.35 against 0.58 for ground truth (self-reported).
- Compared with Stable Diffusion alone, training needs about 23% more GPU memory and 34% more time per iteration (A100 40GB) (self-reported).
- The authors describe "sudden convergence": control is learned abruptly, usually in under 10K steps (example at step 6133) (self-reported).
- Swapping zero convolutions for Gaussian-initialized ones lowers quality to roughly ControlNet-lite (6 samples per setting, no metric). Training does not collapse on 1k images and improves with more data (1k, 50k and 3m images for one prompt) (self-reported).

## In Stable Diffusion tooling (Phoenix and Taylor)

Phoenix and Taylor (*Prompt Engineering for Generative AI*, chapter 9) advise matching the ControlNet preprocessor to its model and Stable Diffusion version, starting with Canny, and note that the ControlNet models they use are for SD 1.5 only. The advice is "in our experience", not tested.

## Limits

- The user studies are small and their plus-minus values are undefined; the ablation is qualitative and has no metric.
- PITI is built on a different backbone (GLIDE), so that comparison is not like for like.
- Quantitative comparison covers segmentation and sketch only; depth is a user discrimination test.

## See Also

- [[Diffusion and GAN Image Generation]] — related
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for
- [[Make-A-Scene Scene-Based Text-to-Image Generation]] — related (segmentation tokens as a control mechanism)
- [[InstructPix2Pix Instruction-Based Image Editing]] — related (both condition Stable Diffusion on an image)
- [[GLIGEN Grounded Text-to-Image]] — related
- [[Image Prompting Practices for Diffusion Models]] — related
