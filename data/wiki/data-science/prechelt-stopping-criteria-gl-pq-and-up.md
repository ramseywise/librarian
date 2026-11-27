---
title: "Prechelt's Stopping Criteria: GL, PQ and UP"
tags: [data-science, deep-learning, comparison]
summary: "Prechelt defines three classes of validation-based rule for stopping neural-network training, GL, PQ and UP, and compares 14 variants over 1296 runs; later-stopping rules bought roughly 4% lower test error for roughly four times the training time."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-prechelt-1998-early-stopping-but-when.md
---

# Prechelt's Stopping Criteria: GL, PQ and UP

Prechelt asks which validation-based rule should end the training of a neural network when training time trades against generalisation. He expects rules that stop later to generalise a little better at a large time cost, with no class of rule clearly ahead. The figures below are his own measurements of the rules he defines, so they are self-reported.

## The three classes

Write E_va(t) for validation error after epoch t, and E_opt(t) for the lowest validation error seen up to t.

- **GL.** The generalisation loss GL(t) is 100 times the ratio E_va(t) over E_opt(t), minus one: the percent by which validation error sits above its running minimum. GL_alpha stops at the first epoch where GL(t) is above alpha.
- **PQ.** Epochs are grouped into training strips of k epochs. P_k(t), in per thousand, measures how much the strip's average training error exceeds its smallest training error. PQ_alpha stops at the first strip end where GL(t) divided by P_k(t) is above alpha.
- **UP.** UP_s stops once the validation error has risen across s consecutive strips. UP_1 stops at the first strip end where the error is higher than one strip earlier.

The result of a run is the set of weights at the validation minimum found before stopping. The plain procedure from his introduction: hold out a validation set (for example one third of the data), train on the rest, check validation error now and then (for example every fifth epoch), stop when it is higher than at the previous check, and keep the weights from that previous check.

## What the study measured

Setup: fully connected multilayer perceptrons trained with RPROP on 12 Proben1 problems. Twelve topologies, three dataset variants and three runs per problem give 1296 runs, and each run scores 14 criteria on one error curve, for 18144 records. Times and errors are relative to GL2 and averaged over all runs (self-reported).

- Later-stopping rules gave roughly 4% lower test error for roughly a fourfold rise in training time; none dominated.
- Table 1 lists the slowest rule, PQ3, with a good-result fraction P_g of 0.800, time 3.095 and error 0.988 (both normalised); the fastest, UP2, gets P_g 0.587 with time 0.766 and error 1.024.
- Redundancy, the extra training beyond what the same run needed to reach the same result, is 2.140 for PQ3 and 0.277 for UP2.
- The lowest-error rules beat the fairly quick GL2 by only about 1% test error. Several moderately slow rules sat about 2% above the best rule of the same run.
- One Glass curve (4+4 hidden nodes) shows 16 local minima before heavy overfitting near epoch 400; the best stop is epoch 205. Training to epoch 400 instead of stopping after the deep dip at epoch 45 takes about seven times as long to learn and gains 1.1% on validation error.
- In 270 of the 18144 records (1.5%, from 125 runs) training ended at the 3000-epoch cap rather than by the rule.
- On the building problem, the one dataset split chronologically rather than at random, GL rules were much less robust. PQ was less robust on card and horse.

## Prechelt's advice

For setups like his (MLP, RPROP, small datasets) he gives three rules of thumb:

1. Prefer fast rules, unless a small gain (such as 4%) justifies a large time increase (such as a factor of 4).
2. If the aim is to maximise the chance of a good solution, choose a GL rule.
3. If the aim is average quality, choose PQ when the network overfits very little and UP otherwise.

He reports UP3, UP4 and UP6 as the best time-versus-error trades for one run, and prefers GL rules if he makes several runs and keeps whichever has the best validation error.

## Limits

- He used one learner (RPROP, epoch-wise updates, small training sets) and squared error only; his expectation that other learners behave alike, if they take no extreme steps, is speculation.
- There are twelve problems, none strongly nonlinear. The rules differ by problem, and what causes that is left open.
- He says his discussion is shaped by the 14 rules he picked; his PQ rules are slower than the rest, so setting PQ0.5 against GL1 or UP2 is unfair.
- The validation data never updates weights; a real application would retrain with it, and that was not tested.
- There are no significance tests or confidence intervals, only a standard deviation over 108 runs in a figure.
- The cited theory (Wang et al., Amari et al.) does not cover these MLPs and small datasets, so the evidence is empirical.
- No venue, book title or year is printed; the latest reference is dated September 1997. The setting is 1990s single-run RPROP MLPs, with nothing on SGD, minibatches, deep networks or large data.

## See Also
- [[Regularisation Knobs and Early Stopping]] — prerequisite-for
- [[Train, Validation and Test Discipline]] — related
