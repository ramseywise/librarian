---
title: Efficient Attention Approximations
tags: [infra, comparison]
summary: "Three 2020-2021 routes to sub-quadratic attention, random-feature kernels (Performer), global plus window plus random sparsity (BigBird) and learned cluster routing (Routing Transformer), with their reported results and limits, plus the Tay et al. survey taxonomy."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-choromanski-2020-rethinking-attention-performers.md
  - data/raw/papers/2026-11-08-zaheer-2020-big-bird.md
  - data/raw/papers/2026-11-08-roy-2021-efficient-content-based-sparse-attention.md
  - data/raw/papers/2026-11-08-tay-2022-efficient-transformers.md
---

# Efficient Attention Approximations

Three papers cut the quadratic cost of attention in different ways. The extraction notes that all three pre-date fused exact-attention kernels, which changed the speed trade-off.

## Performer (FAVOR+)

Choromanski et al. estimate softmax attention with positive orthogonal random features: queries and keys pass through random feature maps and the product is computed right to left, which gives time O(Lrd) and space O(Lr + Ld + rd) for r random features, where full attention needs O(L^2 d) time and O(L^2 + Ld) space (analysis, not measurement). Their theory says positive features keep the estimate's error small as the softmax-kernel value goes to zero, where trigonometric features do not. Results (self-reported, single runs):

- Protein data (TrEMBL, 36 layers, L = 1024): the softmax Performer matches the exact Transformer on bidirectional test accuracy; a generalized-ReLU variant beats it. On out-of-distribution families the Performer is slightly worse.
- Concatenated proteins at L = 8192: the memory-limited Transformer plateaus near 19%, the full-size Performer reaches about 24%.
- On ImageNet64, after 100K steps, the ReLU (3.67), softmax (3.69) and SMREG (3.67) variants give nearly the same bits per dimension.
- Trigonometric features gave unstable training and NaNs on PG-19; separately, a Linear Transformer (elu+1) hit exploding gradients in the ProGen 36-layer TrEMBL protein setting, not on PG-19.

## BigBird

Zaheer et al. combine three parts per query: g global tokens, a window of w neighbouring tokens and r random keys, all evaluated blockwise so they run as dense tensor operations. Models warm-start from RoBERTa (or Pegasus) and pretrain at 4096 tokens. Results (self-reported):

- Without global tokens, random plus window attention at 512 tokens does worse than BERT-base, which motivates adding them.
- BigBird-ETC reaches 84.5 F1 on the TriviaQA full test set; on BigPatent, re-evaluated Pegasus gets 52.25 ROUGE-1 and BigBird-Pegasus large 60.64.
- On DNA, promoter prediction F1 is 99.9 against 95.6 for DeePromoter, and masked-language-model bits per character at 4096 tokens is 1.12 against 1.23 for BERT at 512.
- The paper argues the pattern is a universal approximator and Turing complete, and, under the Orthogonal Vectors Conjecture, that some tasks need many layers with any sparse attention.

## Routing Transformer

Roy et al. cluster queries and keys with online spherical k-means; each centroid keeps the tokens closest to it and attention is dense inside a cluster, costing O(n^1.5 d) when k = sqrt(n) (claimed for balanced clusters). Results (self-reported): Wikitext-103 test perplexity 15.8 against 18.3 for Transformer-XL; PG-19 33.2 against 33.6 for the Compressive Transformer; ImageNet-64 3.425 bits per dimension against 3.437 for the Sparse Transformer. A strong baseline is local attention at larger scale (PG-19: 39.3 for a 24-layer local model against 36.3 for a 36-layer Transformer-XL). A routing-only model is much worse than a mix with local heads (CIFAR-10: 3.400 bits per dimension).

## Taxonomy from the Tay et al. survey

Tay et al. group efficient Transformers by their central technique; per the extraction, Table 1 lists the complexity, decoder support and class of about 30 models:

- **Fixed patterns:** sparsify the attention matrix with predefined local windows and strided blocks. The survey extraction does not assign classes to individual models; this page's own reading is that [[Sparse Transformer Factorized Attention]] and [[Longformer Sliding-Window and Global Attention]] (dilated window plus global tokens) fit here.
- **Combination of patterns**, and **learnable patterns** that assign tokens to buckets or clusters (Reformer's LSH attention at O(N log N); the Routing Transformer above).
- **Neural memory:** a learnable side memory such as global tokens or inducing points, for which the survey names inducing points as an example; see [[Set Transformer Induced Set Attention]].
- **Low-rank methods** (Linformer projects length N to k) and **kernels**, as in [[Linear Attention (Transformers Are RNNs)]] and the Performer above.
- **Recurrence** between blocks, as in [[Transformer-XL Segment Recurrence]]; and, separately, the memory-compressed attention of [[WikiSum and Memory-Compressed Attention]] (cost O(n*n/k) for a strided convolution of kernel and stride k, with blockwise local attention O(b*n)); and **sparse models** (mixture of experts) that activate a subset of parameters.

The survey's claims and reported figures (it ran no experiments):

- Self-attention takes quadratic time and memory, with the QK^T product by itself being N^2. The survey says feed-forward layers account for about half of a block's compute (no measurement given), so speeding up attention alone leaves much of the cost in place.
- Figures the survey relays from the papers it cites: block pruning yields a 2.4x faster Transformer with small loss on language tasks (Lagunas et al. 2021), and linear Transformers raise inference speed by up to three orders of magnitude with little loss (Katharopoulos et al. 2020).
- As of December 2021 (citing Xiong et al. 2021a), linear-attention variants have trouble competing on standard benchmarks and none has become the default; a well-built local attention is a hard baseline on long-context tasks.
- In parallel teacher-forced training, causal kernel attention may run several times slower than the vanilla Transformer, since it needs a left-to-right scan. Lower complexity can still be slower in practice, and linear models bring no gain at short lengths.
- The models cannot be compared directly, because every paper picks benchmarks and model sizes independently; Long Range Arena covered 10 variants on encoder-only tasks and has no causal tasks.
- Practices the survey gives: separate memory complexity from real throughput before adopting a variant; treat local attention as the strong baseline; if lengths vary, sequential processing may suffice (citing Rabe and Staats 2021); check causal-masking support before autoregressive use; compare encoder-only models only on encoder-only benchmarks.

## Limits

- Performer: the generalized-ReLU gain is shown on protein data only; reusing pretrained Transformer weights needs fine-tuning; orthogonal features require m no larger than d; no variance for most results; the speed benchmark is on V100 in Jax with no comparison to fused exact kernels.
- BigBird: the 8x longer-sequence claim has no memory or speed measurement; the QA headline results come from ETC without random attention; promoter F1 is inflated because negative examples were built in a way that overlaps with pretraining; sparse attention is on the encoder only; no latency or kernel benchmark.
- Tay et al. survey: it runs no experiments and gives no head-to-head numbers; comparing models is hard because papers choose their own benchmarks and sizes and at times mix in pretraining; complexity is not the same as wall-clock speed; it covers work up to early 2022, so it predates IO-aware exact attention of the FlashAttention kind, and it says nothing of today's long-context LLMs.
- Routing Transformer: on TPU wall-clock time is worse than local attention (PG-19 about 1.7x slower); per the extraction notes, the text reports 3.425 and 3.437 but Table 4 prints the rounded 3.43 and 3.44; full attention is compared only on short CIFAR-10 sequences; no variance; no decode-time measurement.

## See Also

- [[Self-Attention Mechanism]] — prerequisite-for
- [[Sparse Transformer Factorized Attention]] — extends
- [[Longformer Sliding-Window and Global Attention]] — extends
- [[Linear Attention (Transformers Are RNNs)]] — extends
- [[FlashAttention and FlashAttention-2]] — alternative-to
- [[MiniMax Sparse Attention]] — related
- [[Star Attention]] — related
- [[RWKV Linear-Time Recurrent Language Model]] — related
