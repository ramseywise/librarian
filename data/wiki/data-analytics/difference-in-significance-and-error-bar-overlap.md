---
title: Difference in Significance and Error Bar Overlap
tags: [data-analytics, probability-and-statistics, concept]
summary: "Two bad shortcuts for comparing groups: calling one result significant and another not, and judging by whether error bars overlap. Compare the groups directly with a test or an interval for their difference."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch05-bad-judges-significance.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch05-multivariate-linear-models.md
---

# Difference in Significance and Error Bar Overlap

Reinhart's chapter 5 names two ways of judging whether two groups differ that mislead. Both replace a direct comparison with a comparison of two separate verdicts.

## Difference in significance

Take two drugs with the same nonzero effect against placebo, each in an independent trial with power B. Probability that exactly one trial reaches significance: 2B(1-B). With B = 0.5 this is 0.5, so a coin-flip "disagreement" appears although the drugs are identical.

Cited cases in the extraction:
- The 2007 trial of a Boots No. 7 serum: 43% of users improved against 22% of controls given the serum minus its active ingredient. The serum's improvement was called significant and the control's insignificant, yet Reinhart reports that comparing the two groups directly showed no significant difference.
- Five statin meta-analyses (patients without prior cardiovascular disease; three said yes, two inconclusive) each put relative mortality risk near 0.9, about a tenth fewer deaths. Reinhart reads them as agreeing.
- Reinhart reports that neuroscientists use the difference-in-significance method about half the time when comparing groups.

Reinhart adds that a replication failure may fit the original result once truth inflation and the lower true power are taken into account ([[Winner's Curse]]).

McElreath (Statistical Rethinking ch. 5) gives the same warning for parameters: with 0.15 +/- 0.02 for one and 0.02 +/- 0.10 for the other, the first is clearly nonzero and the second is not, yet their difference is 0.13 +/- 0.10 (hypothetical, assumed uncorrelated). The two verdicts do not show that the parameters differ.

## Overlapping error bars

Eyeballing whether two error bars overlap is stricter than a test at p < 0.05: in Reinhart's invented Fixitol and Solvix example (two groups of 10 patients, bars assumed to be 95% confidence intervals, no underlying numbers given) the intervals overlap while a t test gives p < 0.05. In the usual case a standard error bar is roughly half the width of a 95% interval, so a plot labelled "standard error" may really show two of them. Reinhart cites surveys in which most psychologists, neuroscientists and medical researchers read significance off overlap, and so did most climate-science papers that drew error bars on two groups. He notes that a textbook on error analysis (Taylor) teaches judging by eye.

Reading an interval by eye works only when the comparison is with one fixed number, such as zero.

## What to do instead

- Test the difference, or give an interval for the difference, rather than noting that one group was significant and one was not.
- State whether error bars are standard deviation, standard error or a 95% interval.
- When many groups are compared, correct for multiplicity; Reinhart calls Bonferroni tedious and conservative ([[Multiple Comparisons Corrections]]).

## Limits

- The Fixitol and Solvix figures are illustrations; the chapter gives no data.
- Gabriel comparison intervals, a visual procedure, assume the groups share a standard deviation.
- A direct comparison does not add power; it only avoids concluding that the drugs differ.
- Footnote 1 is not resolvable from the extract.

## See Also
- [[P-Value Misreadings]] — prerequisite-for
- [[Confidence Interval Coverage and Wilson]] — related
- [[Minimum Detectable Effect and Sample Size]] — related (power drives the 2B(1-B) result)
