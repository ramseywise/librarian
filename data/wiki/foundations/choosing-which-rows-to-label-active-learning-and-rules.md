---
title: "Choosing Which Rows to Label: Active Learning and Rules"
tags: [foundations, comparison]
summary: "Rules can stand in for many hand labels but learned rule weights lose to a plain vote at low label density; uncertainty sampling beat random on generated data and lost AUC on real data, and its labelled set is biased."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--14-learning-from-corrections.md
---

# Choosing Which Rows to Label: Active Learning and Rules

When labels are scarce there are two levers: get labels from rules, or choose which rows a person labels. Both are tested here on a generated review task (about 6% problems) and, for active learning, on a real 22.1% default file. Context: [[Label Quality: Agreement, Noise and Confident Learning]].

## Weak supervision: rules as labels

Labelling functions each vote "problem", "good" or abstain; a label model learns how far to trust each from agreements and disagreements and trains on soft labels. Eight hand-written rules (five "problem", three "good") gave mean 1.02 votes per case and 29% with no vote. "Problem" rules were mostly wrong (accuracy 0.150 to 0.472) yet informative: one right 26% of the time picks problems at over four times the 6% base rate. Models trained on each label source (calibrated on 5,000 true labels, 5 seeds):

| Source | AUC | Priced cost |
|---|---|---|
| Rules: majority vote | 0.800 | 3.773 |
| Rules: learned weights | 0.783 | 4.119 |
| Rules + 4 copies of one rule: majority vote | 0.771 | 4.061 |
| Rules + 4 copies: learned weights | 0.562 | 4.461 |
| 200 clerk labels | 0.692 | 4.411 |
| 1,000 clerk labels | 0.784 | 4.021 |
| 5,000 clerk labels | 0.826 | 3.696 |

A majority vote sits between 1,000 and 5,000 clerk labels. Learned weights lost (an independent EM sketch, not the published model); at label density near 1 there is little room for weighting to beat a vote, which is why published systems include an optimiser choosing between them. Correlated rules break the independence assumption: copies' agreement is read as accuracy and AUC collapses to 0.562. Caveats: the rules were written knowing the generator, calibration still used true labels, and a rule cannot teach what its writer has not imagined.

## Active learning: uncertainty sampling

Start from 100 random labels, buy 100 at a time to 2,000, compare random, uncertainty (nearest 0.5) and highest score (what a queue of the riskiest items gives). Differences are uncertainty minus random over 10 seeds:

| Data, learner | AUC diff | Seeds won | Cost diff |
|---|---|---|---|
| Generated, logistic | +0.003 | 9 | -0.021 |
| Generated, boosted | +0.020 | 10 | -0.206 |
| Credit, logistic | -0.026 | 0 | +4.346 |
| Credit, boosted | -0.012 | 0 | -0.802 (6 of 10 seeds) |

Highest-score was worse again on credit (AUC diff -0.079 logistic, -0.035 boosted). The cause is not identified; the labelled credit set became unrepresentative (46 to 48% defaulters against 22%), and a published survey reports that active learning can need more labels than passive learning. You cannot know which case you are in without a comparison, which needs a random sample anyway. Batches of 500 matched batches of 100, and missing 30% of problems did not hurt (gain 0.022), on this generator.

**The bias outlives the model.** The uncertainty set is about a third problems against a true 6%; train on it, never estimate a rate from it, and calibrate on a random set. A review queue is already an active learner of a sort, so the same bias applies ([[Learning From Corrections and the Audit Sample]]).

## See Also
- [[Label Quality: Agreement, Noise and Confident Learning]] — related
- [[Learning From Corrections and the Audit Sample]] — related
- [[Train, Validation and Test Discipline]] — related
