---
title: Diverse Beam Search
tags: [llm, architecture, pattern]
summary: "Split the beam budget into groups, decode groups left to right, and penalise each group's choices for similarity to earlier groups, so one beam search call returns a diverse list; tested on COCO captioning, visual question generation and English-French translation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-vijayakumar-2018-diverse-beam-search-improved-description.md
---

# Diverse Beam Search

Vijayakumar, Cogswell, Selvaraju and colleagues ask whether beam search can be changed to return a varied list of good sequences at no extra compute, and whether that lifts top-1 and oracle quality. The source is the arXiv v2 preprint (22 Oct 2018); the AAAI 2018 paper it is associated with is a shorter version.

## Mechanism

The beam budget B is divided into G groups, each holding B' = B/G beams. Groups are decoded in order, left to right in time. Within group g, each step runs beam search on the sum of the model log-probability and lambda times a dissimilarity term (Hamming by default) against the tokens chosen by groups 1 to g-1 at that step. The authors call the procedure doubly greedy, over time and over groups.

- Group 1 carries no diversity term, so by the authors' argument the method does no worse than a plain beam search of width B/G.
- G = 1 reduces it to plain beam search; all reported results use G = B, the maximum exploration setting.
- Staggered parallel runs take T + G steps, against T x G for the black-box approach of Gimpel et al. (analytic claim).
- The diversity strength lambda worked over 0.2 to 0.8; too high a value overpowers the model probability and gives ungrammatical outputs. It was tuned per task by grid search on validation data.
- Of the diversity functions tried, Hamming performed best despite being simple; the others also beat plain beam search.

## Results (self-reported, B = 20)

| Task and setup | Diverse beam search | Plain beam search |
|---|---|---|
| COCO captioning, neuraltalk2, distinct 4-grams | 13.44 | 5.67 |
| COCO captioning, oracle SPICE@20 | 28.09 | 27.34 |
| PASCAL-50S (captioner trained on COCO), oracle SPICE@20 | 9.293 | 8.74 |
| Visual question generation, oracle SPICE@20 | 27.94 | 26.74 |
| Visual question generation, distinct 4-grams | 12.24 | 5.23 |
| En-Fr newstest-2013, GRU with attention, oracle BLEU-4@20 | 18.77 | 18.44 |
| En-Fr, top-1 BLEU-4 | 13.69 | 13.52 |
| En-Fr, distinct 4-grams | 5.54 | 3.23 |

- On PASCAL-50S, oracle@20 improves by 7.24% over beam search and 9.60% over Li and Jurafsky's method, and the best top-1 log-probability is higher (-6.53 against -6.91).
- On COCO the oracle SPICE gain over beam search grows with image complexity, from 0.67 for simple images to 0.91 for average and 1.13 for complex ones.
- In a human forced choice on PASCAL-50S, diverse-beam captions were preferred 60% of the time; the preference rate climbs with difficulty, to roughly 50%, 69% and 83% for simple, average and difficult images (correlation 0.73 with difficulty).
- On En-Fr, Li et al. (2015) is slightly higher on oracle BLEU-4@20 at 18.86 against 18.77.

## Limits

- No variance, seeds or significance tests; gains in absolute SPICE and BLEU are small.
- Models are 2015-era LSTM and GRU captioners and translation models; no Transformer or LLM experiments.
- Not best on every oracle column in translation.
- Baselines are the authors' own reimplementations, and the re-rankers originally used by Li and Jurafsky and by Li et al. were dropped.
- Oracle scores take the best of 20 candidates, so they reward diversity by design; the top-1 gains are small.
- The lambda value per task is not printed, only sensitivity plots.
- The dissimilarity is token level, and the authors note that initial words dominate the diversity.
- Table 2's Li and Jurafsky visual-question-generation row appears to copy COCO values.

## See Also
- [[Nucleus Sampling and Text Degeneration]] — related (another change to decoding, tested on open-ended text)
- [[MMI Objective for Generic Responses]] — alternative-to (another diversity-promoting decoding objective, compared as a baseline)
- [[Attention for Neural Machine Translation (Bahdanau, Luong, Decomposable)]] — related (the translation model family it is tested on)
