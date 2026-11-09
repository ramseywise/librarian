---
title: SoundStream Neural Audio Codec
tags: [multimodal, method]
summary: "SoundStream is an end-to-end trained codec built from a causal convolutional encoder, a residual vector quantizer with quantizer dropout, and an adversarially trained decoder."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-zeghidour-2021-soundstream.md
---

# SoundStream Neural Audio Codec

The question is whether one neural codec, trained end to end, can code speech, music and other audio at low bitrates with better quality than Opus and EVS, while allowing variable bitrate and low latency.

## Mechanism

A fully convolutional causal encoder in the SEANet style feeds a residual vector quantizer (RVQ, Nq layers with codebooks of 1024 entries), and a matching decoder reconstructs the audio. Training pairs an STFT discriminator with a waveform discriminator at three scales, with three kinds of loss: adversarial (hinge), feature matching, and mel reconstruction at several scales. RVQ cascades quantizers over successive residuals. Quantizer dropout samples the number of active quantizers uniformly in [1, Nq] per example, which makes one model usable at several bitrates. FiLM conditioning switches denoising on or off, giving joint compression and enhancement.

## Results

- At 3 kbps the baselines that match it are EVS (9.6 kbps) and Opus (12 kbps), which use 3.2x to 4x more bits (self-reported). Setup: a crowdsourced test modelled on MUSHRA, 200 clips with 20 ratings each, 24 kHz audio.
- At 6 kbps the baselines need 2.2x to 2.6x the bits; at the 12 kbps operating point they need 1.3x to 1.6x (self-reported). Setup: the same listening test.
- Using a fixed mel filterbank instead of the learned encoder lowers ViSQOL from 3.96 to 3.33 when coding at 6 kbps (self-reported). The learned encoder at 3 kbps still outperforms the mel-filterbank variant at 6 kbps.
- The default model (8.4M parameters) runs in real time on a single CPU thread of a Pixel4 at 6 kbps, with ViSQOL 4.01 (self-reported).
- Entropy coding could save between 7% and 20% of the bitrate; this is an estimate from the empirical entropy of the RVQ symbols under a memoryless-source assumption, not an implemented result.
- One model doing compression and enhancement together comes close to separate SEANet and SoundStream pipelines while using half the compute (self-reported). Setup: 2 s noisy VCTK clips, input SNR 0 dB.

## Limits

- Optimizer, learning rate, batch size, step count, hardware and dataset sizes go unstated, so the paper alone does not let you rerun training.
- Bitrate is constant, and the entropy coder is not built; evaluation clips run 2 to 4 seconds, with ViSQOL as the objective metric and MUSHRA used only in the headline comparison.

- The authors collected the real-world evaluation set themselves and state no release.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[EnCodec Neural Audio Compression]] — extends (closest successor; RVQ codec with a single spectrogram discriminator)
- [[WaveNet — Autoregressive Audio Generation]] — related (a sample-by-sample alternative to codec tokens)
