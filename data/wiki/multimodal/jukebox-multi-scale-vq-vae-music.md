---
title: "Jukebox Multi-Scale VQ-VAE Music"
tags: [multimodal, speech-and-audio, concept]
summary: "Jukebox compresses 44.1 kHz audio with three separate VQ-VAEs and models the discrete codes with a 5B top-level Transformer prior and two 1B upsamplers, conditioned on artist, genre, timing and lyrics; sampling takes hours per minute."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-dhariwal-2020-jukebox.md
---

# Jukebox Multi-Scale VQ-VAE Music

Dhariwal and colleagues ask whether a single model can produce varied, high-fidelity music that includes singing, working directly on raw audio and staying coherent over minutes. Figures are the authors' own (self-reported).

## Method

- Three independent VQ-VAEs shrink 44.1 kHz audio by factors of 8, 32 and 128 (bottom, middle and top levels). They use random restarts and a spectral loss.
- Autoregressive models of the codes are sparse (axis-aligned) Transformers: a 5B prior at the top level and two 1B upsamplers; conditioning is artist, genre, timing and unaligned lyrics.
- Sampling runs top level first and then downwards (ancestral), and comes in windowed and primed variants. In **windowed sampling** the sampling window advances by half the context and sampling continues conditioned on that half context.
- An 8192-token context covers roughly 24 s at the top level, 6 s at the middle and 1.5 s at the bottom.

## Findings

- VQ-VAE reconstruction error rises with hop length: the bottom level with restarts is at -23.0 dB, the top level -8.3 dB (5,000 held-out 3 s segments).
- Cutting the codebook from 2048 to 256 entries degrades the bottom level's reconstruction, from -23.0 dB to -15.9 dB. At the top level, dropping the spectral loss gives -6.3 dB and one hierarchical autoencoder instead of separate ones gives 2.9 dB, against -8.3 dB.
- Generating a minute of top-level tokens with the 5B prior takes about an hour; upsampling that minute then needs about 8 hours, since it is sequential. The authors state the asymmetry as fast parallel likelihood evaluation against slow autoregressive sampling.
- Judged by listening, samples hold together over the span the top level sees (about 24 s) but have no long-range structure, for instance repeating choruses.

## Place in this wiki

The raw-audio autoregressive predecessor is [[WaveNet Autoregressive Generation]]; the extraction lists distilling a faster sampler (Parallel WaveNet) as a suggestion. Related audio pages are [[Speech and Audio Generation and Recognition]] and [[SoundStream Neural Audio Codec]].

## Limits

- Evaluation is by listening; the authors judge MOS-style or FID-style metrics not meaningful here.
- Output lacks long-term structure such as choruses that recur, and has noise or scratchiness at fine scale.
- Training songs are mostly English; with linear windowing, lyric alignment is weaker for hip hop and rap.
- Very slow sampling.
- Temperature, top-p and other sampling hyperparameters are not stated.

## See Also

- [[WaveNet Autoregressive Generation]] — prerequisite-for
- [[Speech and Audio Generation and Recognition]] — prerequisite-for
- [[SoundStream Neural Audio Codec]] — related
- [[Auto-Encoding Variational Bayes]] — prerequisite-for
