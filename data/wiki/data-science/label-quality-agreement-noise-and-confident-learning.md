---
title: "Label Quality: Agreement, Noise and Confident Learning"
tags: [data-science, classical-ml, concept]
summary: "Kappa measures agreement, not correctness, and is unstable on rare classes; label noise hurts probabilities more than ranking unless it depends on the row; confident-learning flags are a review list, not a cleaning rule."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--14-learning-from-corrections.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch11-managing-linguistic-data.md
---

# Label Quality: Agreement, Noise and Confident Learning

Every correction looks like a free label, but a label is a decision made under a rule. Settle who decides, what the rule says (hard cases included), which label you wait for (a reviewer's opinion in minutes or the true outcome in months), and how disagreement is resolved (a senior person decides, or the row is marked ambiguous and the rule rewritten; averaging hides a rule that does not work). Measure the annotator as well as the model by seeding known problems and counting how many come back.

## Agreement is not correctness

Cohen's kappa = (p_o - p_e)/(1 - p_e): observed agreement corrected for chance. Three simulated annotator pairs on 20,000 cases (6% positives):

| Pair | Raw agreement | Kappa | Recall A, B | Recall on shared blind spot |
|---|---|---|---|---|
| Two careful, independent | 0.943 | 0.550 | 0.802, 0.787 | 0.798 |
| Careful plus one who rarely flags | 0.923 | 0.045 | 0.802, 0.054 | 0.798 |
| Two careful, same blind spot | 0.977 | 0.797 | 0.826, 0.818 | 0.000 |

Raw agreement fails on a rare class (row 2); kappa catches it. The third row is the trap: the highest kappa, yet neither ever flags a changed bank account (13% of all problems). Agreement cannot see a mistake two people share; an outside source of truth (seeded problems, later outcomes) can. Kappa is also unstable: with 200 double-labelled cases (about 12 problems) the same pair ranges 0.312 to 0.740 (5th to 95th percentile); 500 gives 0.409 to 0.656; 2,000 still 0.489 to 0.611.

### Agreement in annotated-corpus practice

The NLTK book's chapter on managing linguistic data gives the corpus-building version. Bird, Klein and Loper advise writing annotation guidelines, double-annotating a sample (they suggest 10% of the corpus) and reporting agreement, which they say caps how well any system trained on the corpus can perform. They caution that the acceptable level is task-dependent: 90% agreement would be poor for part-of-speech tagging and exceptional for semantic role labelling. A worked example: if four codes are equally likely, two random annotators agree a quarter of the time, which is kappa 0; agreeing half the time gives kappa 0.333. For segmentation, `nltk.windowdiff` with window size 3 gives partial credit for near-miss boundaries; on three 23-character boundary strings it scored 0 (s1 against s1), 4 (s1 against s2) and 16 (s2 against s3). They also advise releasing annotations as standoff records that point to stable identifiers in the source, leaving the source untouched so independent annotations can be compared.

## What noise breaks depends on its shape

Train on 20,000 noisy rows (mean of 5 seeds), judged on true outcomes with priced routing ([[Review Route Thresholds From Priced Costs]]):

| Labels | AUC | Cost, calibrated on noisy labels | Cost, calibrated on 5,000 true labels |
|---|---|---|---|
| None | 0.857 | 3.321 | 3.321 |
| Symmetric 5% flips | 0.851 | 4.414 (pays 0.1%) | 3.386 |
| Misses 30% of problems | 0.854 | 3.439 | 3.380 |
| Misses small cases | 0.830 | 3.664 | 3.607 |

- Ranking survives random noise but probabilities do not: mean score rose 0.057 to 0.102 on a 6% base rate. A small trusted set repairs calibration ([[Probability Calibration and Reliability Curves]]).
- Missing problems looks like an improvement (mean score 0.044, paid share 66.4% against 62.5%) while cost rises.
- Noise that depends on the row cannot be fixed by calibration, which only rescales: AUC 0.830 and cost only back to 3.607. Compare [[Regularisation Under Noisy Labels]].

## Confident learning

It takes out-of-sample probabilities and noisy labels; a class threshold is the mean predicted probability of that class among rows labelled with it; a row is flagged if it confidently belongs to a class other than its label. It assumes noise depends only on the true class. Against the plain rule "out-of-fold prediction disagrees with label":

| Noise | Share wrong | CL precision, recall | Plain rule precision, recall |
|---|---|---|---|
| Symmetric 5% | 0.050 | 0.347, 0.737 | 0.475, 0.941 |
| Misses 30% of problems | 0.022 | 0.205, 0.468 | 0.123, 0.252 |
| Misses small cases | 0.022 | 0.121, 0.210 | 0.110, 0.215 |

It wins only where per-class thresholds suit the noise; where noise depends on the row both find about a fifth. Precision is far below image-benchmark results, plausibly (untested) because even the true probability gives AUC only 0.861, so a high-score "good" label is often genuinely good. Retraining after removing flags improved cost modestly (3.386 to 3.344 for symmetric noise; clerk-checking the flags 3.335), but a flawed checker sent the flags made it worse (3.634 against 3.607 left alone). Treat flags as a review list and check on trusted labels.

## Limits

- The chapter 11 practices are stated, not tested on any measured outcome, and the examples are toy ones.
- It predates crowd-sourced and model-produced labels.
- Its Toolbox and XML sections are tied to Python 2 and NLTK 2.

## See Also
- [[Learning From Corrections and the Audit Sample]] — extends
- [[Regularisation Under Noisy Labels]] — related
- [[Choosing Which Rows to Label: Active Learning and Rules]] — related
