---
title: RuleTaker
tags: [foundations, concept]
summary: "Clark et al. fine-tune RoBERTa-large on synthetic natural-language facts and rules and report it answers true/false questions at about 99% on its own test data, generalises to deeper proofs, and transfers to paraphrased rules, while stopping short of proving it reasons (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-clark-2020-transformers-as-soft-reasoners-over.md
---

# RuleTaker

Clark, Tafjord and Richardson (IJCAI 2020) ask whether transformers can learn to reason, or imitate reasoning, over facts and rules written as English sentences, even at proof depths absent from training. They call the trained models **RuleTaker** and describe them as limited soft theorem provers.

## Method

Synthetic rulebases of facts and conjunctive rules, under closed-world semantics with negation as failure, are generated as logic, forward-chained so each true/false question gets a label, then rendered as templated English. RoBERTa-large, pre-fine-tuned on RACE, is fine-tuned as a binary classifier. Tests cover held-out proof depths and perturbed theories, plus two rulebases written by hand and crowdsourced paraphrases of the rules. A **critical sentence** is one that every proof of a fact uses, so removing it can change the fact's truth.

## Results

All numbers are the paper's own (self-reported); the extraction records only prose-quoted numbers, not the tables.

- The abstract-level claims: about 99% accuracy on the synthetic data, generalisation to greater depths, 98% on paraphrased rules when trained on them, and 94% F1 on identifying needed facts (the paper's intro figure).
- A model trained up to depth 3 carries over to depth 5; trained to depth 2 it reaches 71.1% on unseen depth 3.
- Deleting a critical sentence makes the model flip a true prediction to false in just 81% of cases, where a formal prover would manage 100%: accuracy on those theories falls to 81.2% against 99.4% on the originals (no-negation variants, 20,746 critical-removal probes among 113,978).
- Predicting critical sentences reaches macro F1 92.4.
- With no training on them, the strongest model (MMax) reaches 66.6% on the crowdsourced-paraphrase rules; training on depth-3 data plus the paraphrase set gives 98.8%.
- Swapping every word for a random one lowers accuracy from 99.3% to 83.3%, which the extraction reads as pretrained knowledge mattering.
- A depth-0 model falls below chance beyond depth 2 because it predicts false for anything not given. On one hand-written rulebase (Electricity4) models trained deeper score a little below the depth-1 model.

## Limits

- Small theories (under 20 facts and 10 rules), small domains and at most one quantified variable per rule; templated language, with the paraphrase test only a first step.
- The authors leave open whether the transformer reasons or emulates input-output behaviour.
- Closed-world semantics clash with natural language inference intuitions; the perturbation analysis excludes negation.
- Training hyperparameters, compute and seeds are not stated, and the work predates few-shot prompting of language models.

## See Also
- [[Selection-Inference]] — related (prompted alternative on rule-based deduction tasks)
- [[Chain-of-Thought Prompting]] — related
- [[ReClor Logical Reasoning Reading Comprehension]] — related
- [[Compositionality Gap]] — related
