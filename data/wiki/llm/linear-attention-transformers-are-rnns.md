---
title: Linear Attention (Transformers Are RNNs)
tags: [llm, architecture, concept]
summary: "Katharopoulos et al. replace the softmax in attention with a kernel feature-map dot product, which makes attention linear in sequence length and turns a causal Transformer layer into a recurrence with a fixed-size state."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-katharopoulos-2020-transformers-rnns.md
---

# Linear Attention (Transformers Are RNNs)

Katharopoulos, Vyas, Pappas et al. ask whether self-attention can cost only linear time and memory in sequence length, with quick autoregressive inference and no quality loss. Their hypothesis: swap softmax for a dot product of feature maps, then use associativity, which gives linear cost and a recurrent form.

## Mechanism

- The attention is recast as phi(Q) times (phi(K)^T V), where phi(x) = elu(x) + 1; the N x N matrix is never built, so time and memory are both O(N).
- Under causal masking the layer turns into a recurrence that carries a state S_i and a normaliser Z_i. Each step adds phi(x_i W_K) times (x_i W_V)^T to S and phi(x_i W_K) to Z; the output takes the query-side feature vector against S_i and divides by the same against Z_i.
- In the causal case the gradients come from cumulative sums. The paper states that every causal Transformer layer can be expressed as an RNN.

## Results (all self-reported, single runs)

- CIFAR-10 autoregressive generation (16 layers, 7 days on a single GPU each): 3.40 bits per dimension against 3.47 for softmax, and generation 4,462x faster than the softmax recompute baseline (batch 1 for softmax). Against stateful softmax with cached keys and values, linear is more than 50x faster (Appendix C.1, throughput). At batch 1 on GPU the latency is 61.3 s against 300.1 s.
- MNIST (8 layers, 250 epochs): 0.644 bits per dimension for linear against 0.621 for softmax, at 142.8 against 0.45 images per second.
- WSJ speech recognition (80h, 9 layers, CTC): softmax gets the lowest phone error rate (5.12). Linear scores 8.08, beating LSH-4 (9.33) and a Bi-LSTM (10.94), and each epoch is over 3x quicker.
- Copy task (4 layers, 8 heads, sequence length 128): linear converges to softmax's loss and ends below LSH-4.
- Memory benchmark on an 11GB GTX 1080 Ti: softmax tops out at length 4,096 while LSH-4 and LSH-8 reach 16,384.

## Limits

- On WSJ speech recognition softmax stays ahead, at phone error rate 5.12 compared with 8.08.
- The experiments are small: MNIST, CIFAR-10, WSJ and a copy task. None involves language modelling or a pretrained model.
- Only the elu+1 feature map is tried; random Fourier features, aimed at reusing pretrained softmax models, are left by the authors as future work.
- The speed comparisons use a softmax baseline that has no key-value caching, and a stateful softmax narrows much of the difference (Appendix C). At batch size 1 the speedup on GPU is about 4.9x, since the loop over the sequence dominates.
- No seeds or variance are reported.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Mamba-2 and Structured State Space Duality]] — extends
- [[RWKV Linear-Time Recurrent Language Model]] — extends
- [[Efficient Attention Approximations]] — related (Performer is a kernel method too)
- [[Structured State Space Sequence Model (S4)]] — alternative-to
