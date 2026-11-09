---
title: EnCodec Neural Audio Compression
tags: [multimodal, method]
summary: "EnCodec is a streaming encoder-decoder codec with residual vector quantization, a multiscale STFT discriminator and a gradient-fraction loss balancer, plus an optional Transformer LM for entropy coding."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-defossez-2022-high-fidelity-neural-audio-compression.md
---

# EnCodec Neural Audio Compression

The question is whether a streaming neural encoder-decoder codec, using residual vector quantization and one spectrogram-domain adversary, can be rated by listeners above Opus, EVS and Lyra-v2 at low bitrates while running in real time. The hypothesis is that a single multiscale STFT (MS-STFT) discriminator plus a gradient loss balancer trains more simply and stably than earlier codecs.

## Mechanism

The encoder is a convolutional stack (4 blocks, strides 2, 4, 5, 8, followed by a 2-layer LSTM). An RVQ with as many as 32 codebooks, each of 1024 entries, quantizes the latent, and a mirrored decoder rebuilds the audio. Training combines time-domain and mel-frequency reconstruction, a hinge adversarial loss from the MS-STFT discriminator, feature matching and a commitment loss. The loss balancer sets each weight to the share of the total gradient that its loss should account for, so the weight no longer depends on the loss's typical scale. An optional Transformer LM of 5 layers models the codes and drives a range coder for extra compression. Training uses 24 kHz mono and 48 kHz stereo audio.

## Results

- At matched bandwidth, 3 kbps EnCodec scores higher average MUSHRA than Lyra-v2 (6 kbps) and Opus (12 kbps) (self-reported). Setup: 24 kHz mono, streamable model, MUSHRA averaged over speech and music.
- Entropy coding with the LM saves roughly 25 to 40% of bandwidth, bringing the 3 kbps model to 1.9 kbps (self-reported). Setup: 24 kHz mono.
- The MS-STFT discriminator on its own reaches MUSHRA 77.5, against 62.91 for MSD plus Mono-STFT (self-reported).
- EnCodec at 3 kbps scores MUSHRA 76.8 against 71.8 for the authors' own SoundStream reimplementation (self-reported). Setup: same hyperparameters.
- Stereo 48 kHz at 6 kbps is rated like Opus at 24 kbps and above Opus at 6 kbps (self-reported).
- Without entropy coding the 24 kHz streaming model runs roughly ten times faster than real time; with it the 24 kHz real-time factor falls to 1.6 (self-reported). Setup: one thread of a 2019 MacBook Pro CPU, 6 kbps.

## Limits

- Entropy-coding probabilities were rounded to a fixed precision of one part in a million, because batch and streaming evaluation differ numerically beyond that; deployment would need more contexts, and the coder adds about 13 ms of latency and is slower.
- With entropy coding the 48 kHz model runs slower than real time, and normalisation gives it 1 s of latency.
- The comparison is against the official Lyra-v2 and a reimplemented SoundStream, because the original is not open sourced.
- No seeds or run-to-run variance, only MUSHRA confidence intervals; only reconstruction quality is evaluated, not use of the codes as tokens for language models.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[SoundStream Neural Audio Codec]] — prerequisite-for (the codec it extends)
- [[VALL-E Neural Codec Language Model TTS]] — extends (uses EnCodec as its tokenizer and decoder)
- [[Audiobox Unified Audio Generation]] — extends (generates over EnCodec dense latents)
