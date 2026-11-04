---
title: EDA Audit Loop
tags: [foundations, pattern]
summary: "What to do with a new extract before any test or model: fix the row unit, hunt impossible and missing values, pick summaries the shape allows, and write the findings and open questions down."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--01-descriptive-statistics-and-eda.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--README.md
---

# EDA Audit Loop

Exploration comes before inference because formal inference answers a question you already framed, while looking tells you whether you framed the right one. Most analysis errors that reach a decision are not exotic statistics: a join that duplicated rows, a unit that changed, or a mean quoted over a distribution where the mean describes nobody.

The loop: load and type-check, then look for missing, impossible and duplicate values, then read one column at a time for shape, then [[Robust Summaries for Skewed Metrics]] the shape allows, then two columns at a time, then write down findings. A new question sends you back to the second step.

## Steps

- **Fix what one row is.** Revenue per user, per session and per order are three numbers with three denominators, and their standard errors differ too (see [[Delta Method for Ratio Metrics]]).
- **Types decide what you may compute.** Counts, continuous values, unordered categories and binary flags each allow different summaries. An ordinal rating has unequal gaps, so its mean is a convenience. An integer ID means nothing numerically yet `describe()` reports its mean. The type later picks the test ([[Statistical Test Selection]]).
- **Look for the impossible.** A revenue column whose median and 75th percentile are both zero, whose standard deviation is about 60 times the mean, with a negative minimum and an absurd maximum needs a person, not a test: ask the owner what a negative row is. Sentinel values (99 for "refused", -1, 1970-01-01, empty strings) pass through `describe()` silently; a suspiciously round maximum is the tell.
- **Write exclusions down and count them.** In the worked extract of 20,000 rows, 6 negative-revenue rows and 2 rows at 48,000 were removed (19,992 kept) because they could be explained. Dropping real large customers changes the question; explain, then decide, then count. Every exclusion is an analyst degree of freedom (see [[Multiple Comparisons Corrections]]).
- **Treat missing values as data.** Compare the missing and non-missing groups on other columns before dropping. Here 300 blank devices had the same country mix as the rest, so they were kept as an explicit `unknown` level. If missingness tracks a segment (tracking failing on one old browser), dropping it silently removes that segment. Beware an apparent gap in a group summary that is really two outlier rows in the other group (a mean of 8.21 against 0.97 was entirely those two rows).
- **Two columns at a time.** Keep group size next to every rate ([[Small-N Trap and Shrinkage]]). A group table is association, not cause: desktop converting at 7.5% against mobile at 4.0% generates a hypothesis only.

## Writing it down

An EDA is finished when someone else can act on it. A useful note has: what the extract is and what one row is; what was removed and why; what was kept and how labelled; the shape of each key metric; group differences flagged as observational; what to do next; and the open questions (is a refund part of the metric, who owns the two large accounts). The open questions are the bridge to the next stage.

## How it fails

- Quoting a mean over a zero-inflated column ("average spend 3.30" when 95% of users spent nothing). Report conversion and spend among buyers as well as the blended figure, since blended is their product.
- Deleting outliers because they are large rather than because they are explained.
- Hypotheses found by looking are already selected. Confirm them on new data, not the data that suggested them.

## See Also
- [[Robust Summaries for Skewed Metrics]] — related (the summaries step of the loop)
- [[Inspection Paradox in Metrics]] — related (the row unit decides whose average it is)
- [[Small-N Trap and Shrinkage]] — related (why group tables mislead)
- [[Data Science Curriculum Layers]] — related (the analytics layers this audit belongs to)
- [[Anscombe's Quartet: Plot Before Summarising]] — related (why plot before summarising)
