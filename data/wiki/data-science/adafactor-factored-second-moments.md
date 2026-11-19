---
title: Adafactor Factored Second Moments
tags: [data-science, concept]
summary: "Adafactor keeps Adam's second-moment estimate for a matrix as row and column sums (O(n+m) memory instead of O(nm)), drops momentum, and uses update clipping and a 1 - t^-0.8 decay to stay stable."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-shazeer-2018-adafactor.md
  - data/raw/papers/2026-11-07-a-2020-scaling-laws-neural-language-models.md
---

# Adafactor Factored Second Moments

Shazeer and Stern ask whether Adam's per-parameter optimizer memory can be cut to sublinear without losing quality or stability. By the authors' account, Adam stores two additional values for every parameter, which triples the memory needed for parameters. All results below are (self-reported) and come from one task.

## Mechanism

Adafactor is Adam with four changes:

- **Factored second moment.** For an n x m weight matrix the second-moment accumulator is a rank-1 estimate built from row and column sums (I-divergence optimal), so memory falls from O(nm) to O(n+m).
- **No momentum.**
- **Update clipping.** The update on a weight X is scaled down whenever RMS(U_t) exceeds a threshold d (d=1 in Algorithm 6).
- **Increasing decay.** beta2_t = 1 - t^-0.8 instead of a fixed beta2, with step sizes rho_t, the smaller of 1e-2 and t^-0.5, scaled by the parameters' RMS (the relative step size, floored at eps2 = 1e-3; eps1 = 1e-30).

The authors' hypothesis is that stale second-moment estimates produce updates larger than intended, which destabilises training.

## What the ablations showed

Setup: Tensor2Tensor Transformer on WMT 2014 En-De, 100,000 steps, about 4,096 input plus 4,096 target tokens per batch, newstest2013, beam 4.

- Factored second moments without momentum (with warmup) matched Adam without factoring.
- Without warmup, factored beta2=0.999 with no clipping was unstable; clipping at d=1 restored stability without warmup, but below the warmup score. Baseline Adam without warmup and without momentum collapsed.
- Fast decay (beta2=0.9) scored 18.4 against 25.6 for slow decay.
- Pairing the rising decay with clipping at d=1 matched the best score obtained with warmup and also trained stably without it; full Adafactor with no momentum was stable either way.
- A column-mean-only second-moment estimate failed; row-mean worked.
- Plain SGD did worse and was very sensitive to the learning rate; its best stable score, 24.3, came at lr 200*s_t with warmup.
- With embeddings not shared with the softmax and naively scaled (sigma 1/sqrt(dmodel), multiplier 1), Adafactor with relative step size was more resilient than Adam (50,000 steps, batch 16,384 tokens).

Kaplan et al. list Adafactor as the optimizer for their models above 1B parameters; see [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]].

## Limits

- Only one task and architecture were tried, with neither a language-model run nor a run at billions of parameters, even though memory is the stated motivation.
- Single runs with no seeds or variance; BLEU on the dev set only.
- Batches are one eighth the size used by Vaswani et al., so the scores cannot be set against published ones.
- The authors say the effect of relative step size on stability is unclear, since step sizes are not comparable.
- No convergence guarantee for the non-convex case.

## See Also
- [[Adam, AdamW and Decoupled Weight Decay]] — prerequisite-for
- [[Scaling Laws: Kaplan, Chinchilla and Error Landscapes]] — related
- [[AlgoPerf: Time-to-Result Benchmark for Training Algorithms]] — related
