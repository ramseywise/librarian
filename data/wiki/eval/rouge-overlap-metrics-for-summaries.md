---
title: ROUGE Overlap Metrics for Summaries
tags: [eval, graders-and-metrics, concept]
summary: "Lin's ROUGE package scores a candidate summary by n-gram, longest-common-subsequence, weighted LCS and skip-bigram overlap with reference summaries; its system-level correlation with human coverage scores on DUC 2001-2003 varies with summary length, stopword handling and number of references."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-lin-2004-rouge.md
---

# ROUGE Overlap Metrics for Summaries

Chin-Yew Lin (ACL 2004 workshop) asks whether automatic scores of n-gram, LCS and skip-bigram overlap between a candidate summary and reference summaries track what human judges say about summary quality. Taking BLEU in machine translation as the model, the working hypothesis is that agreement with human-written references should line up with human coverage ratings.

## The measures

- **ROUGE-N**: matching n-grams divided by all n-grams in the set of reference summaries, so it is a recall.
- **ROUGE-L**: built on the LCS of candidate and reference, giving recall LCS/m, precision LCS/n and an F-measure with weight beta. The author shows that MEAD's normalised pairwise LCS is this F-measure at beta = 1.
- **ROUGE-W**: a weighted LCS that favours consecutive matches. In the worked example with f(k) = k^2, a candidate that matches the first four reference words consecutively scores 0.571 and one that matches the same words with gaps scores 0.286.
- **ROUGE-S and ROUGE-SU**: skip-bigram overlap, where a skip-bigram is any pair of words in sentence order with arbitrary gaps. Against the reference "police killed the gunman" at beta = 1, S2 scores 0.5, S3 0.167 and S4 0.333 (worked example).
- In a second worked example, S2 gets a ROUGE-L of 0.75 and S3 gets 0.5, even though the two candidates have equal ROUGE-2.

## Correlation with human coverage (self-reported)

Pearson correlation of mean ROUGE with mean human coverage over DUC systems, with bootstrap confidence intervals; 17 measures were evaluated.

- DUC 2002, 100-word single-document (14 systems, 295 summaries per system, 2 references): every ROUGE variant correlates very highly.
- DUC 2001, 100-word single-document (12 systems, 1 reference): ROUGE-1 0.76 against ROUGE-2 0.84.
- DUC 2003, 10-word single-document (14 systems, 624 summaries per system, 1 reference): ROUGE-L is at 0.97, ROUGE-1 at 0.96 and ROUGE-2 at 0.75. Orders of N above 1 do significantly worse on such short summaries, and ROUGE-8 and ROUGE-9 reach 0.00 once stopwords are removed. A second reference gave no gain here.
- Multi-document 100-word tasks (about 30 summaries per system) rarely reach the high 90s except for long summaries, and the LCS-based variants ROUGE-L and ROUGE-W score poorly. On DUC 2001 100-word multi-document summaries with one reference, ROUGE-1 goes from 0.48 to 0.86 when stopwords are dropped.
- Over the DUC tasks as a whole, dropping stopwords mostly helped, and so did adding references.
- The author says manual DUC evaluation at scale would need over 3,000 hours of human effort (reported from Over and Yen).

## Limits

- Correlations are computed per system over 6 to 18 systems; the multi-document tasks give only about 30 summaries per system, which the author says makes the estimates unstable.
- Only Pearson is reported; the author says Spearman and Kendall follow it closely but does not show them. The human judges compared against a single manual summary even where several existed.
- The author calls high-90s correlation on multi-document tasks an open problem.
- Overlap is surface-level: ROUGE-L credits one LCS only (S4 ties S3), and ROUGE-S scores a reversed sentence (S5) at zero.
- The evaluation covers extractive-era news systems of 2001 to 2003, not abstractive or LLM output.
- The extraction infers that, because the DUC setting uses a very large beta and so only recall counts, length is not penalised.

## See Also
- [[BLEU, Brevity Penalty and SacreBLEU]] — prerequisite-for
- [[Text Metrics Beyond N-gram Overlap]] — alternative-to
- [[XSum Extreme Summarisation]] — related (ROUGE can mislead there: the extractive oracle scores high ROUGE but low on QA and human tests)
- [[Output Length Confounds Reference Metrics]] — related
