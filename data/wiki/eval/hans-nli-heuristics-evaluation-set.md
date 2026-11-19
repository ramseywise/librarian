---
title: HANS NLI Heuristics Evaluation Set
tags: [eval, datasets-and-contamination, benchmark]
summary: "HANS is a template-built NLI test set in which three syntactic heuristics (lexical overlap, subsequence, constituent) give the wrong answer; MNLI-trained models, BERT included, score below 10% on most non-entailed cases (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mccoy-2019-right-wrong-reasons.md
---

# HANS NLI Heuristics Evaluation Set

McCoy, Pavlick and Linzen (2019) ask whether models trained on MNLI pick up shaky syntactic shortcuts that flatter their test accuracy. They suppose the training data backs the shortcuts and the input representations allow them. Numbers are the authors' own (self-reported).

## The heuristics

- **Lexical overlap:** treat a premise as entailing any hypothesis made only of its words.
- **Subsequence:** treat a premise as entailing every contiguous piece of itself.
- **Constituent:** treat a premise as entailing each complete subtree of its parse.

## Construction

HANS has 30 subcases, with 1,000 examples per template and, for each heuristic, five templates that support it and five that contradict it. DA, ESIM, SPINN and BERT (bert-base-uncased) were trained on MNLI and evaluated on it.

## Results

- On most non-entailed HANS cases, all four models get under 10%, where chance is 50%. BERT's score on subject/object swap is zero.
- MNLI's training set has 2,158 cases favouring lexical overlap (subsequence and constituent included) against 261 opposing it, and 133 of those 261 have negation in the premise only.
- Humans: 95 retained MTurk workers averaged 76% on a HANS subset (114 categories, 20 examples each, 5 judgments apiece), compared with 92% on MNLI items. Three linguists averaged 97%. Mistakes were spread evenly over labels.
- Retraining with 30,000 added HANS-like examples gives very good HANS results, except DA on subcases a bag of words cannot handle; no HANS items were used. BERT's MNLI test accuracy barely moves, while DA's drops.
- Generalisation is partial. With a merged non-entailment label BERT still fails constituent non-entailment, and when entailed passives are held out it scores 0% on them.

## Limits

- It does not separate architecture from training data as the cause, and BERT had much more pretraining text.
- Templates and a narrow vocabulary restrict the sentence types covered.
- The augmentation study is a first exploration: the number of contradicting examples needed is open and withheld-subcase transfer is incomplete.
- Only bert-base-uncased, with no hyperparameters, seeds or variance, and only models from 2019.

## See Also
- [[NLI Annotation Artifacts and Hard/Easy Splits]] — related (hypothesis-only bias in the training data)
- [[Dynabench]] — related (another way to build tests that models fail)
- [[Edge Probing and Layer Localisation in BERT]] — related (probes of what BERT encodes)
