---
title: Experiment Ramps and Overlapping Tests
tags: [foundations, pattern]
summary: "A platform assigns users with a salted cryptographic hash per experiment layer so many tests overlap independently, ramps traffic from tiny shares because a catastrophe needs far less data than a planned effect, and audits the portfolio because winners' summed lifts overstate what shipped."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
  - data/raw/papers/2026-11-06-kohavi-2008-controlled-experiments-web.md
---

# Experiment Ramps and Overlapping Tests

## Assignment by salted hash

Assignment must be random, stable per user and independent of other tests. Hash the user id with a per-experiment salt and take the result modulo the number of arms. There is no assignment table, a returning user lands in the same arm, and a new salt produces a fresh, independent split. In a simulated check, two salts gave independent splits (chi-square p 0.867) with an interaction estimate of -0.052 (p = 0.59) when the true interaction was zero. Quality of the hash matters: in a published test of hashes over a million sequential ids, only a cryptographic hash passed, and weak hashes correlated experiments. Test your hash.

## Overlap and layers

Tests must overlap or traffic runs out. Layered design puts a user in one test per layer, with independent salts across layers, and keeps tests on the same parameters in the same layer. Large interactions are possible but rarer than feared, so monitor them rather than queue all tests; an interaction's standard error is twice a main effect's in a balanced design. Queuing loses more in throughput than interactions usually cost.

## Ramps

Start with a sliver of traffic to catch disasters, then widen in steps (0.1%, then 0.5%, 2.5%, 10% and finally 50%). Needed sample size shrinks with the square of the effect, which makes a catastrophe cheap to spot. At 4,000 users a day, a 20% drop (delta 0.01 on a 5% base) needs 7,600 per arm, which is 3.8 days with an even split; the planned +10% needs 30,400 per arm, 15.2 days. A bug causing a 20% drop shows up in roughly one four-hundredth of the time a planned 1% change would need. A platform can abort automatically when a metric crosses a threshold. End the ramp at an even split: a 99/1 allocation would run about 25 times longer ([[A/B Test Lifecycle and Interval Decisions]]).

## The portfolio

Across many tests, selecting on significance inflates winners ([[Winner's Curse]]). In a simulation of 200 experiments (about 30% with a real effect, standard error 0.35), 19 shipped; the summed measured lift was 18.6 against a true 9.2, and 37% of shipped changes had zero effect. Finance adding up reported lifts therefore exceeds real growth. Mature platforms keep a long-running holdout, shrink estimates ([[Small-N Trap and Shrinkage]]), control false discoveries ([[Multiple Comparisons Corrections]]) and rerun borderline wins: one OEC win at p = 0.029 did not reproduce at double the traffic.

## Practical-guide findings (Kohavi et al., 2008)

The authors' survey of web controlled experiments adds operational detail. Results here are their own reports (self-reported), several second-hand.

- **Hash test.** With five simulated experiments over one million sequential user ids and chi-square interaction tests, only MD5 showed no cross-experiment correlation. SHA256 came close (a five-way interaction was needed to expose correlation). Other hashes, including a common string hash, failed a two-way test. Seeding a random generator per request and caching then XOR-ing hashes both induced severe correlation.
- **Randomisation requirements:** equal assignment probability, consistent assignment across a user's visits, and no correlation between experiments; monotonic ramp-up and an external control are optional extras.
- **A/A tests.** Run them continuously to confirm the allocation matches the plan, that logged data agrees with the system of record, and that 95% of runs show no significant difference. Robots that accept cookies (examples up to 7,000 clicks in an hour) inflate variance and can push A/A false positives well above 5%, so filter them.
- **Auto-abort.** Dropping an underperforming treatment's share to zero automatically.
- **Choose the OEC in advance** as a planned comparison to avoid familywise error; include long-term predictors such as repeat visits, not only clicks.
- **Latency.** Reported effects of slowing pages (some second-hand): Amazon, 100 ms for about 1% of sales; Microsoft Live Search, one second for 1% of queries per user and 1.5% of ad clicks per user, two seconds for 2.5% and 4.4%.
- **When user-level randomisation fails:** an incentive that affects all items (eBay's first-bidder case), price tests, and search-engine or robot tests, where item or page is the better unit.
- **Multivariate designs.** A full factorial of five two-level factors has 32 groups; an eight-group fractional design confounds all interactions with main effects. They prefer concurrent independently randomised one-factor tests, say large interactions are less common than expected (an assertion), and say the first experiment should be a simple A/B test.
- **Assignment mechanisms.** Traffic splitting, page rewriting, client-side JavaScript and server-side API calls trade intrusiveness against generality. They flag a client-side shortcut that skips the call for Control as incorrect, because it ties render delay to assignment.

The paper does not cover sequential testing, sample ratio mismatch by name, variance reduction or interference beyond a few examples.

## LLM features

An LLM prompt change is an experiment with the same machinery: user or conversation as unit, task success or retention as OEC, cost and latency as guardrails, offline graders as a sensitive proxy that must be validated.

## See Also
- [[Sample Ratio Mismatch]] — related (a reused salt or correlated hash shows up as SRM)
- [[Interference and Cluster-Randomised Experiments]] — related
- [[OEC, Guardrails and North Star Metrics]] — related
