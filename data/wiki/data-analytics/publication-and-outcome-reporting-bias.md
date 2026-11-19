---
title: Publication and Outcome Reporting Bias
tags: [data-analytics, probability-and-statistics, concept]
summary: "Unshared data, unpublished studies and unreported outcomes skew the visible evidence toward extreme results; register protocols, share data and code, publish negative results and check study power against the share of positive results."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch11-hiding-data.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch10-everybody-makes-mistakes.md
---

# Publication and Outcome Reporting Bias

Publication bias is the file drawer problem: negative studies are never published. Outcome reporting bias works inside a study: when dull outcomes go unreported, systematic reviews drift toward extreme findings. Reinhart's chapter 11 lists cited figures; all come from endnotes not in the extract.

## Cited figures

- After six months psychology authors had supplied data for only 64 of 249 requested studies, and the non-sharers' papers had more errors and weaker evidence. Among APA journal papers whose errors could be checked from the text, at least half contained one and 15% had a significant result only because of an error.
- Of 516 articles whose authors could be reached, fewer than half of datasets from papers older than 20 years were still available.
- Adding unpublished outcomes could shrink a quarter of significant Cochrane review results by 20% or more of effect size; over a third of reviews were probably affected by outcome reporting bias, and one in five significant results might lose significance.
- Half of academic psychologists, by their own admission, publish only the experiments that worked.
- A meta-analysis of TP53 and head and neck cancer found a significant correlation across 18 published studies, which disappeared when unpublished data were included. In antidepressant trials, Pfizer's unpublished reboxetine data outweighed the published data threefold and pointed to an ineffective drug.
- Over 40% of clinical trials were registered on ClinicalTrials.gov after recruitment began; the median late study was 10 months late.

Chapter 10 adds that about 38% of Nature papers have typos or calculation errors in p values, that the forensic reanalysis of a Duke cancer-genetics study by Baggerly and Coombes took roughly 2,000 hours, and that Amgen reproduced 6 of 53 landmark preclinical cancer studies. It advises scripting the analysis so it can be tested on known input, following the published Ten Simple Rules for reproducible computing, and posting data and code in repositories such as Dryad or Figshare.

## Detecting and limiting it

- Compare each study's power with the share of positive results; Francis applied this to Bem's psychic experiments (2011).
- Register protocols publicly, document deviations, follow reporting guidelines (CONSORT, STROBE, ARRIVE) and publish negative results.

## Limits

- No data of its own in either chapter.
- Reinhart's footnote warns that the power comparison presumes every study is estimating one common effect.
- Registration and sharing figures date from 2008-2012; chapter 10's Reproducibility Project results were preliminary and have since been published, and its tooling advice (Sweave, IPython Notebook) has dated.

## See Also
- [[Researcher Degrees of Freedom and Prespecification]] — related
- [[Winner's Curse]] — related
- [[Multiple Comparisons Corrections]] — related
