---
title: Researcher Degrees of Freedom and Prespecification
tags: [data-analytics, probability-and-statistics, concept]
summary: "Choosing measures, covariates, exclusions and stopping points after seeing the data inflates false positives even without intent; plan the analysis first, register it, analyse blind where possible and replicate before publishing."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch09-researcher-freedom-good-vibrations.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch12-what-can-be-done.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch15-horoscopes.md
---

# Researcher Degrees of Freedom and Prespecification

Researcher degrees of freedom are the analyst's open choices: which measures, covariates, exclusions, groupings, missing-data handling and sample size. Reinhart's chapter 9 argues that because those choices are made after seeing the data, standard errors and intervals are biased and false positives inflated, without any intent to cheat.

## What the chapter reports

- Simulations he cites show that varying the adjustment variables, the excluded cases and the outlier handling can alter effect sizes twofold.
- Keeping at it with different covariate sets and sample sizes until one works can lift the false positive rate past 50% on a given dataset.
- In a music study he cites, 20 undergraduates were randomly given one of two songs. After optional stopping and covariates chosen post hoc (father's age was controlled), those hearing "When I'm Sixty-Four" came out 1.5 years younger than those hearing "Kalimba" (p < 0.05), an effect that cannot be real.
- A large replication attempt turned up nothing for the claims linking ovulation to clothing choice or to political attitudes; Gelman criticised the original for its many degrees of freedom.
- A single scientific hypothesis can be tested many statistical ways (a dozen possible side effects; red, pink or other clothing); counting any hit as support inflates false positives.

## Remedies

- Write the analysis plan before data collection, naming the effects sought and allowing for multiple comparisons; register trial protocols, and state any departure from the plan.
- Blind analysis, in which the value of interest stays uncomputed until the method is final: conceal it, shift it by a hidden constant, divide the work among independent groups, or add fake data and strip it out later. Triple blinding keeps patients, doctors and statisticians ignorant of who is the control group.
- Replicate before publishing: gather fresh independent data and apply identical methods.
- If the plan turns out to be wrong, fix the analysis and say so openly.

McElreath (Statistical Rethinking ch. 15) gives an openness workflow for individual researchers: pre-plan the research with its analysis, draft it as a dry-run analysis fit to show a colleague, register it publicly, collect the data, analyse as planned, document and justify any changes, and put data and scripts online. He frames this as the part a researcher controls, among eight dynamics of scientific discovery that generate error (his own unranked list, from theory quality through replication and meta-analysis).

Chapter 12 adds a reading checklist for papers: how power or sample size was set, how variables were selected, effect sizes with intervals, multiple-comparison corrections and stopping rules. It also advises planning with a statistician before collecting data, as a collaborator and not a replacement for Excel.

## Limits

- No data of its own; each quantitative claim comes from footnoted work not in the extract.
- Fixing the plan first is not always feasible or correct: distributional and outlier assumptions may prove wrong, and some data, such as a market crash or cancer patients, cannot be collected again.
- Blinding methods for common statistical methods need more methodological research, and triple blinding does not remove all bias.
- McElreath's ch. 15 is a three-page essay with no data: every figure is an assertion or a quoted opinion, footnotes 169-184 are absent, and the list of eight dynamics is his own, unranked.
- Journal policy descriptions in chapter 12 date from 2013-2014.

## See Also
- [[Multiple Comparisons Corrections]] — prerequisite-for
- [[Double Dipping and Selection on the Test Data]] — related
- [[Publication and Outcome Reporting Bias]] — related
- [[Peeking and Sequential Testing]] — related
