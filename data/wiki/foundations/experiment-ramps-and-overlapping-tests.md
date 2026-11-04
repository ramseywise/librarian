---
title: Experiment Ramps and Overlapping Tests
tags: [foundations, pattern]
summary: "A platform assigns users with a salted cryptographic hash per experiment layer so many tests overlap independently, ramps traffic from tiny shares because a catastrophe needs far less data than a planned effect, and audits the portfolio because winners' summed lifts overstate what shipped."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--01-ab-testing.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# Experiment Ramps and Overlapping Tests

## Assignment by salted hash

Assignment must be random, stable per user and independent of other tests. Hash the user id with a per-experiment salt and take the result modulo the number of arms. There is no assignment table, a returning user lands in the same arm, and changing the salt gives a fresh independent split. In a 60,000-user check, two salts gave independent splits (chi-square p 0.867) with an interaction estimate of -0.052 (p = 0.59) when the true interaction was zero. Quality of the hash matters: in a published test of hashes over a million sequential ids, only a cryptographic hash passed, and weak hashes correlated experiments. Test your hash.

## Overlap and layers

Tests must overlap or traffic runs out. Layered design puts a user in one test per layer, with independent salts across layers, and keeps tests on the same parameters in the same layer. Large interactions are possible but rarer than feared, so monitor them rather than queue all tests; an interaction's standard error is twice a main effect's in a balanced design. Queuing loses more in throughput than interactions usually cost.

## Ramps

Start small, check for disasters, then expand to full power: 0.1%, 0.5%, 2.5%, 10%, 50%. Sample size falls with the square of the effect, so a catastrophe is cheap to see. At 4,000 users a day, a 20% drop (delta 0.01 on a 5% base) needs 7,600 per arm, 3.8 days at 50/50; the planned +10% needs 30,400 per arm, 15.2 days. A bug causing a 20% drop is visible in about 1/400 of the time needed to detect a planned 1% change. A platform can abort automatically when a metric crosses a threshold. End the ramp at 50/50: a 99/1 split needs about 25 times the running time ([[A/B Test Lifecycle and Interval Decisions]]).

## The portfolio

Across many tests, selecting on significance inflates winners ([[Winner's Curse]]). In a simulation of 200 experiments (about 30% with a real effect, standard error 0.35), 19 shipped; the summed measured lift was 18.6 against a true 9.2, and 37% of shipped changes had zero effect. Finance adding up reported lifts therefore exceeds real growth. Mature platforms keep a long-running holdout, shrink estimates ([[Small-N Trap and Shrinkage]]), control false discoveries ([[Multiple Comparisons Corrections]]) and rerun borderline wins: one OEC win at p = 0.029 did not reproduce at double the traffic.

## LLM features

An LLM prompt change is an experiment with the same machinery: user or conversation as unit, task success or retention as OEC, cost and latency as guardrails, offline graders as a sensitive proxy that must be validated.

## See Also
- [[Sample Ratio Mismatch]] — related (a reused salt or correlated hash shows up as SRM)
- [[Interference and Cluster-Randomised Experiments]] — related
- [[OEC, Guardrails and North Star Metrics]] — related
