---
title: LAION-5B Open CLIP-Filtered Image-Text Dataset
tags: [multimodal, concept]
summary: "LAION-5B is an open set of 5.85B web image-text links filtered by CLIP ViT-B/32 similarity, released with safety tags and used to reproduce OpenCLIP models, with explicit warnings that it is research-only and unfinished (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-schuhmann-2022-laion-5b.md
---

# LAION-5B Open CLIP-Filtered Image-Text Dataset

Schuhmann et al. (2022) ask whether a public dataset holding billions of web image-text pairs, filtered with CLIP, can serve as training data for CLIP-class models and for text-to-image models, and where its safety and ethics limits lie. They hypothesise that open models can match OpenAI CLIP once a public dataset reaches the scale of CLIP's WIT or beyond.

## Construction

- Pairs are taken from Common Crawl alt-text, language-detected and downloaded; a pair stays only when its CLIP ViT-B/32 cosine similarity passes 0.28 for English or 0.26 for other languages. This removed about 90% of the roughly 50B starting images (self-reported).
- 5.85B pairs remain: 2.32B English, 2.26B multilingual and 1.27B of unknown language. Pipeline code, kNN indices and a web UI are open; NSFW, watermark and Q16 tags are attached rather than the images being removed.
- The dataset consists of URLs. LAION holds only the metadata, so content can disappear, and takedown happens on request or at the host.

## Validation (self-reported)

- OpenCLIP reproductions of ViT-B/32, B/16, B/16+ and L/14 were trained on LAION-400M and of B/32 and L/14 on LAION-2B-en. With compute held equal (34B samples seen), the L/14 trained on LAION-2B-en beats the LAION-400M one on zero-shot ImageNet-1k, and across six models zero-shot accuracy follows a straight line in log-log space against total compute (self-reported).
- LAION-trained L/14 is much weaker than CLIP WIT on ImageNet-A: 46.5 against 70.8 (self-reported).
- GLIDE was fine-tuned on LAION and Stable Diffusion was trained for 237k steps at 256x256 on LAION-2B-en (first stage); the extraction leaves most headline numbers blank, so only those stated are reported.

## Limits

- The authors recommend research-only use and say the dataset is not a finished product; no deployed systems without bias investigation. The datasheet says it contains explicit, racist and abusive content kept for safety research, and identifiable people were not notified or asked for consent.
- Safety tags are imperfect and not a production filter; filtering with a small CLIP inherits its biases, and alt-text is often SEO spam.
- Only ViT-B/32 filtering was tried. Test-set overlap with Common Crawl was not measured; deduplication was deferred.
- GLIDE results are qualitative (web demo, no FID or human study). Single runs, no seeds.
- A reader note from the extraction, not part of the paper: the paper was written before later reports of illegal content in the dataset.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for
- [[OBELICS Interleaved Web Document Dataset]] — alternative-to
