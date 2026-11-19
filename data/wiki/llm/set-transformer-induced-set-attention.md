---
title: Set Transformer Induced Set Attention
tags: [llm, architecture, concept]
summary: "Lee et al.'s Set Transformer builds permutation-invariant set models from attention blocks, with inducing points (ISAB) that cut encoder cost from O(n^2) to O(nm) and learnable seed vectors (PMA) that pool a set by attention."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lee-2018-set-transformer.md
---

# Set Transformer Induced Set Attention

Lee, Lee, Kim et al. ask how a set network can capture interactions among elements, remain permutation invariant, and scale to big sets. Their hypothesis: attention in both the encoder and the aggregation step does better than encoding each element alone and then applying a fixed pooling, and inducing points turn the quadratic cost in set size into a linear one without costing accuracy.

## Blocks

- **MAB:** MAB(X, Y) = LayerNorm(H + rFF(H)), where H = LayerNorm(X + Multihead(X, Y, Y)). It is a Transformer encoder block minus positional encoding and dropout.
- **SAB:** SAB(X) = MAB(X, X).
- **ISAB:** ISAB_m(X) = MAB(X, H), where H = MAB(I, X) and I is a set of m trainable inducing points. For fixed m the cost is linear in set size; a stack of l SABs costs O(l n^2); a stack of l ISABs costs O(l n m).
- **PMA:** PMA_k(Z) = MAB(S, rFF(Z)), using k learnable seed vectors S; a SAB and a row-wise feed-forward layer follow, producing k correlated outputs.
- The authors prove permutation invariance and that the model can approximate any permutation-invariant function (universal approximation).

## Results (all self-reported)

- Max regression (n up to 10, 5 runs): SAB+PMA has an error close to max pooling and far under mean and sum pooling. Unique-character counting (5 runs, on Omniglot sets of 6 to 10 images): SAB+PMA is best; SAB+pooling improves a great deal on rFF+pooling whereas rFF+PMA improves little, so attention in the encoder matters.
- Meta-clustering: on synthetic 4-Gaussian data ISAB(16)+PMA beats the oracle after one EM step, and on CIFAR-100 (4 random classes, VGG features) it reaches ARI near the oracle while rFF+pooling is far below. SAB(32)+PMA(6) is near the oracle on large sets (n 1000-5000, k = 6).
- Set anomaly detection (CelebA, 8-image sets): SAB+PMA has the best AUROC, with a small gain (0.594 against 0.564).
- Point clouds (ModelNet40): ISAB(16)+PMA is best at 100 points; PMA does not help at 1000 points; at 5000 points ISAB(16)+pooling is the best of this work's models but below Zaheer et al.'s 0.90.
- In the runtime test a SAB could not go beyond 2,000 elements on a Tesla P40.

## Limits

- On large point clouds of 5000 points the authors concede the Set Transformer lost to ISAB(16)+pooling, which they put down to those sets holding enough information already; the Zaheer et al. baseline used more engineering (augmentation, Adamax, a schedule), so the two are not compared on equal terms.
- Parameter counts, GPU hours and per-model compute are missing, and runtime is shown only in a figure.
- The universality proof sets W^O = 0, removing the pairwise interaction terms, and so tells nothing about why attention helps.
- The authors propose that ISAB works as a regulariser (16 inducing points beat a full SAB on clustering) but they do not test this.
- Anomaly error bar type is unspecified and the training schedule ("1,000 iterations" with exponential decay) is unclear; the supplement has unresolved references.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Perceiver IO Latent Bottleneck Attention]] — related (the Perceiver IO paper lists inducing points and seed vectors as related)
- [[Efficient Attention Approximations]] — related
