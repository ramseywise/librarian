---
title: Bayes Rule and the Base Rate Fallacy
tags: [data-analytics, probability-and-statistics, concept]
summary: "P(A|B) and P(B|A) share a numerator but not a denominator; Bayes' rule converts between them through the base rate, which is why a 99 percent accurate test of a rare event is mostly false positives and why a significant p-value is often a dud."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--02-probability-foundations.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch04-p-value-base-rate-fallacy.md
  - data/raw/papers/2026-11-08-think-bayes-ch01-bayess-theorem.md
  - data/raw/papers/2026-11-08-think-bayes-ch02-computational-statistics.md
  - data/raw/papers/2026-11-08-think-stats-ch05-probability.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch03-sampling-imaginary.md
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

## Other worked cases (Reinhart, chapter 4)

- Mammogram screening (prevalence 0.8%, test power 90%, false positives in 7% of healthy women): among 1,000 women only 7 of the 77 positive results are real, roughly a 9% chance of cancer after a positive.
- His drug-screening example (100 candidates, 10 effective, power 0.8, alpha 0.05) counts 5 false positives and 8 true ones, a false discovery rate of 38%; the table above uses 4.5 false detections and so differs slightly.
- A 1992 telephone survey implied as many as 2.5 million defensive gun uses, set against about 65,000 a year from the National Crime Victimization Survey (both as cited). His arithmetic: if 2% of non-users answer yes by mistake, a true 0.1% rate among 99.9% non-users shows as nearly 2.1%.

## Bayes table, small examples (Downey, Think Bayes ch. 1-2)

Downey lays out hypotheses with prior, likelihood, their product and the normalised posterior; the data's likelihood decides the result, so recompute it when the data-generating process changes.
- Cookie problem: Bowl 1 holds 30 vanilla and 10 chocolate, Bowl 2 holds 20 of each, bowl chosen at random. After drawing a vanilla cookie, the chance of Bowl 1 rises from 1/2 to 3/5.
- M&M problem: 1994 mix 20% yellow and 10% green; 1996 mix 14% yellow and 20% green; one M&M is drawn from each of two bags, a yellow one from the 1994 bag and a green one from the 1996 bag; the posterior for hypothesis A is 20/27.
- Monty Hall: if Monty picks uniformly between the two other doors when the car is behind your door, switching wins 2/3. If he always opens B whenever he can, seeing B opened leaves 1/2 and 1/2.

## A drug-test case (Downey, Think Stats ch. 5)

With sensitivity about 60%, specificity about 99% and a 5% base rate of users, P(user given a positive) = 0.76, meaning about a quarter of positive tests come from non-users. The same chapter has a Monty Hall puzzle (switching wins 2/3) and suggests simulating the random process with Monte Carlo to see if an apparent streak or cluster signifies anything.

## Vampire test and toy science (McElreath, Statistical Rethinking ch. 3)

A vampire test detects 95% of vampires and falsely flags 1% of mortals; prevalence is 0.001. A positive gives an 8.7% chance of vampirism. In natural frequencies: of 100,000 people, 100 are vampires and 95 test positive, while 999 of the 99,900 mortals do too, so 95 of 1,094 positives are real. He advises presenting base-rate problems as counts. The same arithmetic for science: with power 0.95, a 5% false-positive rate and 1 true hypothesis in 100, a significant finding means about a 16% chance the hypothesis is true; cutting the false-positive rate to 1% lifts that only to around 0.5.

## Failure modes

- Quoting accuracy without prevalence.
- Multiplying evidence that is not independent.
- Reading P(buy | desktop) > P(buy | mobile) as what a device switch would do: it describes populations, not interventions.

## Limits

- Reinhart's chapter 4 arithmetic uses assumed rates, his survey figures come from endnotes not in the excerpt, and Benjamini-Hochberg does not remove the base-rate problem.
- Think Bayes ch. 1-2 is textbook level (2012 first edition, Python 2 code) and reports no empirical results or timings.
- Think Stats notes Monte Carlo is slow for rare events.
- The Rethinking figures are toy illustrations with assumed rates, not measured data.
- The Think Stats drug-test sensitivity and specificity are 1990s-era JAMA estimates, cited through Gleason and Barnum.

## See Also
- [[P-Value Misreadings]] — related (the same inversion applied to p-values)
- [[Independence Pitfalls]] — prerequisite-for (the independence needed to chain evidence)
- [[Winner's Curse]] — related (low base rate and low power compound)
- [[Eval Error Bars and Sample Size]] — related (judge and classifier rates need the same accounting)
- [[Beta-Binomial Updating and Credible Intervals]] — extends
- [[Bayes Factors and Composite Hypotheses]] — extends
