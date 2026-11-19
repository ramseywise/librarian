---
title: Sparse Transformer Factorized Attention
tags: [llm, architecture, concept]
summary: "Child et al. factorise the attention matrix into two sparse patterns, strided and fixed, that connect every position over two steps, cutting cost to O(n sqrt n) for byte-level density modelling of text, images and audio."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-child-2019-generating-long-sequences-sparse-transformers.md
---

# Sparse Transformer Factorized Attention

Child, Gray, Radford et al. ask whether sparse factorisations can bring self-attention below quadratic cost in sequence length yet keep dense attention's density-modelling quality on images, text and audio. Their hypothesis is that factorised patterns linking every position across several steps can rival the rich patterns that full attention learns. The model is a decoder-only Transformer using pre-activation residual blocks, trained autoregressively on raw bytes from four sources: classical music audio, ImageNet 64x64, Enwik8 and CIFAR-10.

## Patterns

- **Strided attention:** one head covers the l previous positions and the other covers every lth position, with l near sqrt(n). Formally A1_i = {t, ..., i} for t = max(0, i - l), and A2_i = {j : (i - j) mod l = 0}.
- **Fixed attention:** one head stays inside its own block of length l; the other reads the final c positions of every block, which act as summary cells reaching all later positions.
- **Merged head:** one head that covers the union of the positions that the factorised heads cover between them.
- Supporting pieces: a restructured residual block and initialisation for depth, recomputation of attention matrices to save memory, and fast block-sparse GPU kernels with mixed precision.

## Results (all self-reported)

- Enwik8 (merged heads, context of 12,288 tokens; model of 30 layers with d=512, 8 heads, stride 128 and c=32): the 95M fixed model gets 0.99 bits per byte, level with a 277M Transformer-XL and ahead of an 88M Transformer-XL (1.03). Dense attention scores 1.00 and takes 1.31 time per iteration; fixed sparse scores 0.99 in 0.55 (timing unit and hardware not stated). The strided pattern performs badly on text.
- Enwik8 bits per byte improves monotonically as the minimum evaluation context grows, up to 12,160 of 12,288.
- CIFAR-10 (128 layers, d=256): the strided 59M model sets state of the art, and strided beats dense and is faster (context 3,072).
- ImageNet 64x64 (one run; 48 layers, 16 heads, d=512, trained 70 epochs over 7 days on 64 V100s): the 152M strided model improves on the previous best result.
- Audio (classical music, 12 kHz mu-law, length 1,048,576, strided): a 4x longer sequence needs about 8x fewer parameters, and a 3M-parameter model trains on million-timestep sequences.
- With no table behind it, the paper claims that recomputation by itself makes dense attention networks of hundreds of layers feasible at length 16,384.

## Limits

- Only density modelling in bits per byte; no downstream tasks.
- Strided attention fails on text, and the fixed pattern costs c times what strided does.
- The paper attributes sparse beating dense to inductive bias or an unexplained optimisation problem with full attention.
- Fixed patterns cannot represent the global, data-dependent patterns that dense models display.
- The ImageNet result comes from one run; audio data processing was unavailable, so there is no comparison with other work, and audio sample quality drops at longer lengths because of reduced capacity.
- Batch size, ImageNet and audio learning rates and audio layer counts are not stated.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Longformer Sliding-Window and Global Attention]] — related (the most similar attention pattern, per the Longformer paper)
- [[Efficient Attention Approximations]] — related
- [[Transformer-XL Segment Recurrence]] — related (another route to long context, via recurrence)
