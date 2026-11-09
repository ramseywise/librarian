---
title: Audiobox Unified Audio Generation
tags: [multimodal, method]
summary: "Audiobox pre-trains a 330M flow-matching Transformer by infilling unlabeled speech, music and sound, then fine-tunes it for speech, sound and a unified model controlled by text descriptions and voice prompts."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-vyas-2023-audiobox.md
---

# Audiobox Unified Audio Generation

The question is whether a single flow-matching model can produce speech and sound from text descriptions, example audio or a mix of both, with more control than separate speech and sound models. The hypothesis is that self-supervised infilling pretraining on speech, music and sound together, followed by fine-tuning, matches or beats models built for one modality.

## Mechanism

A 330M-parameter Transformer is trained with conditional flow matching on dense EnCodec latents. Audiobox SSL is pretrained by masked-frame infilling on 160K h of speech, 20K h of music and 6K h of sound. Fine-tuning gives Audiobox Speech (transcript-guided), Audiobox Sound (caption-guided) and a unified Audiobox that accepts a transcript, a description, a voice prompt and audio context. A voice prompt is an extra utterance from the same speaker that conditions vocal style only. Inference uses a midpoint or dopri5 ODE solver (or a Bespoke solver for 4 steps), classifier-free guidance and CLAP re-ranking. Joint-CLAP scores description-conditioned speech; it pairs WavLM and RoBERTa encoders and was trained on descriptions of speech and sound.

## Results

- The Bespoke solver with 4 steps keeps the quality of dopri5 at 8 NFE versus about 280 NFE (self-reported). Setup: zero-shot TTS on LibriSpeech.
- Full fine-tuning cuts WER by 23% to 43% relative to LoRA, except on Switchboard, and LoRA is 15% to 30% worse for sound (self-reported).
- General pretraining boosts sound generation by about 20% FAD (self-reported). CLAP re-ranking moves FAD from 0.91 to 0.78 and CLAP score from 0.60 to 0.71.
- Joint-CLAP tracks human relevance ratings while public CLAP does not; public CLAP is about 30x worse on speech retrieval than on sound (self-reported).
- WER differs by about 1.5% across gender and accent groups with no significant gap (self-reported). Setup: zero-shot TTS over 64 accents, 400 samples per accent.
- Watermark detection is near 0% false positive and false negative rates (self-reported).

## Limits

- Description control is held back by the shortage of paired audio-description data: unseen concepts such as regional accents cannot be generated, and annotators disagree on emotion, age and quality.
- Most speech captions were produced by an LLM from coarse tags; only 500 hours are annotated by humans.
- No significance tests or seeds; data and weights are not released.
- Compared with Audiobox Speech the unified model has slightly worse WER (average 4.8 against 4.0), and its FAD is worse than Audiobox Sound's.
- The data is mostly English; the VoiceLDM and AudioLDM2 baselines were given averaged CLAP embeddings, a best-effort comparison. Fairness was tested only on zero-shot TTS.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[Voicebox Flow-Matching Speech Infilling]] — prerequisite-for (the infilling model it extends)
- [[EnCodec Neural Audio Compression]] — prerequisite-for (the latent features)
- [[Make-An-Audio Text-to-Audio Latent Diffusion]] — alternative-to (diffusion rather than flow matching for text-to-sound)
