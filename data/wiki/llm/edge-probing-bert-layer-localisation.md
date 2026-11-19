---
title: Edge Probing and Layer Localisation in BERT
tags: [llm, interpretability-and-safety, concept]
summary: "Tenney et al. train small probes on frozen BERT layers for eight labelling tasks and find syntax is localised in lower layers while semantic information is spread out, in an order that follows the classical NLP pipeline (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-tenney-2019-bert-rediscovers-classical-nlp-pipeline.md
---

# Edge Probing and Layer Localisation in BERT

Tenney and colleagues (2019) ask where in BERT's layers each stage of the traditional NLP pipeline is represented. The working hypothesis (syntax lower, semantics higher) is inferred by the extraction, not stated by the authors. Every finding here is the authors' own (self-reported).

## Mechanism

- **Edge probing** puts structured-prediction tasks in a single format: a probe gets one or two token spans, sees only the contextual vectors inside them, and predicts a label. Eight labelling tasks are used, drawing on OntoNotes 5.0, the English Web Treebank, SemEval-2010 Task 8 and semantic proto-role labelling.
- **Scalar mixing**, borrowed from ELMo, learns a softmax-weighted sum of all encoder layers together with the probe. A heavily weighted layer is read as more useful for the task, and the weights' centre of gravity places the task in depth.
- **Cumulative scoring** trains one probe per depth, each seeing that layer plus every earlier one. The F1 gained by adding a layer is its differential score, and an expected layer is computed from these gains.

## Findings

- On BERT-large (24 layers), both measures put part-of-speech first, followed by constituents, dependencies, semantic roles and coreference.
- For many tasks the biggest differential gains come within the first few layers, yet the learned mixing weights sit much deeper.
- Syntactic tasks are localised to a few layers. Relation and proto-role tasks are spread almost evenly through the network, and entity labelling is settled early but has a long tail.
- BERT-base (12 layers) shows the same order, each task landing at similar positions relative to the top of the model.
- On the OntoNotes dev set, a layer-0 probe on BERT-base already gets most POS tags right from non-contextual embeddings.
- Per-sentence traces of cumulative probes (BERT-base, hand-picked OntoNotes dev sentences) show the model resolving decisions out of pipeline order; one example changes an entity from GPE to ORG once the semantic role of Toronto is settled. This part is qualitative.
- An appendix covers ELMo: for all tasks its first LSTM layer carries the most information, and coreference barely concentrates anywhere.

## Limits

- The study is exploratory and covers one encoder family (ELMo weights appear only in an appendix); the authors want further work on whether the trends generalise.
- Probing only inspects. A pattern the probe misses may still exist, and one it finds says nothing about whether the model uses it; the authors ask for behavioural studies.
- Whether semantics is poorly localised because of BERT or because semantics is hard to localise is left open.
- Final-layer drops are put down by the authors to possibly distracting new features and probe overfitting.
- The expected layer is only a pseudo-expectation, because F1 is not an average over examples.
- Absolute F1, dataset sizes and probe hyperparameters appear only in figures, and sentences for the traces were chosen heuristically.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Attention Head Roles, Pruning and Faithfulness]] — related (head-level analysis of the same encoder)
- [[Contrast-Consistent Search]] — related (another probe on frozen hidden states)
