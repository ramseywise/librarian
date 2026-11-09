---
title: Self-Supervised LLM Evaluation by Text Transformations
tags: [eval, llm, pattern]
summary: "Score a model's sensitivity or invariance to a simple transformation of any text corpus (negation, a toxic trigger, shuffling, splitting tokens) and compare against labelled benchmarks; on Wikipedia sentences the scores tracked TriviaQA and LAMBADA closely in scatter plots, with no correlation coefficients (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-jain-2023-bring-your-own-data-self.md
---

# Self-Supervised LLM Evaluation by Text Transformations

Jain and colleagues (2023 preprint) ask whether LLM behaviour can be measured without labels by checking how outputs change under a simple transformation of text. The score is an aggregate of a comparison between the model's response to the original text and to the transformed text, over all pairs in a corpus; the comparison can use perplexity, the next-token distribution (Jensen-Shannon divergence) or the generated text itself. Nothing is trained. The metrics are framed as invariances and sensitivities that can be probed by changing the input and watching only the model under test.

Five case studies (self-reported), run on 1000 Wikipedia sentences each over roughly 15 to 25 open and API models:

- **Knowledge via negation**: the sensitivity score tracked TriviaQA accuracy closely; the share of inputs where perplexity falls after negation correlated negatively with it.
- **Toxicity (F-bomb)**: a word-list trigger appended to a sentence; the score correlated closely with Perspective API toxic fractions (toxic meaning a score of at least 0.5).
- **Long-range context**: rose with LAMBADA accuracy, and larger models were more sensitive to context changes.
- **Word order (word salad)** and **tokenization (broken token)**: tokenization sensitivity fell with training compute, with OPT trained on 180B tokens a strong outlier.

Other results (all self-reported): instruction tuning on average raised negation, long-range context and word-order sensitivity, did not reliably change tokenization sensitivity and left toxicity unchanged on average; most models take under 30 minutes for 1000 examples on one RTX A4000; human inspection of 100 negation samples found grammatical counterfactuals. Cohere command seldom altered its answer when the sentence was negated, whereas text-ada-001 almost always did, a difference TriviaQA does not show. The authors argue, without testing, that scores on fresh text such as news avoid memorization and contamination.

## Limits

- Agreement with benchmarks is shown only as scatter plots, with no correlation coefficients or significance tests.
- Only Wikipedia text was used; applying it to a live production stream is a proposal that was not run.
- Negation needs mostly true sentences, toxicity covers only explicit profanity from a word list, tokenization only character splits, and word order assumes next-token divergence is a proxy.
- Low sensitivity can simply reflect low entropy (LLaMA) or come as a side effect of other behaviour (text-ada-001); scores for very small models carry no meaning.
- Memorization effects are not studied; the models date from 2023, with open ones up to 7B parameters plus OpenAI and Cohere API models since retired or changed.

## See Also
- [[Paired Input-Perturbation Eval]] — related (another perturb-and-compare design)
- [[Eval Contamination Defenses]] — related (fresh text as a contamination answer)
- [[HELM Holistic Evaluation]] — related (the multi-metric benchmark this complements)
