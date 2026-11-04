---
title: Bayes Rule and the Base Rate Fallacy
tags: [foundations, concept]
summary: "P(A|B) and P(B|A) share a numerator but not a denominator; Bayes' rule converts between them through the base rate, which is why a 99 percent accurate test of a rare event is mostly false positives and why a significant p-value is often a dud."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Bayes' Rule and the Base Rate Fallacy

P(A | B) is the probability of A once you know B happened: P(A and B) / P(B). Conditioning has direction, and swapping it is the commonest probability error. In simulated data, P(buy | mobile) was 3.8% while P(mobile | buy) was 45%: same numerator, different denominators. "45% of purchases are on mobile" says nothing about whether mobile users are good customers (mobile was 62% of users but 45% of purchases, which is the interesting reading).

## The inversion

```text
P(A | B) = P(B | A) P(A) / P(B)
P(B)     = P(B | A) P(A) + P(B | not A) P(not A)
```

```python
def posterior(prior, sensitivity, specificity):
    tp = prior * sensitivity
    fp = (1 - prior) * (1 - specificity)
    return tp / (tp + fp)
```

For a filter with 99% sensitivity and 99% specificity:

| Setup | P(event given flag) |
|---|---|
| prevalence 1 in 1,000 | 0.09 |
| prevalence 1 in 100 | 0.50 |
| prevalence 1 in 1,000, 99.9% accurate | 0.50 |
| 1 in 1,000, after two independent flags | 0.91 |

Of 10,980 flags in a million, 990 are real. Lessons: the answer depends on the base rate as much as accuracy; a better test must beat the base rate, so rare-event detection needs extreme specificity; and evidence accumulates, as yesterday's posterior becomes today's prior. The accumulation assumes independence: repeating the same test on the same item is not new evidence, and two checks sharing a blind spot are not two pieces of evidence.

## The same mistake in hypothesis testing

A p-value is P(data | no effect), commonly read as P(no effect | data). With 100 candidate ideas of which 10 work, 80% power and a 5% threshold, there are about 8 true and 4.5 false detections, so about 64% of significant results are real. P(real | significant) as a function of the share of tested ideas that are truly good:

| Base rate of real effects | P(real given significant) |
|---|---|
| 0.5 | 0.94 |
| 0.2 | 0.80 |
| 0.1 | 0.64 |
| 0.02 | 0.25 |

For a team that tests modest changes the base rate is usually low, so a win at p = 0.04 deserves suspicion. See [[P-Value Misreadings]] and [[Multiple Comparisons Corrections]].

## Failure modes

- Quoting accuracy without prevalence.
- Multiplying evidence that is not independent.
- Reading P(buy | desktop) > P(buy | mobile) as what a device switch would do: it describes populations, not interventions.

## See Also
- [[P-Value Misreadings]] — related (the same inversion applied to p-values)
- [[Independence Pitfalls]] — prerequisite-for (the independence needed to chain evidence)
- [[Winner's Curse]] — related (low base rate and low power compound)
- [[Eval Error Bars and Sample Size]] — related (judge and classifier rates need the same accounting)
