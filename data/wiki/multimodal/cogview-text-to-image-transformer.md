---
title: "CogView Text-to-Image Transformer"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "CogView is a 4B, 48-layer autoregressive Transformer over text tokens and VQ-VAE image tokens, with PB-relax and Sandwich-LN to stabilise fp16 training and a caption-loss reranker in place of CLIP."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ding-2021-cogview.md
---

# CogView Text-to-Image Transformer

Ding and colleagues ask if one big autoregressive Transformer over a joint sequence of text tokens and VQ-VAE image tokens can generate images in the general domain from text, and how its fp16 training can be kept stable. Numbers are self-reported.

## Mechanism

- **Tokenizer:** a discrete autoencoder maps 256x256 images to 32x32 tokens with an 8192 codebook. Four tokenizer-training methods converged to similar L2 loss, so the authors conclude codebook learning matters little if initialised properly.
- **Model:** a GPT with 48 layers, trained left to right on [text; image] token sequences, drawn from 30M text-image pairs that lean Chinese; fine-tuned variants do super-resolution, captioning, style learning and fashion design.
- **PB-relax** (precision bottleneck relaxation) divides by the maximum before LayerNorm, and computes attention with the maximum subtracted inside the softmax and a factor alpha = 32 restored afterwards, to prevent overflow. **Sandwich-LN** places an extra LayerNorm at the close of every residual branch. An ordinary pre-LN 4B Transformer gave NaN loss within 1,000 iterations in fp16, and the pair fixed it (claim; toy setup and a 500M run, no full-scale ablation).
- **Caption Loss (CapLoss):** the cross-entropy of the text tokens conditioned on the image; it reranks candidates and also serves as a metric.
- Three-region sparse attention (with pivot tokens) was 2.5x faster and saved 40% GPU memory on 4096-token sequences; it was not used for the 4B model.

## Findings

- MS COCO (30,000 captions), FID with Gaussian blur: FID-0 27.1 against DALL-E 27.5 but behind DM-GAN and DF-GAN (26.5), with 60 candidates reranked by CapLoss. With blur applied, CogView is well ahead of DALL-E: FID-2 13.9 against 45.5 and FID-8 23.6 against 85.0.
- CapLoss 2.43, against DM-GAN 2.87, AttnGAN 3.01 and DF-GAN 3.09. IS is 18.2 against 32.2 for DM-GAN, which has the best unblurred FID and IS but comes last in human preference.
- Human evaluation (50 captions, 2,950 comparison groups, 59 evaluators kept): CogView chosen best 37.02% of the time against 59.53% for recovered ground truth.
- Training ran 144,000 steps on 512 V100s with 6,144 sequences (6.7M tokens) per batch; 96B tokens against 56B for DALL-E, which the authors list as a guessed reason for the FID gap.
- CapLoss reranking gives better FID-0 than CLIP as candidates increase; CLIP gives better IS.
- Setting the text-token loss weight to zero made images unrelated to the text (small-scale, no number given); the authors say this contradicts the DALL-E choice of a lowered text weight.

## Limits

- The authors name two limits: generation is slow, one token at a time, and the VQ-VAE blurs images.
- DALL-E's numbers were read off its published figures, and the causes of the gap are guesses since DALL-E is closed source.
- FID-0 is not better than DM-GAN or DF-GAN; the best results are on blurred FID.
- Human evaluation is small (50 captions) and has no DALL-E.
- The captioning fine-tune is not evaluated; the text-loss-weight finding is from small-scale runs without numbers.
- Potential misuse (deepfakes) and gender bias are acknowledged.

## See Also

- [[DALL-E and Parti Autoregressive Text-to-Image]] — alternative-to
- [[VQGAN Taming Transformers]] — prerequisite-for
- [[PixelRNN and Gated PixelCNN]] — prerequisite-for
- [[Diffusion and GAN Image Generation]] — prerequisite-for
