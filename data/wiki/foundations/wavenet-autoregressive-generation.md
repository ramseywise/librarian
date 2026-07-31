---
title: WaveNet — Autoregressive Audio Generation
tags: [foundations, voice, concept]
summary: WaveNet (van den Oord et al., 2016) is a deep autoregressive generative model for raw audio waveforms using dilated causal convolutions — achieved state-of-the-art TTS naturalness (MOS >4.0) and demonstrated multi-speaker conditioning, music generation, and speech recognition from raw audio.
updated: 2026-07-19
sources:
  - raw/pdfs/2016-09-12-wavenet.md
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

## Relevance to Agent Engineering

WaveNet established that autoregressive neural models can generate high-quality audio directly from raw waveforms. This is the foundation for:
- Modern TTS systems used in [[Voice Agent Patterns]]
- The autoregressive generation paradigm shared with GPT-family LLMs
- Conditioning mechanisms (global/local) used in controllable generation

## See Also
- [[Dilated Causal Convolutions]] — extends
- [[Voice Agent Patterns]] — instance-of (modern voice agents build on WaveNet lineage)
- [[Transformer Architecture]] — alternative-to (autoregressive but attention-based vs convolution-based)
- [[LLM Fundamentals Interview Study Guide]] — instance-of
