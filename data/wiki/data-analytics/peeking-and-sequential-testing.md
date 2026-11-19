---
title: Peeking and Sequential Testing
tags: [data-analytics, experimentation-and-causality, pattern]
summary: "Checking a fixed-horizon p-value repeatedly inflates false positives to 25% at 20 looks, so if people will look use group-sequential boundaries (O'Brien-Fleming, Pocock) or always-valid mSPRT p-values, which pay for looks with a stricter threshold."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch06-double-dipping-data.md
  - data/raw/papers/2026-11-08-bandit-algorithms-ch03-stochastic-processes-markov-chains.md
---

# Peeking and Sequential Testing

A p-value holds only at the planned sample size. If a test is halted as soon as the value falls under 0.05, the false-positive rate rises ([[P-Value Misreadings]]).

## How bad

With both arms at 10%, testing once gave 0.055; stopping at the first of 20 looks gave 0.250. Under the null with n_max 10,000, the false-positive rate by number of looks: 1 look 0.048, 2 looks 0.085, 5 looks 0.141, 10 looks 0.196, 20 looks 0.245, 100 looks 0.390, 1000 looks 0.524.

A ban on peeking fails as policy, because live dashboards are there to be watched and a harmful launch has to be stoppable. Two honest alternatives both pay for looks.

## Group-sequential boundaries

Decide how many looks there will be before starting, then give each look its own threshold. Calibrated to 5% overall over five looks:

- Pocock: constant z boundary 2.42 at every look. Stops moderate effects earlier, costs power at the end.
- O'Brien-Fleming: boundaries of 4.53 (first look), 3.2 (second), 2.61 (third), 2.26 (fourth) and 2.03 (fifth). Stops early only on enormous effects and ends near the fixed value 1.96; the usual choice.

A boundary that is 1.96 divided by the square root of the information fraction, uncalibrated, gave about 0.058, slightly above 5%. Published designs use tables or alpha-spending functions, which allow looks on unplanned dates.

## Always-valid p-values (mSPRT)

The mixture sequential probability ratio test divides the likelihood averaged over a normally distributed effect (variance tau squared) by the likelihood with no effect. Under the null this ratio has mean 1 and behaves as a martingale, so the chance it ever reaches 1/alpha is at most alpha; p = min(1/ratio) is valid at any stopping time. In simulation, checking after every pair of users gave a false-positive rate of 0.041. With a true effect of 0.05 sd, 98.2% of runs detected it within 20,000 pairs; the median run stopped at 5,897 pairs and the 90th percentile at 12,932, against 6,272 pairs for a fixed test with 80% power. So half the runs stop sooner, but the tail is long. Tau squared sets where the method is sharpest; choose it from effect sizes seen in past experiments.

## Reinhart's account

Chapter 6 shows the same effect in a simulation with no true difference: starting at 10 per group with 100 planned, testing after every added pair eventually gives p < 0.05. He cites more than half of surveyed academic psychologists saying they chose whether to gather more data once they had looked at significance, and trials stopped early overstating effects by 29% on average ([[Double Dipping and Selection on the Test Data]]).

## Choosing

- Test planned for weeks and reviewed weekly: group-sequential.
- Self-serve platform where people look whenever: always-valid.
- Either way keep whole weeks, and allow early stops for guardrail failure.
- A Bayesian posterior does not make peeking free either.

## Stopping-time results in Bandit Algorithms chapter 3

Chapter 3 of Lattimore and Szepesvari's Bandit Algorithms covers Doob's optional stopping theorem: for a martingale and a stopping time, E[X_tau] = E[X_0] if any one of three conditions holds (bounded tau; finite E[tau] with bounded conditional increments; a bounded stopped process), while super- and submartingales yield inequalities. Their Rademacher-coin gambler example says a fair gambler cannot turn the expected winnings positive through a stopping rule unless E[tau] is infinite. A non-negative supermartingale ever exceeds epsilon with probability at most E[X0]/epsilon, a sharpening of Markov's inequality, and a matching bound for finite-horizon non-negative submartingales is an exercise. The extraction's practice note is to test the three conditions first and reach for the maximal inequality when they fail.

## Limits

- Reinhart's 29% figure for early-stopped trials rests on a footnote not in the extract (chapter 6).
- The chapter names no sequential-analysis procedure to use instead.
- The Bandit Algorithms chapter is measure-theoretic background in discrete time with no testing or experiment content; its proofs are mostly left as exercises, and the authors themselves expect many readers to skip it initially.

## See Also
- [[A/B Test Lifecycle and Interval Decisions]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — related (repeated looks are multiple tests)
- [[Minimum Detectable Effect and Sample Size]] — prerequisite-for
- [[Experiment Ramps and Overlapping Tests]] — related
- [[Double Dipping and Selection on the Test Data]] — extends
