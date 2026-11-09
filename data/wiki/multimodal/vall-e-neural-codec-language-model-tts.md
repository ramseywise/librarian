---
title: VALL-E Neural Codec Language Model TTS
tags: [multimodal, method]
summary: "VALL-E treats text-to-speech as conditional language modeling over EnCodec codes, using a 3-second acoustic prompt for zero-shot voice cloning."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-wang-2023-neural-codec-language-models-zero.md
---

# VALL-E Neural Codec Language Model TTS

The question is whether speech synthesis can be framed as language modeling on neural codec codes conditioned on text, using large noisy training data, so that a 3-second prompt is enough to clone an unseen voice. The hypothesis is that raising the semi-supervised data to 60K hours and predicting codec tokens gives GPT-like in-context learning for new speakers.

## Mechanism

Text becomes phonemes and speech becomes EnCodec codes with 8 RVQ quantizers. A decoder-only autoregressive transformer produces the first quantizer's codes, given the phonemes and the first-layer codes of the 3-second prompt. A non-autoregressive transformer then fills in quantizers 2 to 8, and the EnCodec decoder produces the waveform. The factorisation is p(C|x, C~) = p(c1 | C~1, x; AR) times the product over quantizers j = 2..8 of p(cj | c<j, x, C~; NAR).

## Results

- On LibriSpeech test-clean, VALL-E shows higher speaker similarity and a lower WER than YourTTS (self-reported). Setup: a 4-10 s subset, a 3 s prompt, the mean of three runs, and HuBERT-Large as the ASR model.
- SMOS improves over YourTTS by 0.93 and CMOS by +0.12 on LibriSpeech (self-reported). Setup: 40 speakers.
- On VCTK it beats YourTTS by 0.23 CMOS and sits 0.04 above the ground-truth recordings, a difference to humans that is not statistically significant (self-reported). Setup: 60 speakers, each given a 3 s prompt; 49 of them had appeared in YourTTS training.
- Without the AR acoustic prompt, speaker similarity collapses while WER is unchanged. In the NAR stage, the phoneme prompt cuts WER from 19.6 to 3.0 and the acoustic prompt raises speaker similarity from 0.541 to 0.732 (self-reported). Setup: NAR ablation fed ground-truth codes for the first level.
- The authors observe qualitatively that it keeps the prompt's reverberation and emotion; this is shown on a demo page only, with no metric.

## Limits

- The AR stage has unconstrained attention alignment, so words may be unclear, missed or duplicated.
- 60K hours of read-style audiobook speech does not cover accented speakers; VCTK similarity is worse than LibriSpeech.
- Two separate models (AR and NAR) are used for the quantizers.
- The VCTK comparison with YourTTS is unfair, since YourTTS was trained on 97 of those speakers; the rater pools are small (12 and 6), and no significance test is described.
- Weights are not stated as released; no parameter count, seeds or sampling settings. Misuse risk (impersonation) is noted with a detection model suggested, not built.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[EnCodec Neural Audio Compression]] — prerequisite-for (the tokenizer VALL-E builds on)
- [[Voicebox Flow-Matching Speech Infilling]] — alternative-to (non-autoregressive; compares against VALL-E)
- [[Audiobox Unified Audio Generation]] — related (uses VALL-E as a baseline)
