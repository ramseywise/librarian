---
title: LLM-as-a-Verifier
tags: [eval, pattern]
summary: "Instead of reading the single score token a judge emits, take the probability-weighted expectation over its score-token logprobs, which removes ties between candidates; on Terminal-Bench V2 trajectory pairs one such verifier pass scored 74.7% pairwise accuracy against 71.8% for a discrete judge, and best-of-N selection with it recovered part of the gap to an oracle (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-kwok-2026-llm-as-verifier.md
---

# LLM-as-a-Verifier

Kwok et al. (arXiv 2607.05391, 2026) build a verifier from a prompted LLM that is asked to
rate a candidate (or a pair of candidates) on a fine integer scale. Rather than keeping the
token the model picks, the verifier reads the probabilities over every score token and
averages the scores weighted by them. A discrete judge that outputs one number often gives two
candidates the same number; the expectation almost never does.

## The mechanism

- **Granularity (G).** The score scale has G levels; the paper's main setting is G = 20.
- **Repetition (K).** The expectation is averaged over K passes.
- **Criteria (C).** The rating is repeated for several separately worded criteria (the
  paper uses three: Specification, Output, Errors) and averaged.
- **Pairwise form.** Two candidates are scored in one prompt, and the difference of their
  expected scores is turned into a win probability with a logistic function, in the
  [[Bradley-Terry Preference Model]] style.
- **Probabilistic Pivot Tournament.** To pick the best of N candidates without comparing all
  pairs, k pivot candidates are used, at O(Nk) cost (N + k(N−k) + C(k,2) pairs); the extraction
  does not describe how the remaining candidates are ranked. A ring pass shows every candidate in both prompt positions, first and second; the authors say
  this cancels position bias, though they do not measure it.
- **Models without logprobs.** A closed model writes the reasoning and an open model with
  accessible logits does the scoring.

## Results (self-reported)

- **Ties and accuracy.** The verifier is Gemini 2.5 Flash at G = 20, and the benchmark is
  Terminal-Bench V2. Pairwise accuracy (a correct run must outscore a failed one on the same
  task, ties counting half) on 200 sampled trajectories was 74.7% at K = 1 rising to 77.5% at K = 16. A discrete judge scored
  71.8%, 74.4% and 74.7% at K = 1, 4 and 16, with a tie rate falling from 26.7% to 5.5%; the
  verifier's tie rate was 0.0%.
- **One case study.** On a single trajectory pair (Opus 4.5 with OpenHands, 100 repeats), a
  discrete 1-5 judge produced 12 correct, 88 tied and 0 wrong verdicts; the verifier at G = 20
  produced 77, 0 and 23. Breaking the ties therefore also created wrong orderings that the
  judge had avoided.
- **Best-of-N selection.** Gemini 2.5 Flash scored with G = 20, K = 8 and three criteria, ranking
  by pivot tournament. On Terminal-Bench V2 (N = 5) the pass rate moved from 83.1% to 86.5%, with
  an oracle at 92.1%. On SWE-Bench Verified (N = 3) it moved from 76.1% to 78.2% against an oracle
  of 84.4%, and on MedAgentBench (N = 5) from 70.2% to 73.3% against 75.0%.
- **Tournament cost.** On 89 Terminal-Bench V2 tasks with 20 trajectories each, k = 3 pivots
  scored 66.17% on 4,723 pairs against 67.42% for a full round-robin on 13,111 pairs.
- **Video.** With Qwen 3.6 35B at G = 20 and K = 8 over 500 RoboRewardBench pairs, the verifier scored
  87.4% against 70.8% for the discrete judge and 81.4% for the trained RoboReward-8B.
- **Dense reward.** As an RL reward it gave about 1.8x better sample efficiency on LIBERO
  (5 seeds) and about 1.1x on MATH (3 seeds).

## Limits

The method needs access to score-token logits, and its criteria are written by hand; the RL
experiments are single-turn. The paper reports no cost or latency for its pairwise scoring setup, and the leaderboard claims
place selection among 3 or 5 runs beside single-run entries, so compute is not matched. Gains of a few
points rest on n = 200 with no confidence intervals, all scaling ablations use one verifier on one
benchmark, and self-preference bias and agreement with human raters were not tested. The
authors note that repetition gains shrink on harder examples, which they attribute to
correlated biases. Model names and leaderboard positions are a mid-2026 snapshot.

## See Also
- [[GPTScore]] — alternative-to (another scorer built on model probabilities)
- [[LLM-as-Judge Evaluation]] — extends (the discrete judge it is compared against)
- [[LLM Judge Biases]] — related (position bias and the ring pass)
- [[Verification Loops]] — related (a learned score used to pick among candidates)
- [[Best-of-k Headline Inflation]] — related (selection over several attempts versus a single run)
- [[Self-Consistency]] — related (repetition as a way to pool answers)
- [[Universal Verifier for Computer-Use Agents]] — alternative-to (rubric-based verifier for computer-use trajectories)
- [[VeriHarness Agentic Verification]] — related
- [[Team of Rivals Critic-Veto Orchestration]] — related
- [[Code-Based Self-Verification and Weighted Voting]] — related
