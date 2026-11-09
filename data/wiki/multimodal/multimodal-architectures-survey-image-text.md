---
title: Multimodal Architectures Survey (Image-Text)
tags: [multimodal, reference]
summary: "A compact digest of the textbook chapter surveying image-text architectures to about 2022: captioning, text-to-image generation, images helping language models, CLIP-family contrastive models, data2vec, ViLBERT and Flamingo, with where the chapter's prose and tables disagree."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch03-multimodal-architectures.md
  - data/raw/papers/2026-11-08-multimodal-deep-learning-ch04-further-topics.md
---

# Multimodal Architectures Survey (Image-Text)

Chapter 3 of the textbook Multimodal Deep Learning (Chu, Urbanczyk, Loss et al.) covers five sub-areas: image to text, text to image, images supporting language models, text supporting vision models, and models for both. The extraction notes that almost every number is the original paper's own, reported rather than rerun, and that the chapter's only measurement is an informal laptop test of a CLIP image-search tool (about ten seconds per query over about 100 pictures). Numbers below are as the chapter reports them.

## Image to text

- The Meshed-Memory Transformer (M2) reaches CIDEr 131.2 on the MS COCO Karpathy test split, against 129.2 for the non-meshed variant and 121.8 for the original 6-layer Transformer. The prose says removing memory vectors costs about 1 point; the figure shows 0.8 for one variant and 1.8 for the full model. The prose says M2 beats all models on METEOR, but the figure shows a tie at 29.2 with AoANet.
- MS COCO holds 328,000 images with 2,500,000 instance labels, and annotation took over 70,000 worker hours.

## Text to image

- GAN line (StackGAN, AttnGAN, DM-GAN, DF-GAN), then autoregressive DALL-E 1 (250 million pairs, 12 billion parameters; a dVAE gives a 32x32 token grid and 256 text tokens precede 1024 image tokens). DALL-E won over DF-GAN with raters in over 90 percent of comparisons, although the DALL-E samples shown were the best of 512 ranked by a contrastive model.
- GLIDE (3.5 billion parameters, diffusion) gets a zero-shot MS-COCO FID of 12.24, where DALL-E is near 28; the released model has only 300 million parameters (the ch04 extraction). unCLIP uses a prior from CLIP text embedding to image embedding plus diffusion decoders; its best FID, 10.39, came with a classifier-free guidance scale of 1.25. Imagen (frozen T5-XXL) has FID 7.27 and Parti 7.23 zero-shot. Failure modes listed for Parti include blended features, details left out or repeated, objects out of place, counting and negation.
- The setups differ in zero-shot versus trained use, reranking and temperature, so the ranks do not compare like with like. The field has not agreed on one metric from IS, FID, precision/recall, CLIP score or human evaluation. Classifier-free guidance combines the unconditional and conditional noise estimates, scaled by s, with eps_hat equal to eps(empty) plus s times the difference between eps(y) and eps(empty).

## Images supporting language models

- Measured against caption data, roughly a third of the tokens of three corpora (Wiki103, English Wikipedia, CNN/DM) can be visually grounded (26.6% to 28.3%). Adding Vokenization lifts BERT's average from 79.4 to 82.1 and RoBERTa's from 77.6 to 80.6, while universal vision-language models such as ViLBERT do not beat BERT. iACE beats Voken in few-shot GLUE. Grounding helps concrete words, not abstract ones.

## Contrastive and joint models

- CLIP uses 400 million pairs, ALIGN 1.8 billion (about 800M parameters) and Florence 900 million (893M parameters). Florence reaches 83.7 zero-shot ImageNet against 76.4 for ALIGN and 76.2 for CLIP. The prose claims a clear ranking, but the table has exceptions (on Flickr30K text-to-image R@5, ALIGN's 93.8 tops 93.6). A ResNet101 at 76.2% on ImageNet keeps only 32.6% on ObjectNet.
- A prompt template adds 1.3 points zero-shot and ensembling 80 prompts adds 3.5 more. The chapter says contrastive training needs a seventh of the data in the figure caption but a factor of four slower in prose, an internal inconsistency.
- data2vec predicts averaged teacher-layer latents across modalities: ImageNet-1K top-1 84.2 (ViT-B) and 86.6 (ViT-L) against MAE 83.6 and 85.9; its GLUE gain over a RoBERTa baseline (82.7 against 82.5) is driven by CoLA.
- ViLBERT is pretrained with roughly 3.1 million Conceptual Captions pairs. Dual-stream beats single-stream (VQA test-dev 70.55 against 68.85), and shuffling words barely changes its co-attention maps although VQA drops about 15%.
- Flamingo is a frozen 70B Chinchilla (80B total), with gated cross-attention every 7th layer. Taking out the M3M web dataset lowers the chapter's ablation score, 68.4 falling to 46.9, with no metric named, and attending only to the nearest preceding image gains about 8 points. The 32-shot model beats fine-tuned state of the art on six tasks, and fine-tuning sets new state of the art on five of nine. See [[Flamingo Gated Cross-Attention VLM]].

## Limits

- Tables are images, so several prose statements disagree with them. The Flamingo ablation scores have no metric or table. The chapter is dated to about 2022.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[CLIP Contrastive Language-Image Pretraining]] — related
- [[ViLBERT Co-Attention Two-Stream Pretraining]] — related
- [[Multimodal Fusion and Multipurpose Models]] — related
