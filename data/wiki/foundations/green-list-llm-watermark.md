---
title: Green-List LLM Watermark
tags: [foundations, concept]
summary: "Kirchenbauer et al.'s watermark adds a bias to a pseudo-random green subset of tokens at each sampling step and detects it with a z-test on the green-token count, without model access; on OPT-1.3B it flagged 98.4% of generations at z=4 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-kirchenbauer-2023-watermark-large-language-models-2301-10226.md
---

# Green-List LLM Watermark

Kirchenbauer, Geiping, Wen et al. (arXiv 2301.10226, v4 May 2024) ask whether a watermark can be added to LLM output while it is generated, with no retraining, such that even a short span yields a rigorous p-value and the checker needs no model access. They hypothesise that gently favouring a pseudo-random green subset of tokens is detectable at negligible quality cost, with sensitivity set by how much entropy the text has.

## Mechanism

Hashing the preceding token seeds a PRNG that partitions the vocabulary into a green list (a gamma fraction) and a red list, anew at every step. In the soft variant delta is added to green-token logits before sampling. A detector counts green tokens |s|_G among T tokens and runs a one-proportion z-test: the z-score is the green count minus gamma times T, divided by the square root of T times gamma times (1 - gamma). Further contributions are a private-watermarking algorithm, a multi-key variant, a sensitivity bound based on spike entropy (Theorem 4.2) and a perplexity bound (Theorem 4.3). Spike entropy weights each token probability p_k by 1/(1 + z p_k) and sums over k.

## Results (self-reported)

Unless a line says otherwise, the model is OPT-1.3B, prompts are from C4 realnewslike, length is T=200 and each row has roughly 500 generations.

- With gamma=0.5 and delta=2.0 the soft mark is found in 98.4% of multinomial-sampled outputs at z=4 (507 generations) and in 99.6% of 4-way beam-search outputs.
- Dropping to delta=1.0 (gamma=0.5, multinomial, 506 generations) leaves TPR at 0.767 for z=4 and 0.504 for z=5.
- Theory puts the one-sided false-positive rate at z=4 near 3e-5, and no run produced a false positive.
- For gamma=0.5, delta=2 and mean spike entropy 0.807, Theorem 4.2 lower-bounds green tokens at 142.2 while the observed mean was 159.5.
- Under multinomial sampling, gamma=0.1 (a small green list) sits on the pareto front trading z-score against perplexity.
- Using 8-way beam search with gamma=0.25 and delta=2, the average z passes 5 inside 35 tokens, at very little perplexity cost.
- Attack with T5-Large span replacement, 500 sequences of T=200, multinomial, gamma=0.5 and delta=2.0: at budget 0.1 AUC drops by 0.01; at budget 0.3 perplexity triples. Table 8 (487 generations) shows multinomial TPR at z=4 sliding from 0.984 to 0.353 at eps=0.3 and to 0.039 at eps=0.7, while beam search keeps 0.299 there.
- A worked example with a hard red list at gamma=0.5: z=4 corresponds to a one-sided p near 3e-5 and 16 tokens suffice; an adversary has to alter about a quarter of the tokens or more to scrub a 1000-token text.
- On TriviaQA (greedy zero-shot, 50,000 validation questions, gamma=0.5, delta=2) flan-ul2 exact match goes from 0.374 to 0.336; both FLAN-UL2 and BLOOMZ lose under 4 points.
- The authors claim that memorized or templated, low-entropy text defeats reliable detection (shown by the Table 1 failure cases).

## Limits

- The headline experiments use OPT-1.3B, with one OPT-6.7B figure, and no large instruction-tuned chat model.
- The extraction notes: each setting was run once on about 500 samples, with no confidence intervals.
- The mark sits in the surface text alone, so an essay newly composed from an LM-written outline carries none (Appendix B).
- Memorized or low-entropy passages cannot be marked, which is the main cause of misses.
- Emoji, generative and high-budget paraphrase attacks can beat it; the authors propose instruction tuning as a counter.
- The TriviaQA check is called a worst case by the authors and is not a deployment setting.
- The theory treats the red list as uniformly random, unlike the seeded PRNG used in practice.
- The Aaronson/OpenAI approach is not compared, as its details were not available.

## See Also
- [[DetectGPT]] — alternative-to (detects generated text without controlling the generator)
- [[GLTR]] — alternative-to (statistical detection without a mark)
- [[Min-K% Prob Pretraining-Data Detection]] — related (another detector built on token probabilities)
