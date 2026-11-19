---
title: BLEU, Brevity Penalty and SacreBLEU
tags: [eval, graders-and-metrics, concept]
summary: "BLEU is the geometric mean of clipped n-gram precisions times a corpus-level brevity penalty, validated on five systems and one language pair; Post later measured how undisclosed tokenisation moves scores by up to 1.8 BLEU and released SacreBLEU to fix the reference preprocessing."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-papineni-2001-bleu.md
  - data/raw/papers/2026-11-07-post-2018-call-clarity-reporting-bleu-scores.md
---

# BLEU, Brevity Penalty and SacreBLEU

## BLEU (Papineni et al., ACL)

The authors ask whether a fast, inexpensive, language-independent score built on n-gram overlap with reference translations can order machine translation systems as human judges would. Their hypothesis is that the closer a translation is to professional human references, the better it is.

**Modified n-gram precision.** Each candidate n-gram's count is capped at the most times it occurs in any one reference; the capped counts are summed over the corpus and divided by the number of candidate n-grams. For the degenerate candidate "the the the ..." the modified unigram precision is 2/7, although the standard unigram precision is 7/7 (two-reference worked example). In a three-reference example the good candidate gets 17/18 and the bad one 8/14.

**Brevity penalty.** BP = 1 if the candidate length c exceeds the reference length r, else e^(1 - r/c), computed over the whole corpus using the best match length (the reference length closest to the candidate length).

**Score.** BLEU = BP times exp of the weighted sum of log modified precisions, with N = 4 and uniform weights 1/N. Correlation with monolingual human judgments was best at maximum order 4, with 3 and 5 comparable.

### Evidence (self-reported)

Setup: 500-sentence Chinese-English news set, 3 commercial systems (S1 to S3) and 2 human translators (H1, H2), 2 references.

- BLEU, best to worst: H2 0.2571, H1 0.1934, then S3 0.0930, S2 0.0829 and S1 0.0527.
- Correlation of BLEU with mean monolingual-judge ratings is 0.99, and with bilingual-judge ratings 0.96, across the 5 systems.
- The S2 against S3 difference is significant (t = 3.4) over 20 blocks of 25 sentences; the authors treat a paired t of 1.7 or more as significant at 95%.
- The same human translator scores 0.3468 with four references against 0.2571 with two, so scores are not comparable across reference counts.
- Using one randomly chosen reference per story (40 stories) preserves the system rank order.

## SacreBLEU (Post, WMT 2018)

Post asks how far hidden BLEU settings and the way references are preprocessed move the reported scores. His hypothesis is that user-supplied reference tokenisation is the main cause of incomparable scores.

- Setup: one WMT 2017 entry (online-B) with its references, over 12 language arcs, scored with four tokenisation schemes (basic, split, unk, metric), cased and uncased. Changing the reference tokenisation moves BLEU by as much as 1.8 on one arc, and by about 1.0 on average across arcs.
- Two versions of the WMT14 en-de test set exist, with 2,737 and 3,004 sentences.
- In the author's own earlier workflow, preprocessing the reference moved scores by half a point.
- He checks seven widely cited papers for the BLEU configuration each used; many cases stay unclear.
- **Proposal:** metric-internal reference processing (WMT 13a) as the standard. **SacreBLEU** downloads references itself and emits a version string, invoked by piping detokenised output into the `sacrebleu` command with the test set and language pair as options.

## Limits

- The authors claim BLEU only over a whole test corpus; at sentence level it often departs from human judgment (footnote 4).
- The validation rests on 5 systems, one language pair and one 500-sentence set, so each correlation has n = 5. A companion study is cited for Arabic, Chinese, French and Spanish.
- No recall term and no handling of synonyms; only case folding is stated, with tokenisation not specified. The geometric mean is harsh when any modified precision is zero, which the authors assume is rare. Judges were non-professionals, and the bilingual judges failed to tell H1 from H2. The authors say summarisation and other generation tasks could be adapted, untested.
- Post measured one system on WMT17 only, with no significance testing; whether BLEU is a valid stand-in for human judgment is explicitly out of scope; his table of which configuration each paper used is his own reading, and SacreBLEU 1.2.10 is early, with later versions adding tokenisers and signatures.

## See Also
- [[ROUGE Overlap Metrics for Summaries]] — extends (the recall-oriented counterpart for summaries)
- [[Text Metrics Beyond N-gram Overlap]] — alternative-to
- [[Eval Metric Interpretation Pitfalls]] — related
- [[Output Length Confounds Reference Metrics]] — related
