---
title: Emu Generative Pretraining in Multimodality
tags: [multimodal, concept]
summary: "Emu trains one 14B autoregressive model on interleaved image, video and text, predicting text tokens with cross-entropy and continuous visual embeddings with l2 regression, and decodes embeddings to pixels with a separate fine-tuned Stable Diffusion; all figures self-reported."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-sun-2023-emu.md
  - data/raw/papers/2026-11-08-sun-2024-generative-multimodal-models-context-learners.md
---

# Emu Generative Pretraining in Multimodality

Sun et al. (arXiv 2307.05222, ICLR 2024) build a model that both reads and produces images and text through one autoregressive objective.

## Mechanism

- EVA-CLIP (1B) encodes an image; a 12-block Causal Transformer, randomly initialised, compresses the 2D features into N fixed embeddings arranged as a 1D causal sequence. The paper reasons that raster-order modelling of pixels or patches performs poorly; it reports no ablation of this choice, and the extraction did not find N stated.
- The embeddings are interleaved with text tokens in a LLaMA-13B-based model (14B in total, trained end to end). Text tokens get cross-entropy loss, visual embeddings l2 regression.
- To generate an image, an [IMG] token is appended and the model produces N embeddings. A Stable Diffusion v1.5 decoder, fine-tuned afterwards (the encoder, LLM and VAE stay frozen and only the U-Net trains), turns them into pixels.
- Video becomes interleaved data through YT-Storyboard-1B: storyboard thumbnails paired with timestamped subtitles for 18M videos (1.8B images), which the authors say cuts storage about 20 times against decoding video.
- Instruction tuning attaches LoRA (rank 16) to the LLM's self-attention projections only, using ShareGPT, Alpaca, filtered LLaVA, VideoChat-11K and Video-ChatGPT data; it takes about 16 hours on 16 A100s.

## Results (self-reported)

- Pretraining: 128 A100-80G, 10K steps, about 82M samples (150B tokens), around 2 days, over a data mix of LAION-2B and LAION-COCO plus MMC4 and WebVid-10M, with the YT-Storyboard-1B set added.
- Zero-shot COCO CIDEr 112.4 for Emu and 120.4 for the instruction-tuned Emu-I. Emu-I* (prompted with text-only examples) is ahead of Flamingo-80B on VQAv2 (62.0 against 56.3), on VizWiz (38.3 against 31.6) and on MSVDQA (37.0 against 35.6). Plain Emu-I, however, is behind Emu on VizWiz, 32.2 against 34.2.
- Four-shot, with examples retrieved by EVA-CLIP similarity: VQAv2 58.4 and VizWiz 41.3, against 56.3 and 34.9 for Flamingo-9B.
- MM-Vet: Emu-I-14B scores 36.3 ± 0.3 over 5 runs, against 35.5 for LLaVA-65B and 35.9 for DreamLLM-7B (the gap to DreamLLM is within about two standard deviations); Math is 3.8 and Spat 25.2.
- Zero-shot FID on 30K COCO prompts: Emu 11.66, GILL 12.20, SD1.5 9.93, Imagen 7.27, Parti 7.23. The authors suspect the decoder's embedding space and a 15K-step training run.
- Against discrete image tokens, the paper reports Emu COCO captioning 112.4 versus 61.6 for CM3Leon, though CM3Leon has the better FID (10.82); AnyMAL-13B is ahead of Emu on VQAv2 (59.6 vs 52.0).
- Video ablation (small 7B model, single run): adding YT-Storyboard-1B moves COCO CIDEr 110.8 to 112.9 and MSVDQA 31.1 to 34.9, while OKVQA with text-only examples falls 43.9 to 42.3.
- Not best everywhere: PaLI-X-55B fine-tuned reaches 149.2 on COCO and 86.0 on VQAv2, and plain-row Emu is below Flamingo-9B* on MSVDQA, MSRVTTQA and NExTQA.

## Emu2 (Sun et al., 2024)

Emu2 asks whether taking the same generative recipe up to 37B yields in-context learning that is not tied to a task, covering both understanding and generation. It simplifies Emu: mean pooling plus a linear projection replaces the Causal Transformer (C-Former), and no ablation of that change is reported. The system joins an EVA-02-CLIP-E-plus encoder, a LLaMA-33B language model and an SDXL-base visual decoder; each image turns into 64 continuous embeddings placed among the text, trained with a classification loss on text and a regression loss on image embeddings. Pretraining ran 35,200 iterations on 162 million image-text samples plus 7 million video-text ones (self-reported).

- Few-shot VQAv2 rises from 33.5 at 0 shots to 68.8 at 16 shots, above Flamingo-80B at 66.8 (Emu2 37B base, RICES-selected shots); the paper states a lead over both Flamingo-80B and IDEFICS-80B in every few-shot setting of VQAv2, VizWiz and TextVQA (self-reported).
- On MM-Vet (average of five runs) Emu2-Chat gets 48.5 against 67.7 for GPT-4V, a gap the authors concede; without any video-QA training data it reaches 49.0 on MSVD-QA and, on MSRVTT-QA, 31.4. RefCOCO+ val is 87.05, best among generalist models (self-reported).
- Zero-shot COCO generation: Emu2-Gen CLIP-I is 0.686 against 0.674 for SDXL, but CLIP-T is 0.297 against 0.310 for SDXL and 0.320 for DALL-E 3. Subject-driven DINO score on DreamBench is 0.766 against 0.694 for Kosmos-G (self-reported).

## Limits

- Emu2, per the extraction notes: in-context learning may break down on busy scenes, crowd counting being one; zero-shot VQA is weak (33.5) unless the prompt is tuned; chat-table entries marked with an asterisk used task training sets; generation is measured solely by CLIP-I, CLIP-T and DINO, without human ratings or FID; hardware, compute, seeds and layer sizes are not stated; contamination checks are not described.
- The authors concede hallucination, slow autoregressive inference, knowledge frozen after pretraining, English-centric behaviour and web data that may contain personal images.
- The extraction notes no ablation of the Causal Transformer, of regression versus discrete tokens, or of N; no latency numbers, human evaluation of generation, hallucination benchmark or OCR and high-resolution test (input is 224x224; OCR on MM-Vet is 19.2). Generation quality is shown through cherry-picked figures, and the video ablation is one 7B run with a mixed result.
- The extraction notes that the comparison systems (Flamingo, Kosmos-1, BLIP-2, LLaVA-65B) and the LLaMA-1 and SD1.5 foundations date from mid-2023.
- The extraction flags that table text order is jumbled for Tables 2 and 3, and that the batch-size row lists 128, 64, 16, 16 in the text and 128, 128, 64, 16, 16 in Table 5.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[SPAE Semantic Pyramid AutoEncoder]] — alternative-to (a frozen LLM reads and writes images through words instead of regressed embeddings)
- [[LLaVA Visual Instruction Tuning]] — related (its instruction data is reused here)
- [[Vision-Language Model Training Families]] — prerequisite-for
- [[DreamLLM Interleaved Comprehension and Creation]] — alternative-to
- [[Chameleon Mixed-Modal Early Fusion]] — related
- [[Kosmos-2 Grounded Multimodal LLM]] — related
