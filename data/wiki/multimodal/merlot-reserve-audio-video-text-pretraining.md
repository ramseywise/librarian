---
title: MERLOT Reserve Audio-Video-Text Pretraining
tags: [multimodal, method]
summary: "MERLOT Reserve pretrains on video frames, subtitles and audio with a contrastive span-matching objective, and transfers to VCR, TVQA, Kinetics-600 and zero-shot tasks."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zellers-2022-merlot-reserve.md
---

# MERLOT Reserve Audio-Video-Text Pretraining

The question is whether representations that join video frames, subtitles and audio can be learned with a self-supervised contrastive span objective, then carry over to vision-language tasks both after fine-tuning and zero-shot, including tasks without sound. The hypothesis is that learning across all modalities at once, aligned in time and with each modality teaching the others, helps even tasks without audio such as VCR.

## Mechanism

Video is cut into 5-second segments, each holding a middle frame and either ASR text or audio. Separate encoders (ViT for frames, AST for audio, a text-span encoder) feed one bidirectional joint Transformer. A quarter of the text and audio subsegments are swapped for MASK; the model matches each MASK output, contrastively, with an independent encoding of the hidden span, and adds a frame-to-transcript contrastive loss. Pretraining starts from scratch on YT-Temporal-1B. The model is then fine-tuned on VCR, TVQA or Kinetics-600, or used with no fine-tuning.

## Results

- Reserve-L reaches 72.0 VCR Q->AR test accuracy (self-reported), more than 5 points above the strongest earlier single model, ERNIE-ViL-Large at 66.3. Setup: VCR test leaderboard, 10 pretraining epochs with resolution adaptation, then 5 fine-tuning epochs.
- TVQA test: 85.6 with subtitles, 84.8 with audio only, 86.1 with both softmaxes averaged (self-reported). Setup: Reserve-L, one jointly fine-tuned model.
- Kinetics-600 val top-1 is 91.1 with audio, 1.5 above the larger MTV-Huge, which uses vision only, and audio contributes 1.7 points for Reserve-L (self-reported).
- After one pretraining epoch, the contrastive span objective is 2.5 points ahead of Mask LM on VCR Q->A val (self-reported). Setup: vision plus text only.
- Zero-shot STAR overall is 40.5 for Reserve-B with audio against 38.0 for CLIP ViT-B/16 (self-reported); zero-shot MSR-VTT QA is 13.6 top-1 for Reserve-L with audio.
- A Reserve-L VCR candidate costs 341 GFLOPs against 1867 for UNITER-Large (self-reported).
- Zero-shot person recognition stays under 11% for voice, image and both, where CLIP reaches 86%; the authors present this as a privacy benefit (self-reported). Zero-shot audio classification is behind the supervised AudioCLIP model by 16% on ESC50 and by 6.4% on US8K (self-reported).
- Pretraining ran on TPU v3-512, 5 days for B and 16 days for L, with carbon of about 8.23 tons CO2e (self-reported).

## Limits

- It learns only from 40-second videos, depends on ASR for subtitles, and can match but not generate text and audio.
- Runs are single, with no seeds or significance tests; loss spikes while pretraining Reserve-L are unexplained, and the larger model is worse than the base model on zero-shot STAR, which the authors attribute to limited prompt search.
- On scripted dialogue in TVQA, audio adds 0.5 points over subtitles; the transcript carries most of the signal.
- Inconsistencies in the paper: Table 7 gives 71.5 for Reserve-L on VCR Q->AR, whereas Table 2 gives 72.0; the MSR-VTT label space is 1k in the text and 2000 in the appendix; the sample rate is 22050 in one place and 22500 Hz in another.
- No retrieval evaluation; this is a representation-learning paper.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (an audio-conditioned vision-language model)
- [[CLIP Contrastive Language-Image Pretraining]] — prerequisite-for (the contrastive loss and zero-shot baseline)
- [[Vision-Language Model Training Families]] — related
- [[MERLOT Multimodal Script Knowledge]] — prerequisite-for
- [[VIOLET Masked Visual-Token Modeling]] — related
