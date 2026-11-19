---
title: Self-Play SWE-RL (SSR)
tags: [llm, agent-training, pattern]
summary: "One policy plays bug injector and bug solver on bare Docker images, with bugs specified only by a test-weakening patch, trained jointly with RL; the paper reports gains on SWE-bench Verified and SWE-Bench Pro over a human-data RL baseline (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-wei-2025-toward-training-superintelligent-software-agents.md
---

# Self-Play SWE-RL (SSR)

Self-play SWE-RL (Wei et al., Meta FAIR and UIUC; arXiv v3 June 2026) trains a single model in two roles on the same repository images, with no human issues, no tests and no test commands supplied. The injector builds a bug; the solver repairs it. Both are trained together by RL.

## The bug artifact and the solver's spec

A bug is a bundle of five files: a test script, a list of test files, a test parser, a bug-injection diff and a test-weakening diff. The solver's only specification is the reverse of the test-weakening patch; there is no natural-language issue. The authors chose this because free-form issue text is hard to score automatically, and a run that self-synthesised issues collapsed.

Validity checks include test-file existence and coverage, parser and script validity, minimum counts of passing and failing tests and of changed files, and a check on the weakening patch. Inverse mutation testing requires every modified file to be necessary for triggering the bug. Higher-order bugs reuse a solver's failed patch as a fresh buggy state; they stop at second order to limit overlap with existing bugs.

Integrity measures: the `.git` directory is removed and recreated so history cannot leak, and before scoring the oracle test files are restored from an `ssr-original` tag, which means editing tests cannot win.

## Rewards

- Solver: +1 if all tests pass, -1 otherwise.
- Injector (adapted from Absolute Zero): -1 if consistency validation fails, -alpha when the solve rate s is exactly 0 or 1, and 1-(1+alpha)s for s between them; alpha is 0.8 and the group size is 8. Because alpha is below 1, degenerate-difficulty bugs still give gradient.
- With 8 samples the expected injector reward peaks at a unique interior solve rate near 0.2, so the opposing incentives push bugs toward the solver's frontier.

## Reported results (self-reported)

Setup: CWM-sft 32B base, 150 steps, SWE-bench Verified (500 tasks) and SWE-Bench Pro public (731), scored with one attempt per problem, sampling at temperature 1.0 and top-p 0.95, and no test-time scaling. The baseline RL run gets human issues, fail-to-pass and pass-to-pass tests and eval scripts, with the same images and hyperparameters.

- SSR gains +10.4 points on Verified and +7.8 on Pro, and stays above the human-data baseline throughout training. (The endpoint values 41.0 to 51.4 on Verified and 21.1 to 28.9 on Pro were decoded from a figure by the extractor and are unverified.)
- Ablations, scored as the average over all 1,231 tasks: injection-only training degrades; repair-only is worse than self-play; asking the model to inject bugs directly yields trivial one-line bugs and scores worst; removal alone does better, and removal combined with a history revert does best. Giving the injector a reward that includes solve rate improves only slightly on one that rewards consistency alone.
- Infrastructure: 512 H100s per run (64 for training and 448 for rollouts), 131,072-token context, 16M-token global batch, rollouts more than 8 off-policy steps old discarded, about 2.5B tokens.
- A theory appendix argues that once the challenger is strong enough, some strategies dominate and self-play stalls (random test failures, obfuscating the codebase, tuning one difficulty knob); suggested mitigations are grounding in real repositories and keeping the challenger close to its initial instruction-based behaviour.

## Limits

- One 32B base, one scaffold, 150 steps, one run per condition; the authors put evaluation noise near 2% (paired standard error) on Verified, so small gaps are within noise.
- Unit tests are the only verifier and the solver sees full oracle tests; the authors report no reward hacking and suggest splitting tests into public and private sets. A single policy plays both roles.
- At larger scale training became unstable and the model emitted gibberish; training on only 23 repositories did not beat many non-overlapping ones.
- Several authors work at Meta, which makes the CWM model, and the environment images are not released. The baseline is CWM-style RL, not other open SWE agents. The authors call the result early, with no claim about long-horizon tasks.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Multi-Agent Evolve Self-Play]] — related (another self-play loop)
- [[Repository-Level Coding Benchmarks]] — related
- [[Reward Hacking and Overoptimization]] — related (integrity measures against test editing)
- [[DAPO]] — related
