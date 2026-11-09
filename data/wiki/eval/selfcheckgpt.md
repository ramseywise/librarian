---
title: SelfCheckGPT
tags: [eval, pattern]
summary: "A black-box hallucination detector that samples the model several times and scores each sentence of the main answer by how far the samples disagree with it; on 238 GPT-3 WikiBio passages the LLM-prompt variant was best on the AUC-PR and passage-correlation measures reported (self-reported), but it detects inconsistency, not falsehood."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-manakul-2023-selfcheckgpt.md
---

# SelfCheckGPT

Manakul, Liusie and Gales (arXiv 2303.08896, 2023) ask whether hallucinations in a black-box model's answer can be found with no external database and no token probabilities, only by checking consistency across stochastically sampled responses. Their hypothesis is that when a model knows a concept its samples agree, and for a hallucinated fact they diverge and contradict each other. "Zero-resource" means no external database is used; "black-box" means only text responses are needed; "grey-box" methods need the output token probabilities.

## Method

A greedy (temperature 0) answer is generated, then N=20 further samples at temperature 1.0. Each sentence of the greedy answer is scored for inconsistency against the samples in one of five ways:

- **BERTScore**, **QA** (MQAG question answering), **n-gram** (an n-gram model) and **NLI** (DeBERTa-v3-large MNLI).
- **Prompt**, an LLM yes/no prompt whose answers are scored Yes 0.0, No 1.0 and N/A 0.5 and averaged over the samples.

The test set is 238 GPT-3 (text-davinci-003) passages about WikiBio concepts, 1,908 sentences, annotated by hand for factuality.

## Results (self-reported)

Setup unless stated: that 238-passage set, N=20, greedy answer at temperature 0.

- The Prompt variant with a GPT-3 judge scored best on AUC-PR for non-factual sentences (random 72.96; the best GPT-3 grey-box baseline, Max(-logp), 87.51), for factual sentences (random 27.04) and for the NonFact* setting (random 29.72), and had the highest passage-level Pearson and Spearman correlation with human judgement. The extraction does not give the variant's own scores.
- The NLI variant came close to Prompt at lower cost. The unigram (max) variant, the cheapest, beat the grey-box baselines on factual-sentence AUC-PR.
- For factual sentences, GPT-3's own token probabilities made a strong grey-box baseline. Probabilities from a proxy model did worse: LLaMA-30B much worse than GPT-3's own, while OPT-30B and GPT-NeoX were near random.
- Giving NLI or Prompt a WikiBio reference paragraph instead of samples improved passage-level Pearson for Prompt, which is retrieval and no longer zero-resource. The n-gram variant collapsed with that reference.
- With only N=4 samples, GPT-3 checking its own text still beat unigram, and ChatGPT as checker was slightly better than GPT-3. Performance rose smoothly with N with diminishing gains, and n-gram needed the most samples to plateau.
- Running Prompt over 1,908 sentences with 20 samples cost about $200 with GPT-3 at $0.020 per 1k tokens, or $20 with ChatGPT.
- Annotation agreement was moderate for three classes and substantial for two (201 doubly annotated sentences).

## Limits

Only 238 passages, mostly about individuals; there are no locations or objects. Labels are per sentence, so a sentence mixing true and false content is a single label, and atomic-fact scoring is left for later. The generator is text-davinci-003 only, and the checkers are dated. The label scheme gives a high base rate (39.9% major-inaccurate, hence the random AUC-PR of 72.96). There are no seeds, confidence intervals or significance tests, so gaps between close variants such as Prompt and NLI are untested. The Prompt variant is best but computationally heavy. Detection is of inconsistency, not falsehood: a model that is consistently wrong would pass.

## See Also
- [[FActScore]] — extends (the atomic-fact follow-up the paper names; scores facts against a knowledge source)
- [[Tool-Augmented Factuality Checking]] — alternative-to (checks claims with external tools instead of the model's own samples)
- [[Lookback Lens]] — alternative-to (a white-box detector of contextual hallucination)
- [[Hidden-State Hallucination Probes]] — alternative-to (white-box, not compared in this paper)
- [[Language Model Self-Knowledge]] — alternative-to (a self-evaluation route from the model's own probabilities)
- [[Self-Consistency]] — related (sampling consistency applied to reasoning answers)
- [[Output Length Confounds Reference Metrics]] — related (a later re-scoring of hallucination detectors with a judge instead of ROUGE)
- [[LLM Hallucination Surveys]] — related (surveyed as a sampling-consistency detector)
