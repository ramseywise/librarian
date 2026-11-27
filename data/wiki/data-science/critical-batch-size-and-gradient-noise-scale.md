---
title: Critical Batch Size and the Gradient Noise Scale
tags: [data-science, deep-learning, concept]
summary: "McCandlish et al. predict the largest useful batch size from a statistic measured in one run, the simple gradient noise scale, and show the critical batch size grows during training; Shallue et al. measure the same three-regime steps-versus-batch curve across many workloads."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-mccandlish-2018-empirical-model-large-batch-training.md
  - data/raw/papers/2026-11-08-shallue-2018-measuring-effects-data-parallelism-neural.md
---

# Critical Batch Size and the Gradient Noise Scale

Larger batches cut the number of steps to a goal, up to a point. Two 2018 studies measure where that point is. Figures are the papers' own (self-reported).

## The tradeoff and the critical batch size

McCandlish et al. run a ladder of constant batch sizes, tuning the learning rate separately for each, and note the steps S and examples E needed to hit a fixed goal. Fitting the Pareto front gives the hyperbola (S/Smin - 1)(E/Emin - 1) = 1, and Bcrit is defined as Emin/Smin. Training at Bcrit needs double the minimum steps and double the minimum examples, where compute efficiency has fallen to half of the best.

## The simple noise scale

The simple noise scale is B_simple = tr(Sigma)/|G|^2, the summed variance of gradient components divided by the squared global gradient norm. It is measured in a single well-tuned run from gradient norms at small and large batch sizes.

- Over eight tasks spanning supervised learning, RL and generative models (the image sets MNIST, SVHN, CIFAR10 and ImageNet, the Billion Word text set, the games Atari and Dota, and an SVHN VAE) it tracks Bcrit to within an order of magnitude, while Bcrit itself ranges from about 20 to above 10 million.
- The ratio B_simple/Bcrit itself differs by about 10x between tasks: under one for the autoencoder, the VAE and Dota 1v1, near one for LSTMs, and over one for image classification and Atari.
- The noise scale climbs as loss drops, and Bcrit commonly rises tenfold or more during one run. ImageNet: Bcrit 1,000 early to 15,000 averaged; Billion Word LSTM per token: 700 early to 100,000 averaged; Dota 1v1: 50,000 early to 3,000,000 averaged.
- Compared at the same loss, the noise scale barely depends on LSTM size (512, 1024 and 2048 units on Billion Word); bigger models show a larger one only because they reach lower loss.
- The noise scale varies inversely with temperature, roughly learning rate over batch size: cutting that ratio 16x raised the simple noise scale 16x (SVHN with SGD; Billion Word LSTM with Adam). Measuring it therefore needs a well-tuned learning rate.
- For Adam and RMSProp the best learning rate first rises as a power of the batch size (exponent from 0.5 to 1.0) and later levels off.
- ImageNet ResNet-50 with momentum SGD showed a noise scale between 2,000 and 100,000 through the main phase, consistent with reports that constant batches to 64 thousand work; the measured Bcrit was lower (15k against 64k).
- Predicted gain from an adaptive batch size on SVHN is about 4% (gamma = 24/25), though measured gains looked larger than the theory explains.

## Shallue et al.: steps to result across workloads

Setup: six model families, seven datasets, three optimizers (SGD, momentum, Nesterov), quasi-random search of learning rate, momentum, decay schedule and label smoothing per batch size (about 100 non-divergent trials each), recording the fewest steps to a goal validation error.

- Every workload shows perfect scaling (steps halve per doubling of batch), then diminishing returns, then no change. Perfect scaling ended between batch sizes 2^4 and 2^13; the maximum useful batch size lay between about 2^9 and 2^16.
- Momentum extends perfect scaling: ResNet-8 on CIFAR-10 (goal error 0.3, no batch norm) stops at batch size 16 with plain SGD and 256 with Nesterov momentum.
- Model matters in non-simple ways (narrower Transformers on LM1B scale further than wider ones; ResNet-50 further than VGG-11); dataset matters less and not through its size.
- Optimal effective learning rate (eta/(1-momentum)) generally rises with batch size but follows neither linear nor square-root scaling, and sometimes falls.
- The paper found no evidence that larger batches hurt out-of-sample error; quality depended on compute budget protocol (step versus epoch) more than on batch size. On ResNet-50 and ImageNet, label smoothing lowered validation error by up to about one point at large batches; with none, the 0.25 error goal could not be reached above batch 2^14.
- The authors released a database of 71,638,836 loss measurements covering 168,160 models across 35 workloads.

## Limits

- McCandlish: the theory is local and assumes a quadratic loss with an optimal step and good conditioning, and B_simple leaves out the Hessian; it says nothing about generalisation (test-set check preliminary); seeds are not averaged and Dota 5v5 Pareto fronts were not measured, so that batch size is a lower bound; models are 2018-era (CNNs, small LSTM, A2C/PPO) with no Transformer or large language model; the authors have no explanation for the task-to-task variation in B_simple/Bcrit or for adaptive-batch gains above prediction.
- Shallue: hand-specified search spaces; small batches were validated more often, giving more chances at a lucky value; only the best trial is reported; only SGD-family optimizers (no Adam); idealised data-parallel hardware with step count as the time proxy; results are retrospective, since nothing predicts the maximum useful batch size short of tuning at each size; width, depth and dataset-size effects are inconsistent; the role of the noise scale is not shown.

## See Also
- [[Large-Batch Recipes: Linear LR Scaling, Warmup and Growing the Batch]] — related (recipes for operating near and past these limits)
- [[Adam, AdamW and Decoupled Weight Decay]] — related
- [[Batch Norm Eval Mode and Small-Batch Failure]] — related
