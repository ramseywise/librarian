---
title: NLI Annotation Artifacts and Hard/Easy Splits
tags: [eval, datasets-and-contamination, benchmark]
summary: "A classifier that sees only the hypothesis predicts SNLI labels at 67.0% and MultiNLI at 53.9% matched (self-reported); splitting the test sets by whether it is right gives Hard and Easy subsets on which NLI models drop sharply."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-gururangan-2018-annotation-artifacts-natural-language-inference.md
---

# NLI Annotation Artifacts and Hard/Easy Splits

Gururangan and colleagues (2018) ask whether the way SNLI and MultiNLI were crowdsourced leaves clues in the hypothesis alone, which would inflate reported NLI accuracy. They suppose workers fall back on writing heuristics. Numbers are the authors' own (self-reported).

## Method

A fastText model sees only the hypothesis and predicts the label. PMI between words and classes, plus sentence length, describe the cues. Each test set is divided into Easy (the hypothesis-only model gets it right) and Hard (it gets it wrong). DAM, ESIM and DIIN are retrained and scored on the full, Hard and Easy versions. The Hard SNLI and MultiNLI sets are released.

## Results

- The hypothesis-only model scores 67.0% on SNLI test (majority class 34.3%), 53.9% on MultiNLI matched (35.4%) and 52.3% on MultiNLI mismatched (35.2%).
- Retrained models score lower on Hard. SNLI: DIIN goes 86.5 full, 72.7 Hard, 93.4 Easy; DAM 84.7 down to 69.4; ESIM 85.8 down to 71.3. MultiNLI matched (DIIN trained only on MultiNLI): DIIN 77.0 down to 64.1, DAM 72.0 to 55.8, ESIM 74.1 to 59.3.
- Cue statistics: a neutral SNLI hypothesis has a median length of 9 tokens, while 60% of entailed ones have no more than 7. Bag-of-words containment in the premise holds for 8.8% of entailed hypotheses but 0.2% of neutral and contradiction ones. "No" occurs in 7.6%, and "never" in 5.0%, of MultiNLI contradiction training sentences.
- Discarding Easy items may not leave a clean set. In early experiments (no numbers given), removing contradictions containing "no" pushed that word into the other classes, creating a fresh artifact.

## Limits

- Only fastText defines Hard and Easy; the authors say other classifiers behave alike but show nothing.
- Models were retrained as shipped, with no hyperparameters, seeds or variance given, and dataset sizes are not stated.
- Because one model's mistakes define Hard, new artifacts may sit in it; filtering the training data is left for later.
- The cues are many and individually rare, and the analysis is shallow and statistical. The authors stress that artifacts do not make examples incorrect; the trouble is a lopsided sample.

## See Also
- [[HANS NLI Heuristics Evaluation Set]] — related (constructed examples that NLI models also fail)
- [[Pretrained Transformer OOD Robustness Benchmark]] — related (cites spurious cues as an explanation for OOD brittleness)
- [[VLM Benchmark Shortcuts]] — related (shortcuts in vision-language benchmarks)
