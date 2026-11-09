---
title: Oracle-Gap Recovery by Selection
tags: [loop, concept]
summary: "In sample-and-select loops the cap on gains is the selector, not the sampler: one study recovers 78.3% of the gap to an oracle on SWE-bench Verified, and a second shows that selecting on the test score instead of validation inflates medal rates by 9 to 17 points."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-sunkaraneni-2026-inference-time-amplification-weak-reasoning.md
  - data/raw/papers/2026-11-06-toledo-2025-ai-research-agents-machine-learning.md
---

# Oracle-Gap Recovery by Selection

A loop that samples k candidates and keeps one has an upper bound, the oracle that picks the best of k, and a lower bound, the first sample. Sunkaraneni et al. (2026) define oracle-gap recovery as (system score minus pass@1) divided by (oracle@k minus pass@1) and use it to ask how much of the exposed capability a selector recovers. Toledo et al. (2025) ask what happens when the selector reads the wrong score.

## Findings (self-reported)

- **Recovery.** On SWE-bench Verified (500 tasks, a GPT-5.4 nano agent, k=8, hidden tests never shown to the selector), a critic-gated pairwise comparator moved the solve rate from 67.0% to 76.4% against an oracle of 79.0%, a recovery of 78.3%. The paper attributes 89.0% of the residual failures to proposals (no correct candidate in the pool) and 11.0% to selection.
- **Evidence helps the judge.** On a Qwen3.6-27B pool, giving the comparator repository access as well as the patch raised recovery from 24% to 40%, with judgment latency rising from 178 to 739 seconds.
- **A sound cheap check beats a learned judge.** On Blocksworld a simple verifier and a learned committee both reached 99.0%, the verifier with 6.3 times fewer tokens.
- **A misaligned judge hurts.** On CommonGen a judge that did not match the task rule took the score from 80.5 to 73.0, below doing nothing.
- **Selecting on test data inflates results.** On MLE-bench Lite with DeepSeek-R1 agents (24 hours, 20 seeds), using the test score instead of validation for search and selection raised the medal rate for four search strategies, by 9.4, 12.4, 15 and 16.6 absolute points respectively. Most of the gap came from final-node selection. The gap grows with run time, and the AIRA operators narrowed it.
- **Ranking noise.** The authors recommend at least 10 seeds per task, 20 preferred, and show that gaps of 2 to 5 points between search policies fall within the seed noise at fewer seeds.

For loop design this puts the investment on the verifier and on honest held-out scoring before it goes into more samples; compare [[Best-of-k Headline Inflation]] for the reporting side and [[Verification Loops]] for the harness side.

## Limits

- The 78.3% result is one agent and one benchmark; recovery varied by proposer pool (27% to 69% on SWE pools) and by domain, and simple heuristics such as shortest patch were unstable across pools.
- The 76.4 headline comes from a different run than the 75.7 replay the paper uses elsewhere.
- Toledo: the extraction finds the 12.4-point figure does not match its own reconstruction from the bar labels (12.0), the abstract baseline is 39.6 in one place and 39.77 in another, divergence between policies is dated to 19 hours in the main text and 15 hours in an appendix, and a long run is 90 hours in the text and 120 in a caption.
- Both papers are preprints with no independent replication.

## See Also
- [[Best-of-k Headline Inflation]] — related
- [[Verification Loops]] — related
- [[LLM-as-Judge Evaluation]] — related
- [[AIRA Draft-Debug-Improve Search]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
