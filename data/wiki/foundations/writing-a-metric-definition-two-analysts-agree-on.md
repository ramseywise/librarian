---
title: Writing a Metric Definition Two Analysts Agree On
tags: [foundations, pattern]
summary: A metric definition fixes population, finality, window, clock, unit, owner and version in a spec that code reads; immature cohorts read as falls (censoring) and the function should return None rather than zero.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--11-metric-trees.md
---

# Writing a Metric Definition Two Analysts Agree On

A definition is precise when two analysts working apart get the same number. "Repeat rate for customers who joined in a year" shows five choices that decide it.

## Population and finality
Ever-repeat 46.5% vs 24.4% is unfair: the earlier cohort had an extra year. A 90-day rate over everyone, 30.4% vs 18.1%, is unfair the other way. Only customers with 90 days to watch give the honest comparison, 30.4% vs 20.2% (7,923 of 10,503). The most recent month's joiners show 4.6% (854 customers) as seen at period end: that is the calendar, not behaviour. This is right-censoring; see [[Survival Analysis for Customer Lifetimes]] for when you cannot wait.

## Window
"How many customers do we have?" has several defensible answers: 1,881 active in 30 days, 4,820 in 90, 13,825 in 365, 26,342 ever acquired. The choice follows purchase frequency ([[Per-User Metrics Depend on Window Length]]). A trailing 365 days is not a calendar year in a leap year: 1,264,983 vs 1,268,304 for the same year's revenue; both correct, never compare across.

## Clock
One month's revenue by order, dispatch or delivery date: 117,454, 113,807, 113,299; and 12.0% of December's orders (14,197) were delivered after year end, so later clocks keep changing.

## Unit
Conversion has one numerator and two denominators: 7.52% per session, 14.20% per visitor ([[Ratio Metrics and the Denominator Trap]]).

## Owner and version
Definitions change for good reasons; an unversioned number gets compared with its former self. Keep a frozen spec (name, version, question, population, numerator, denominator, clock, window, finality, owner) and have the function read it so code cannot disagree with the words. Check it with a hand-worked toy table (one of four mature rows counts; a same-day repeat and a day-151 repeat do not). Return None when nobody in the period is final: a 0% would read as a collapse. A 60-day window gave 24.5% and 15.6% for the two years: the level changes, so compare only like windows, which is why the version goes in the name.

## Semantic layer
A semantic layer stores one definition and serves it to every consumer, with metric types such as simple, cumulative, derived, ratio and conversion; a ratio type computes numerator and denominator as metrics and divides. It enforces answers but does not choose the population, clock or owner.

## Pitfalls
- Reporting an immature cohort as a fall: show only final customers or mark the rest provisional.
- Comparing across a definition change: version, and restate or break the line.
- Mixing a trailing window with a calendar period.

## See Also
- [[Metric Tree Decomposition]] — related
- [[Counter-Metrics, Guardrails and Goodhart Variants]] — related
- [[Cohort Retention Triangle]] — related
