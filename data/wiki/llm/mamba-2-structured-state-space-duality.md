---
title: Mamba-2 and Structured State Space Duality
tags: [llm, architecture, concept]
summary: "Dao and Gu relate state space models to attention through semiseparable matrices (structured state space duality), derive a matmul-based chunked SSM algorithm, and use it in the Mamba-2 block."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-dao-2024-transformers-ssms.md
---

# Mamba-2 and Structured State Space Duality

Dao and Gu ask how structured state space models such as Mamba relate to attention variants, and whether that relation gives a faster SSM layer that stays competitive with Transformers. Their hypothesis is that SSMs and attention are linked through structured matrices, so Transformer algorithms and systems work can transfer to SSMs.

## Mechanism

- **Semiseparable matrices:** call a lower-triangular matrix N-semiseparable when each submatrix at or under the diagonal has rank no greater than N. An SSM with state size N over T steps can be evaluated in O(TN) time (Theorem 3.7).
- **Structured masked attention (SMA):** linear attention generalised by multiplying the attention matrix with a structured mask L. Theorem 5.2 says an autoregressive SMA of bounded order needs a semiseparable mask.
- **Structured state space duality (SSD):** an SSM whose A is a scalar times the identity and an SMA using a 1-semiseparable mask are duals of each other, sharing the same linear and quadratic computation forms.
- **SSD algorithm:** a chunked block decomposition; diagonal blocks use the quadratic form and off-diagonal low-rank blocks pass through states, all as matrix multiplications. Training costs O(TN^2) FLOPs and inference O(N^2) memory, against T^2 N training FLOPs for attention (Theorem 6.1, P=N).
- **Mamba-2 block:** projections run in parallel, with one added normalisation and a multi-input head layout (X differs per head; B and C are shared across heads). The paper argues this cuts the per-block tensor-parallel all-reduces from two to one; it reports no training throughput for that.

## Results (all self-reported)

- Speed (A100 80GB PCIe): the SSD implementation runs 2-8x faster than Mamba's tuned selective scan (state dimension 64), overtakes FlashAttention-2 from sequence length 2K, and is 6x faster at 16K.
- Language (Pile, 300B tokens, GPT-NeoX tokenizer, 7 zero-shot tasks): at 2.7B parameters Mamba-2 scores a higher zero-shot average than both Mamba-2.8B and Pythia-2.8B, with Pile validation perplexity of 6.09 versus 6.22 for Mamba-2.8B. Against Transformer++ at that size the averages are close, and a version with 6 added attention layers improves on it.
- Hybrid (350M, 48 layers, 7B Pile tokens): about 10% attention layers gives the best perplexity, 8.26 with 6 attention blocks, against 8.60 for pure Mamba-2 and 8.68 for Transformer++.
- Head patterns (125M, 2.5B tokens): multi-input 11.66 against 12.62 for multi-query and 12.59 for multi-key. The Mamba-2 block reaches 11.49 against 11.76 for the Mamba-1 block, with 126.5M against 129.3M parameters.
- MQAR (T of 256, 512 and 1024; 2 layers): Mamba-2 does markedly better than Mamba-1 even when both use state size N=16, and gains further at N=64 and 256 (values read off a figure).
- Scaling (Chinchilla-style laws, roughly 125M to 1.3B parameters, Pile, length 8192): Mamba-2 sits on a better perplexity-versus-wall-clock frontier than both Mamba and Transformer++.
- Kernel feature maps borrowed from linear attention work (cosFormer, Performer, Based, ReBased) gave no gain over plain pointwise activations at 130M and 380M parameters.

## Limits

- SSD restricts A to a scalar times the identity, which the authors describe as trading expressivity for hardware efficiency; it does not generalise softmax attention or any kernel without a finite feature map.
- Training a whole model may run slower than a Transformer near length 2K: Mamba-2 stacks L SSD layers, whereas a Transformer stacks L/2 attention layers and L/2 MLP layers.
- The largest model is 2.7B on 300B tokens; no variance or significance tests; no GPU-hours or training hardware reported.
- The authors cannot say which design change accounts for the MQAR improvement over Mamba-1 at the same N. In the 2.7B hybrid comparison, extra MLP layers lowered quality, and Mamba-2 by itself ties Transformer++ instead of surpassing it.

## See Also

- [[Mamba Selective State Space Model]] — prerequisite-for
- [[Linear Attention (Transformers Are RNNs)]] — prerequisite-for
- [[Bi-Mamba Binarized State Space Model]] — extends
- [[FlashAttention and FlashAttention-2]] — related (speed baseline)
