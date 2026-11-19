---
title: WaveNet — Autoregressive Audio Generation
tags: [multimodal, speech-and-audio, voice, concept]
summary: WaveNet (van den Oord et al., 2016) is a deep autoregressive generative model for raw audio waveforms using dilated causal convolutions — achieved state-of-the-art TTS naturalness (MOS >4.0) and demonstrated multi-speaker conditioning, music generation, and speech recognition from raw audio.
updated: 2026-11-19
sources:
  - data/raw/pdfs/2016-09-12-wavenet.md
  - data/raw/papers/2026-11-07-oord-2016-wavenet.md
---

# WaveNet — Autoregressive Audio Generation

WaveNet (DeepMind, 2016) generates raw audio waveforms sample-by-sample, modeling the joint probability as a product of conditional distributions:

```
p(x) = product(p(x_t | x_1, ..., x_{t-1}))
```

Each audio sample is conditioned on all previous samples. Despite operating at 16,000+ samples per second, the model produces audio rated as significantly more natural than previous TTS systems.

## Architecture

### [[Dilated Causal Convolutions]]

The core innovation. Causal convolutions ensure the model respects temporal ordering (no future leakage). Dilation exponentially increases the receptive field without proportionally increasing computation:

```
Dilation pattern: 1, 2, 4, ..., 512, 1, 2, 4, ..., 512, ...
```

Each block of dilations 1→512 gives a receptive field of 1024 samples. Stacking blocks further increases capacity and receptive field. This is more efficient than RNNs and avoids their sequential computation bottleneck.

### Gated Activation Units

From gated PixelCNN:
```
z = tanh(W_{f,k} * x) ⊙ σ(W_{g,k} * x)
```
Performed significantly better than ReLU for audio modeling.

### Residual and Skip Connections

Residual blocks are stacked throughout the network. Skip connections from each layer are summed and processed through ReLU → 1x1 conv → ReLU → 1x1 conv → softmax output.

### Softmax Output with µ-law Companding

Instead of predicting continuous values, WaveNet quantizes audio to 256 values using µ-law companding, then predicts a categorical distribution via softmax. This is more flexible than mixture models — no assumptions about distribution shape.

## Conditioning

### Global Conditioning
A single latent vector h (e.g., speaker identity as one-hot) that influences all timesteps:
```
z = tanh(W_f * x + V_f^T h) ⊙ σ(W_g * x + V_g^T h)
```

### Local Conditioning
A time-varying signal (e.g., linguistic features for TTS) upsampled to audio rate via transposed convolutions:
```
z = tanh(W_f * x + V_f * y) ⊙ σ(W_g * x + V_g * y)
```

## Results

### Text-to-Speech
- MOS 4.21 (EN) and 4.08 (ZH) — significantly better than LSTM-RNN parametric (3.67/3.79) and HMM concatenative (3.86/3.47) systems
- Reduced the gap between synthetic and natural speech by **51%** (EN) and **69%** (ZH)
- Conditioning on both linguistic features and log-F0 values solved prosody issues

### Multi-Speaker
A single WaveNet models 109 speakers by conditioning on speaker identity. Adding speakers actually improved validation performance — internal representations are shared.

### Music Generation
Harmonically pleasing samples but lacked long-range coherence (receptive field ~300ms captures only 2–3 phonemes).

### Speech Recognition
18.8 PER on TIMIT — best result from a model trained directly on raw audio.

## Setup and evidence

The 2016 paper's setup, from the extraction (numbers are the authors' own, self-reported):

- TTS: North American English, one female speaker with 24.6 h of audio, scored on 100 held-out sentences by crowdsourced MOS (8 raters per stimulus; roughly 40% of ratings were discarded because raters lacked headphones); Mandarin 34.8 h. WaveNet is conditioned on linguistic features and log F0. English baselines score 3.86 (concatenative) and 3.67 (LSTM parametric).
- Multi-speaker: VCTK, 44 h, one-hot speaker conditioning, 109 speakers.
- Given a 240 ms receptive field and only linguistic features, WaveNet at times put stress on the wrong words, and F0 conditioning corrected that. The roughly 300 ms receptive field of the multi-speaker model remembers only the last 2-3 phonemes.
- Music (MagnaTagATune and YouTube piano) needs a large receptive field yet lacks long-range consistency over several seconds; evaluation is by listening only.
- TIMIT uses a joint next-sample and frame-classification loss, mean-pooled to 10 ms frames.
- The μ-law transform is f(x) = sign(x) ln(1 + μ|x|) / ln(1 + μ) with μ = 255, which avoids a 65,536-way softmax over 16-bit audio.

The gated unit and autoregressive softmax come from the PixelCNN line, see [[PixelRNN and Gated PixelCNN]]; [[Jukebox Multi-Scale VQ-VAE Music]] takes raw-audio generation to music with a VQ-VAE hierarchy.

## Relevance to Agent Engineering

WaveNet established that autoregressive neural models can generate high-quality audio directly from raw waveforms. This is the foundation for:
- Modern TTS systems used in [[Voice Agent Patterns]]
- The autoregressive generation paradigm shared with GPT-family LLMs
- Conditioning mechanisms (global/local) used in controllable generation

Related speech generators are compared on [[Speech and Audio Generation and Recognition]].

## Limits

- The paper omits training hyperparameters: optimiser, learning rate, batch size, steps, layer and channel counts, parameter count and hardware.
- Each audio sample needs its own sequential step, so generation is slow; no speed figure is given.
- Without F0 conditioning, a 240-300 ms receptive field is too short to keep prosody and phoneme-level coherence, and generated music does not stay consistent over longer spans.
- Music is judged only by listening.
- The evaluation covers single-speaker data and just 100 test sentences.

## See Also
- [[Dilated Causal Convolutions]] — extends
- [[Speech and Audio Generation and Recognition]] — related (later codec-token and flow-matching audio generators)
- [[Voice Agent Patterns]] — instance-of (modern voice agents build on WaveNet lineage)
- [[Transformer Architecture]] — alternative-to (autoregressive but attention-based vs convolution-based)
- [[SoundStream Neural Audio Codec]] — related
- [[PixelRNN and Gated PixelCNN]] — prerequisite-for
- [[Jukebox Multi-Scale VQ-VAE Music]] — extends
- [[VALL-E Neural Codec Language Model TTS]] — related
