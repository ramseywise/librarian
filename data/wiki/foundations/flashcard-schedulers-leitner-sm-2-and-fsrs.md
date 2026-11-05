---
title: "Flashcard Schedulers: Leitner, SM-2 and FSRS"
tags: [foundations, comparison]
summary: "Leitner boxes and SM-2 need no review history, while FSRS tracks per-card memory state, fits parameters per user or preset and beats half-life regression at predicting recall on its own project's benchmark; prediction is not learning, and no controlled comparison of learning outcomes was found, so start simple."
updated: 2026-11-05
sources:
  - data/raw/web/2026-11-05-flashcard-scheduler-sources.md
  - data/raw/web/2026-11-05-citation-check-corrections.md
  - data/raw/web/2026-11-05-citation-check-corrections-third-pass.md
---

# Flashcard Schedulers: Leitner, SM-2 and FSRS

A scheduler turns the [[Spaced Repetition and Self-Quizzing From a Knowledge Base|spacing effect]] into
due dates. The three common choices differ in how much they model and how much history they need.

| | Leitner | SM-2 | FSRS |
|---|---|---|---|
| State per card | A box | Repetition count, ease factor (EF) | Difficulty, stability |
| Parameters | Box intervals | Fixed constants | 21 in FSRS-6, 34 in FSRS-7 |
| Needs history to start | No | No | Runs on defaults; fitting needs reviews |
| Dependencies | None | None | [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) (MIT) |

## Leitner

Cards move between boxes with growing intervals, for example 1, 2, 4, 8, 16 as drawn in Settles &
Meeder (ACL 2016). They describe it as adaptive because a card's interval can rise or fall with
performance. They cite Leitner's own book (*So lernt man lernen*, 1972), which was not read here.

## SM-2

From [Piotr Wozniak's 1990 thesis text](https://super-memory.com/english/ol/sm2.htm), and simple enough to write down:

```
I(1) = 1, I(2) = 6, I(n) = I(n-1) * EF
EF'  = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))     q is the 0-5 grade
EF starts at 2.5 and never falls below 1.3
q < 3 restarts the repetitions and leaves EF unchanged
```

So q=5 adds 0.1 to EF, q=4 leaves it alone and q=3 takes off 0.14. With EF held at 2.5 by q=4 answers, the
intervals run 1, 6, 15, 37.5 days before rounding.

## FSRS

FSRS keeps difficulty D in [1, 10] and stability S (the interval at which recall probability is 90%) per
card, and predicts retrievability R from them. The project's [benchmark](https://github.com/open-spaced-repetition/srs-benchmark) covers
9,999 collections, each from one Anki user, and 349,923,850 reviews. Same-day reviews are left out of evaluation, though
FSRS takes them as input. The results are self-reported, since the FSRS project runs it, and were read from its README
on 2026-11-05:

| Model | Log loss | RMSE (bins) | AUC |
|---|---|---|---|
| RWKV-Instant | 0.2773 | 0.02502 | 0.8329 |
| FSRS-7 recency, 100 epochs | 0.3363 | 0.05764 | 0.7243 |
| Moving average | 0.3369 | 0.05915 | 0.7001 |
| FSRS-7 (34 params) | 0.3401 | 0.0634 | 0.7167 |
| FSRS-6 (21 params) | 0.3460 | 0.0653 | 0.7034 |
| FSRS-7 default params | 0.3620 | 0.0910 | 0.7029 |
| Half-life regression | 0.4694 | 0.1275 | 0.6369 |

A zero-parameter moving average beats plain FSRS-6 and FSRS-7 on log loss and RMSE, though not on AUC. The FSRS-7 log-loss
gap is within the README's 99% confidence intervals (0.3401±0.0043 against 0.3369±0.0042). Recency-weighted FSRS-7 beats the
moving average clearly on AUC; its log-loss and RMSE point estimates are lower, but their ± ranges overlap. Note also
the drop from fitted to default parameters. The section read has no SM-2 row. The benchmark measures prediction of
recall, not whether anyone learned more.

Half-life regression (HLR) comes from Settles & Meeder, whose results are mixed against Leitner. Mean absolute error was
at least 45% lower, yet Leitner had the highest AUC. Against Leitner, HLR moved daily retention by +0.3 (any activity),
+0.3 (lessons) and -7.3 (practice). The 12% figure is one HLR variant against another, not HLR against Leitner.

The [Anki manual](https://docs.ankiweb.net/deck-options.html) calls SM-2 legacy and says FSRS lets you retain more for the
same study time (self-reported), with a default desired retention of 90%. Among reasons an optimiser does badly, it
lists having under a few hundred reviews. None of this is a controlled result.

## Choosing one

This is this wiki's inference, not a finding:

1. Start with SM-2 or fixed Leitner boxes. They have no dependencies, and a new deck has too few reviews to
   fit parameters.
2. Move to FSRS through py-fsrs on default parameters once real review history exists. The only default-parameter
   row in the benchmark section read is FSRS-7, so it does not describe py-fsrs's 21-weight defaults.
3. Optimise per user only after a few hundred reviews, in line with Anki's warning.

Also this wiki's inference: log what a later replay needs from the start, at least a card id, timestamp and grade. In this repo
`logs/flashcards.jsonl` holds self-grades; whether each record has what an FSRS replay needs is unchecked.

## Open questions

- No controlled study comparing learning outcomes under FSRS and SM-2 was found.
- The KDD 2022 MaiMemo scheduler paper (Ye, Su, Cao) comes from the line of work FSRS's docs trace it to. Its abstract does
  not name FSRS, and its full text was not read.

## See Also
- [[Spaced Repetition and Self-Quizzing From a Knowledge Base]] — prerequisite-for (the effects a scheduler automates)
- [[Graded Rehearsal Drill Harness]] — related (a log of graded attempts a scheduler could replay)
- [[Text Classification Metrics: Macro-F1, Log-Loss and Calibration]] — related (what log loss rewards)
