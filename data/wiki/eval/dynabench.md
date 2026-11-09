---
title: Dynabench
tags: [eval, benchmark]
summary: "Dynabench is an open platform where annotators write examples to fool a live target model, other humans validate them, and models are retrained between rounds, so the benchmark moves as models improve; the 2021 paper reports validated error rates of 33-44% on four tasks (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-kiela-2021-dynabench.md
---

# Dynabench

Kiela and colleagues (NAACL 2021) propose replacing static datasets, which saturate, with dynamic collection where humans and state-of-the-art models are both in the loop over several rounds. It is a position paper with a progress report, not a controlled experiment.

## Mechanism

- Annotators use a web platform and try to write examples that make a live target model err; other humans validate each example.
- Collection runs in rounds, and models are retrained between rounds on the new data, so the next round faces a stronger target.
- The **validated model error rate** (vMER) is the count of model errors that humans confirmed, divided by all examples collected.
- Four initial tasks, each seeded by earlier dynamic-data work: natural language inference, question answering, sentiment and hate speech.

## Results (self-reported)

- vMER stays between 33% and 44% across all four tasks in the paper's Table 1; the extraction notes that rates are not comparable across tasks.
- The NLI task holds 170,294 examples over 4 rounds. On ANLI rounds 2 and 3, models that exceed 90% on SNLI and MNLI reached no more than 50%.
- The final-round hate speech target (RoBERTa retrained over 4 rounds) reaches 94% on the external HateCheck suite.
- Cost per validated example, from personal communication with the authors: SNLI cost $0.50, MultiNLI $0.64 and ANLI roughly $1.00.
- For sentiment, editing a real review sentence (the prompt condition) gave more diverse examples than writing with no prompt.

## Limits

- No controlled experiments, per-round accuracy tables, hyperparameters or seeds.
- The authors concede that example distributions may be unnatural, that annotators may overfit to the model they face, that results depend on the chosen target, and that nothing is guaranteed for later models that were never in the loop.
- Classification and span extraction only, English only; generative tasks are deferred.
- Dynamic benchmarks are costlier, and keeping scores comparable as rounds change is the main obstacle to adoption. The numbers are a 2021 snapshot.

## See Also
- [[HITL Annotation Pipeline]] — related (human validation of model output)
- [[Arena-Hard-Auto and BenchBuilder]] — alternative-to (curates a fixed prompt set from crowdsourced data instead of collecting adversarially)
- [[Eval Contamination Defenses]] — related (saturation and fresh data)
