---
title: Structured State Space Sequence Model (S4)
tags: [llm, architecture, concept]
summary: "S4 parameterises a state space model's HiPPO matrix as normal plus low-rank so the model can be trained as a convolution and decoded as a recurrence; Gu et al. report results on Long Range Arena, raw speech and WikiText-103."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-gu-2021-efficiently-modeling-long-sequences-structured.md
---

# Structured State Space Sequence Model (S4)

Gu, Goel and Re ask whether state space models built on HiPPO matrices can be made fast enough to act as a general model for long sequences. The base system maps input u(t) to state x(t) by x'(t) = Ax(t) + Bu(t), with output y(t) = Cx(t) + Du(t). With a HiPPO matrix A, the state retains a memory of past input. S4 parameterises A as a normal matrix plus a low-rank term (NPLR), diagonalises it stably, and obtains the convolution kernel K = (CB, CAB, ..., CA^(L-1)B) via a truncated generating function, the Woodbury identity and a Cauchy kernel.

## Two views of one layer

- **Training:** the layer is a convolution y = K * u, evaluated with an FFT.
- **Inference:** after bilinear discretisation each step applies a fixed linear update (x_k from x_{k-1} and u_k, with discretised A and B) and needs constant memory and compute for each step.
- A layer holds H independent SSMs with N states each; layers are stacked with position-wise linear mixing and a nonlinearity.
- A theorem in the paper gives O~(N+L) compute and O(N+L) memory to build the kernel, and O(N) per recurrence step.

## Results (all self-reported)

- Long Range Arena (six tasks, lengths 1K to 16K, state size N=64): 80.48% average in the original submission against under 60% for every baseline; the updated Table 4 figure is 86.09. S4 solves Path-X (length 16384) at 88% against 50% chance for all prior work.
- WikiText-103 (16 blocks, each two S4 layers plus a feed-forward layer, context 8192, 800,000 steps): test perplexity 20.95 at 249M parameters, versus 20.51 for a 247M Transformer. TaLK Convolutions at 240M, the best other attention-free model, reach 23.3.
- On one A100, generation is about 60x quicker than a vanilla Transformer once S4 switches to recurrent mode (WikiText-103 and CIFAR-10); the Transformer timing leaves out the embedding and softmax layers.
- A single layer is up to 30x quicker and uses 400x less memory than the LSSL: 4.75 ms and 33.5 MB versus 140.7 ms and 13140 MB at H=512.
- At sequence length 4096, with parameters matched as in Tay et al. (4 layers, hidden size 256, about 600k parameters), S4 runs 5.19x faster than a Transformer and needs 0.091x the memory.
- Raw speech (SC10, length 16000): 98.32% accuracy; with the test sampling frequency halved and only the step size changed, 96.3%.
- Sequential CIFAR-10: S4 gets 91.13%; the Transformer scores 62.2 and the LSSL 84.65. On CIFAR-10 density estimation, S4 large without a 2-D bias reaches 2.85 bits per dimension.
- Forecasting on the Informer benchmark (ETTh1, ETTh2, ETTm1, Weather, ECL): S4 beats Informer and baselines in 40 of 50 settings; univariate Weather horizon 720 MSE is 0.245 against 0.359.
- Ablation (sequential CIFAR-10, 100K parameters): HiPPO initialisation reaches 84.27% while random initialisations trail by over 15% validation accuracy, and random NPLR matrices still perform poorly, so the gain comes from the initialisation and not the NPLR form.

## Limits

- The authors admit the WikiText-103 perplexity shortfall against the Transformer (20.95 versus 20.51) and say S4 might not fit every kind of data.
- The code computes the Cauchy kernel naively at O(NL) through pykeops; the fast, stable algorithms are not implemented for GPU, so the near-linear cost holds in theory only.
- The original NPLR parameterisation may be numerically unstable when eigenvalues lie in the right half-plane; a later change swaps Lambda-PQ* for Lambda-PP*.
- Seeds, variance and significance tests are absent; the speech baselines were swept over small grids and some would not train on one GPU. The LRA and SC numbers have been revised since, and the paper tells readers to cite Gu et al. 2022 for the revised figures.
- WikiText-103 runs at about 250M parameters; large-scale pretraining and in-context behaviour were not tested.

## See Also

- [[Mamba Selective State Space Model]] — extends
- [[Transformer Architecture]] — alternative-to
- [[Linear Attention (Transformers Are RNNs)]] — alternative-to
- [[RWKV Linear-Time Recurrent Language Model]] — alternative-to
