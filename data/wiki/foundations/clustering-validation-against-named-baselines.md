---
title: Clustering Validation Against Named Baselines
tags: [foundations, eval, pattern]
summary: "Customer clustering is only evidence of structure when its silhouette beats a random partition and the trivial k=2 split computed in the same call, when unsupervised leakage analogues (restated timestamp columns, scaler fit outside resamples, a sum beside its own decomposition) are ruled out by name, and when a value-reading matrix-health rule stops a degenerate matrix escaping through the 'structure is weak' clause."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-17-customer-segmentation.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-17-customer-segmentation.md
---

# Clustering Validation Against Named Baselines

From a galactus ML prototype segmenting ~29k retail-brokerage customers from a year of
trades (k-means over 16 behavioural features across activity, performance,
diversification and timing). The final answer — k=4, silhouette 0.25 — was modest, and the
point of the method is that a modest answer could be reported *credibly*.

## Name the baseline before computing the score

Mean silhouette on the standardized matrix, against **two** baselines: a **random partition**
at the chosen k (−0.01 here) and **k-means at k=2**, the trivial split (0.23). A clustering
that does not beat both has not been shown to find structure; only k=3 and k=4 did.
Baselines are computed **in the same function call** as the score, so a result cannot be
reported without its comparator. Davies–Bouldin is the secondary check; here it agreed.

## Unsupervised leakage has analogues

No train/test leak in the supervised sense, but three concrete ones, each named with the
column that would cause it and reported **red until proven**, before any score exists:

- **A column that restates a timestamp.** A provided `cohort` label was exactly the
  customer's first-trade month — a *perfect* diagonal crosstab, zero off-diagonal cells.
  Check with a full crosstab, not a correlation: a strong correlate and a restatement need
  different treatment. Segments built on it encode tenure, not behaviour.
- **Scaler fit outside the resample.** If stability is tested by refitting on subsamples,
  the scaler is fit inside each subsample.
- **A total beside its own decomposition** (total trades plus twelve monthly counts) counts
  the same information thirteen times and silently up-weights activity in Euclidean space.

Excluded leakage columns become **validation variables**: the "tenure test" cross-tabs
segment against first-trade month. Leaked, it would be near-diagonal; here every segment
spanned all six signup months. One real gradient (dormant segment tilted to late joiners)
was named as mechanical — less time to accumulate trades — not leakage.

**An implausibly clean separation is a finding, not a result:** the first hypothesis for a
very high silhouette is that a restated column survived into the matrix.

## The weak-result escape hatch

The leakage check's three rules all read column *names*. An adversarial review found a
degenerate matrix (collapsed or constant features) would pass every rule and then exit
legitimately through the plan's pre-authorised "structure is weak, report it" clause. Fix:
a fourth, **value-reading matrix-health rule** (variance, collapse), with a regression test
of the escape route. It is what makes "weak structure" a statement about the data rather
than about broken features — both produce a low score.

## Feature-construction hazards found

- **Empty-array sentinels collapse `nunique`.** A catalog encoded missing sector as `{""}`
  for ~81% of instruments; naive distinct-count scored such traders as single-sector. Treat
  the sentinel as a third state and add a coverage feature — that feature defined an
  otherwise-invisible "derivative specialists" segment.
- **Log-scale heavy skew sign-preservingly** — `sign(x)·log1p(|x|)` — because P&L is
  legitimately negative and bare `log1p` yields NaN. Keep the log set as an explicit tuple
  with a skew assertion.
- **Explicit date format per file**, measured not guessed (the second file was day-first),
  with a full-calendar / zero-NaT assertion.
- **Pre-computed derived assets as checklists, not data**: a prior feature table with
  conflicting duplicate IDs and an unkeyed positional label file were unusable as rows but
  useful as a feature vocabulary checklist and a cluster-balance prior.
- **Stamp provenance on generated reports** (run id, feature columns, input hashes, leakage
  verdicts) so a published-then-falsified result can be retracted.

## See Also
- [[Data Sufficiency Refusal]] — extends (the supervised refusal; this is the unsupervised case)
- [[HDBSCAN with KMeans Fallback]] — alternative-to (density method for the same task)
- [[An Unrun Scan Is Not a Clean Scan]] — extends (tests outside testpaths collected zero in this build)
- [[Rationale-Blind Worst-Case Review]] — extends (the advisor that found the escape hatch)
- [[A Sentinel Catches Forgetting, Not Asserting]] — extends (a seeded sweep must not record `seed` as NotApplicable)
