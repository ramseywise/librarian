---
title: Deduplicating Training Data (ExactSubstr and NearDup)
tags: [llm, pretraining-and-data, pattern]
summary: "Lee et al. (ACL 2022) remove duplicated text from C4, RealNews, LM1B and Wiki-40B with a suffix-array exact-substring filter and a MinHash near-duplicate filter; models trained on the deduplicated C4 emit about 10x less memorised text without worse perplexity (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-lee-2022-deduplicating-training-data-makes-language.md
---

# Deduplicating Training Data (ExactSubstr and NearDup)

Lee, Ippolito, Nystrom et al. (ACL 2022) ask how much duplicated text common language-model training sets hold, and whether removing it changes perplexity, memorisation and leakage between train and test splits. Their working hypothesis is that removing duplicates cuts memorised generations and train-test leakage while leaving perplexity intact. They apply two tools to C4, RealNews, LM1B and Wiki-40B (English datasets), then train T5-codebase decoder-only models of 1.5B (XL) and 110M (base) parameters on original and deduplicated C4.

## The two filters

- **ExactSubstr** removes any substring of at least k=50 tokens that more than one example shares verbatim. A suffix array over BPE tokens finds the matches. On a 350GB C4 the array takes under 12 hours wall-clock (about 1000 CPU-hours) on one 96-core, 768GB VM, and the array is 1.5TB.
- **NearDup** matches whole documents approximately with MinHash (5-grams, signature size 9,000, b=20, r=450), then keeps only pairs whose edit similarity is above 0.8.
- The two use different thresholds, so the comparison between them depends on those choices. Of the C4 examples NearDup removes, 77% have a verbatim 50-token match that ExactSubstr also finds.

## How much duplication exists (self-reported)

- NearDup finds 3.04% of C4 training examples to be near-duplicates, and 13.63% of RealNews.
- ExactSubstr marks 7.18% of C4 training tokens as part of an exact duplicated 50-token substring (19.4% for RealNews).
- In C4, 4.60% of validation examples have a near-duplicate somewhere in the training split.
- A single sentence of 61 words turns up 61,036 times in C4 training data, and 61 times in its validation data.
- Token counts for C4 (50k BPE vocabulary): 177.3B untouched, 173.7B after NearDup, 165.4B after ExactSubstr. RealNews shrinks most (24.7B down to 20.1B with ExactSubstr), and the abstract states up to 19%.

## Effect on memorisation and perplexity (self-reported)

- In unprompted generations from the XL model trained on original C4, more than 1% of tokens sit inside memorised 50-token substrings; models trained on deduplicated data emit roughly a tenth as much. At the final checkpoint after about 2 epochs, with top-k 50 sampling and no prompt, the figures are 1.571% for the original, 0.264% for NearDup and 0.168% for ExactSubstr.
- Prompted with the first 32 tokens of training examples that have near-duplicates, the XL model trained on original C4 reproduces the true continuation over 40% of the time.
- Perplexity is not hurt and in some cases falls by up to 10%. On Wiki-40B, ExactSubstr brings the XL model's perplexity down by nearly 3 points, whereas base-model seeds vary by about 1 point.
- On validation examples that also occur in training, the deduplicated models score worse perplexity.
- Training on deduplicated C4 shortens a roughly 131-hour two-epoch run on 128 TPU v3 cores by about 5 hours. Energy is estimated at 5.86 MWh for the original and ExactSubstr runs and 5.63 MWh for NearDup, using the per-core estimates of Patterson et al. and a Taiwan datacenter assumption.

## Leakage in released models

- On LM1B every XL model scores perplexity under 35, which beats the 42.16 reported for the 1.5B GPT-2.
- Transformer-XL's LM1B validation perplexity roughly halves on examples with near-duplicates in training (10.11 against 23.58 for unique ones).
- Of the tokens in 25k official GROVER-Mega outputs, 1.38% belong to verbatim 50-token matches with RealNews; for about 200k GPT-Neo 1.3B outputs, over 5% of tokens match the Pile in 50-token runs.

## Limits

- Only perplexity and memorisation are measured; there is no downstream-task evaluation.
- The paper does not separate harmful from innocuous memorisation, runs no privacy study, and says deduplication is not enough to remove private data.
- It does not study negative consequences of deduplication, such as tasks that need memorisation or loss of attribution.
- Deduplicated models still copy the true continuation more often from duplicated prompts, so the authors say stricter deduplication may be needed.
- English datasets only; the XL models were trained once with no seeds, the base models with 3 seeds.
- Size reduction is stated two ways: the abstract gives a reduction of up to 19% (RealNews tokens), while Appendix D gives 3.9% for the C4 runs.

## See Also
- [[Extracting Training Data from Language Models]] — prerequisite-for (the GPT-2 extraction result this paper measures against deduplication)
- [[Dolma Open Pretraining Corpus]] — related (applies URL, document and paragraph deduplication in a larger pipeline)
- [[Pretraining Data Age, Quality and Toxicity Ablations]] — related (applies this approximate deduplication to its C4 and Pile variants)
- [[Eval Contamination Defenses]] — related
