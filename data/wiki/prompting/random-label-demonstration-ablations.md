---
title: Random-Label Demonstration Ablations
tags: [prompting, concept]
summary: "Min et al. replace gold labels in few-shot demonstrations with random ones and find a 0-5% absolute drop on most models; the label space, the input distribution and the pair format carry most of the demonstration gain (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-min-2022-rethinking-role-demonstrations.md
---

# Random-Label Demonstration Ablations

Min et al. (EMNLP 2022) ask which parts of in-context demonstrations drive end-task performance, and whether the ground-truth input-label mapping matters. The study is inference only. Setup: k=16 demonstrations with a minimal template, 12 model variants (6 LMs, each with direct and channel inference), 26 datasets spanning classification and multi-choice (fairseq 13B and GPT-3 used 6 datasets and 3 seeds); scores are Macro-F1 for classification and accuracy for multi-choice. **Direct** models score P(y|x), while **channel** models score the input given the label.

## Findings (self-reported)

- Random labels in place of gold ones drop performance only 0-5% absolute on nearly all models; the drop is smaller on multi-choice than on classification, and MetaICL shows almost none.
- Always-incorrect labels keep most of the gain for MetaICL and for GPT-J on multi-choice; GPT-J on classification drops nearly 10% but stays above no demonstrations.
- The gold-versus-random gap stays small across k, and growing k stops helping past k=8 (channel MetaICL on classification and direct GPT-J on multi-choice, tried at k of 0, 4, 8, 16 and 32).
- **Input distribution**: demonstrations whose inputs are out-of-distribution (CC-News sentences) cut performance by 3-16% absolute, except direct MetaICL.
- **Label space**: direct models lose 5-16% absolute when the labels are random English words rather than random picks from the real label set; channel models lose little.
- With random corpus sentences paired with labels from the label set, direct MetaICL keeps 95% of the gain on classification and 82% on multi-choice. Channel models keep 75-87% by pairing each unlabelled training input with a random English word.
- **Format**: dropping it (inputs with no labels, or labels with no inputs) leaves performance near, or below, having no demonstrations. Drawing the random labels from the true label distribution shrinks the gap further for channel MetaICL and channel GPT-J.
- Meta-training with an in-context objective makes the model lean more on simple aspects such as format.

The largest per-dataset gap is nearly 14% absolute (financial_phrasebank, GPT-J).

## Limits

- The study covers classification and multi-choice with natural-language inputs; the authors concede that generation was not tested.
- Ground-truth labels may matter more on synthetic tasks; macro averages hide outlier datasets (financial_phrasebank, some hate-speech sets).
- Later work, as the extraction notes: negated labels sharply lower classification performance, and random rationales hurt chain-of-thought a great deal.
- Models run 774M to 175B from 2021; no instruction-tuned models, and carry-over is only hypothesised. GPT-3 is assumed to be 175B.
- Several direct models, namely GPT-2, GPT-J and fairseq 6.7B, perform near chance on many classification sets, and channel fairseq 13B with no demonstrations does better than with gold demonstrations.
- GPT-3 and fairseq 13B ran on only 6 datasets with 3 seeds, and the temperature, token cap and seed values are not given.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Flipped-Label In-Context Learning]] — related (finds the mapping is learned at larger scale; the authors say the findings agree up to davinci)
- [[Prompt Programming and Task Location]] — related (the task-location view that these results support)
- [[Irrelevant and Misleading Prompt Templates]] — related (the same indifference to semantics, for templates)
- [[In-Context Explanations for Few-Shot Examples]] — related (its other-item control probes the same question)
