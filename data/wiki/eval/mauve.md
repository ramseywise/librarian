---
title: MAUVE
tags: [eval, concept]
summary: "MAUVE scores the gap between model text and human text by quantizing embeddings of both and taking the area under a divergence curve; the paper reports it ranks decoders and model sizes as expected where generation perplexity does not (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-pillutla-2021-mauve.md
---

# MAUVE

Pillutla and colleagues (NeurIPS 2021) ask how to score automatically how far a text generator's distribution sits from that of human text, so that a generator is penalised both for degenerate output and for missing the range of human text. Their hypothesis is that summarising the whole divergence curve, computed on quantized embeddings of model text and human text, ranks decoders, model sizes and lengths as people expect and tracks human judgment better than single-number metrics.

## Mechanism

1. Embed N human texts and N' model texts using GPT-2 large.
2. Jointly quantize the embeddings with k-means (k of 500 after PCA) and build a histogram for each side, giving two discrete distributions P (human) and Q (model) on shared clusters.
3. Mix the two distributions as R-lambda = lambda P + (1 - lambda) Q, and plot exp(-c KL(Q|R-lambda)) against exp(-c KL(P|R-lambda)) with c = 5. This is the divergence curve.
4. MAUVE is the area under that curve.

The two error types it separates: type I, where the model puts high mass on text unlikely under human text; type II, where the model cannot produce text that is plausible under human text.

## Results

Self-reported by the paper, on the setups named.

- Web text, GPT-2 xl, 5,000 generations: greedy decoding scores 0.016, ancestral sampling 0.882, nucleus sampling 0.940. Generation perplexity, by contrast, prefers degenerate greedy text over ancestral sampling, and an adversarial decoder tuned for perplexity gets near-perfect perplexity but low MAUVE.
- With nucleus sampling, MAUVE increases with GPT-2 size, from 0.878 (small) through 0.915 (medium) and 0.936 (large) to 0.940 (xl).
- Correlation with human-like Bradley-Terry scores is far above generation perplexity on web text (GPT-2 small through xl, each with ancestral and nucleus sampling, which makes eight settings; completions capped at 256 tokens; 90 ratings per pair). MAUVE also correlates with discriminator accuracy on news (Grover base, large, mega) and on story continuation (fine-tuned GPT-2 medium).
- Robustness: rankings are close with RoBERTa-large or GPT-2-large features, and across k from 100 to 5000 and alternative quantizers (DRMM, lattice).
- In the paper's runs MAUVE drops as generation length grows, for every model (max length 200 to 1000), while Frechet distance rises and generation perplexity is non-monotonic.
- Cost: about 1 to 3 minutes on one CPU core for 5,000 generations with cached embeddings.

## Limits

- Validation covers three English domains and only GPT-2 and Grover; closed-ended tasks such as summarization and translation are deferred to future work.
- The human study is limited to web text, crowd workers, eight settings and completions cut at 256 tokens.
- On some pairs MAUVE disagrees with humans (it ranks GPT-2 medium with nucleus sampling above large and xl with pure sampling) and on Grover large (ancestral above nucleus).
- Absolute values depend on k, c, the embedding model and the sample size (small samples inflate values); only the rankings are stable.
- Embedding-model biases are not studied. The extraction adds its own reading: it is a corpus-level score, so it requires thousands of generations, cannot grade a single answer and verifies no facts.

## See Also
- [[Text Metrics Beyond N-gram Overlap]] — related (other embedding-based text metrics)
- [[Perplexity and Bits-per-Byte]] — alternative-to (generation perplexity is the baseline MAUVE is compared with)
- [[ALCE Citation Benchmark]] — related (uses MAUVE as its fluency metric)
