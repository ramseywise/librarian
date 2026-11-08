---
title: Concept-Drift Detector Families and Prequential Evaluation
tags: [foundations, concept]
summary: "A survey of online learning under drift sorts detectors into four families with different cost and precision, treats only real drift as needing adaptation, and scores streams prequentially because cross-validation breaks time order."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gama-2014-survey-concept-drift-adaptation.md
---

# Concept-Drift Detector Families and Prequential Evaluation

This page records a survey of drift handling in online supervised learning (Gama and colleagues). The file is the authors' pre-publication copy; the extraction notes that the file gives no confirmation of a 2014 volume, issue or DOI, so cite the venue only after checking elsewhere.

## What counts as drift

The survey defines drift as a change in the joint distribution of inputs and label. Real drift is a change in p(y|X); virtual drift, in the survey's own usage, is a change in p(X) alone (the paper notes the term means different things elsewhere). Population drift and prior-probability drift are listed too. Only a change that alters the predictions needs adaptation. Over time it names sudden, incremental, gradual and reoccurring patterns, and says an outlier is not drift: a detector has to separate real change from noise. Its stated requirements are to detect quickly, to stay robust to noise, and to run faster than examples arrive within fixed memory.

## Four detector families

| Family | Examples | Cost per item (survey table) |
|---|---|---|
| Sequential analysis | SPRT, CUSUM, Page-Hinkley | constant memory and time |
| Control charts | DDM, EWMA | constant memory and time |
| Two distributions on two windows | ADWIN, Kifer-style tests, KL divergence | between logarithmic and linear in the window |
| Contextual | Splice, IFCS | not tabulated in the extraction |

The survey says the two-window family needs more computation than watching an indicator, but may locate the change more precisely.

- **CUSUM and Page-Hinkley** accumulate deviations above a reference minus a slack delta and alarm past a threshold lambda. A small delta detects faster and raises more false alarms; a larger lambda gives fewer false alarms but may miss changes.
- **DDM** tracks the error rate with three states. The warning line is two standard deviations above the best error seen (about 95%), the action line is three (about 99%), and at least 30 examples are needed. Examples buffered during the warning stage train the replacement model.
- **ADWIN** compares two sub-windows with a Hoeffding-style bound, drops the older one when their means differ, assumes no data distribution and keeps an exponential histogram. The survey suggests a default confidence of 0.2.
- **Windows** trade speed for noise: a short window tracks change but degrades in stable periods, a long one is stable but slow. Blind adaptation (fixed windows, weighting, incremental learners) forgets at a constant speed regardless of change; informed adaptation reacts to a detector.
- **Ensembles** can be reweighted, continuously updated or structurally updated. Citing Minku and colleagues (2010), the survey reports that less diverse ensembles have lower error before a drift and more diverse ones do better soon after it.

## Evaluating a drift handler

Cross-validation does not suit streams, since folds scramble the time order. The survey recommends holdout or prequential scoring (predict, then train on the same example), forgetting old errors through a landmark window, a sliding window or a fading factor, and warns that a single average over time can conceal how a model adapts. A detector is judged by its probability of true detection, its false alarms (best given as average run length measured on drift-free data), its delay and its detection-point accuracy. Streaming cost can be reported in RAM-Hours. For two classifiers on the same stream it gives a McNemar test (reject equal performance when the statistic exceeds 6.635 at 0.99 confidence).

## Limits

- It covers online supervised learning with real drift only. Drift visible from p(X) alone, novelty detection and clustering-style semi-supervised methods are left out, which is the reverse emphasis from label-free input monitors.
- It assumes labels arrive promptly, while conceding they may come late, biased, expensive or never, and that under closed-loop feedback replaying history cannot compare handlers.
- Its only experiment is one illustration: one million synthetic instances from a drifting generator, scored with a window of 1,000, with no accuracy values in the text. The extraction notes there is no head-to-head detector benchmark and that synthetic data may not mirror real drift.
- Being a 2013 text, it predates deep-learning drift work and feature-store monitoring practice. Internal inconsistencies: the extraction found none beyond garbled equations and an unconfirmed venue.

## See Also
- [[Drift Types and What Monitors Can See]] — prerequisite-for (the label-free side of the same taxonomy)
- [[Error-Stream Detectors and Retraining Policy]] — prerequisite-for (the Page-Hinkley and CUSUM trade-off measured on one stream)
- [[Drift Tests: Significance, Magnitude and False Alarms]] — related
- [[Peeking and Sequential Testing]] — related
