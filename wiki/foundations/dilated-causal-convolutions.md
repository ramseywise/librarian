---
title: Dilated Causal Convolutions
tags: [foundations, concept]
summary: Convolutions with exponentially increasing dilation factors that preserve temporal causality while growing the receptive field exponentially with depth — the key architectural innovation in WaveNet for modeling long-range audio dependencies efficiently.
updated: 2026-07-19
sources:
  - raw/pdfs/2016-09-12-wavenet.md
---

# Dilated Causal Convolutions

Dilated causal convolutions combine two properties:

1. **Causal**: the filter only looks at current and past inputs, never future ones — essential for autoregressive generation where each prediction must depend only on previous outputs
2. **Dilated** (à trous): the filter skips input values at regular intervals, effectively operating on a coarser scale without reducing resolution

## Why Dilation?

Standard causal convolutions have a receptive field that grows linearly with depth: receptive_field = layers + filter_length - 1. To model long-range dependencies in audio (16,000+ samples/second), this would require impractically many layers or huge filters.

Dilated convolutions grow the receptive field **exponentially** with depth:

```
Layer dilations: 1, 2, 4, 8, ..., 512
Receptive field per block: 1024 samples
```

Each doubling of dilation doubles the receptive field while adding only one layer of computation. Stacking multiple blocks of exponentially increasing dilations further increases both capacity and receptive field.

## Implementation

A dilated convolution with dilation factor d applies the filter at every d-th input position. It is equivalent to a convolution with a larger filter derived by inserting (d-1) zeros between each filter element, but is much more efficient to compute.

For 1-D data like audio, causal convolutions can be implemented simply by shifting the output of a normal convolution by the appropriate number of timesteps.

## Training vs Generation

- **Training**: all predictions can be made in parallel since all ground truth timesteps are known
- **Generation**: sequential — each predicted sample is fed back to predict the next

## Comparison to Other Approaches

| Approach | Receptive Field Growth | Sequential Ops | Preserves Resolution |
|---|---|---|---|
| Standard convolution | Linear | O(1) | Yes |
| Dilated convolution | Exponential | O(1) | Yes |
| Pooling/strided conv | Exponential | O(1) | No (downsamples) |
| RNN (LSTM/GRU) | Theoretically infinite | O(n) | Yes |

Dilated convolutions offer exponential growth like pooling but without losing temporal resolution, and parallelizable training unlike RNNs.

## See Also
- [[WaveNet — Autoregressive Audio Generation]] — prerequisite-for
- [[Transformer Architecture]] — alternative-to (both solve the long-range dependency problem differently)
