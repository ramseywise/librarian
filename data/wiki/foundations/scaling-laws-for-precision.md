---
title: Scaling Laws for Precision
tags: [foundations, concept]
summary: "Kumar et al. fit loss as a function of parameters, data and numeric precision: post-training quantization hurts more as data grows, compute-optimal training precision is about 7-8 bits, and weights lose effective parameters below roughly 6-7 bits."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kumar-2024-scaling-laws-precision.md
---

# Scaling Laws for Precision

Kumar et al. (arXiv 2411.04330, 2024) add numeric precision to the usual loss-versus-size-and-data scaling fits.

## Reported findings

Every constant, fit quality and bit-width threshold below is the authors' own fit to their own training runs (self-reported).

Setup: OLMo-style models of 30M to 220M parameters trained on Dolma, with GPTQ post-training quantization at INT3 to INT6.

- **Post-training degradation.** The loss added by quantization is a power law in tokens per parameter (D/N) times an exponential in bits. Fitted constants: C_T 0.0598, gamma_D 0.5068, gamma_N 0.3439, R2 0.97. Past a critical data size, additional pretraining makes the quantized model worse.
- **Compute-optimal precision.** Under an integer fit, training precision of about 7-8 bits is compute-optimal. With parameters fixed, the best precision grows with the log of compute.
- **Effective parameters.** Weight precision Pw scales the parameter count as Neff = N(1 - e^(-Pw/gamma_w)), with gamma_w 2.6745; the effect saturates around 6-7 bits.
- A unified law covering both regimes has R2 0.90 over more than 1000 points from 465 runs.

## Limits

- Loss only, not downstream accuracy; a fixed vanilla architecture; the authors say the fitted constants are unlikely to be useful elsewhere; weights-only post-training quantization; the floating-point result is only a hint.
- Internal inconsistency noted by the extraction: the abstract says up to 1.7B parameters, but the main sweep is 30M to 220M; 1.7B appears only in one figure panel and the Figure 6 text says 220M to 1.6B.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (quantization as a serving lever)
- [[BitNet b1.58 Ternary Weights]] — related (training at very low precision)
- [[MoE Expert Offloading]] — related (hard quantization of expert weights in practice)
- [[FP8-LM Mixed-Precision FP8 Training]] — related
