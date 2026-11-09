---
title: InfCode Adversarial Test-Patch Refinement
tags: [harness, pattern]
summary: An issue-resolution pipeline where a test generator and a code generator iterate against each other, then a selector agent filters candidate patches by running them; reports 79.4% on SWE-bench Verified, with the test generator's drift conceded.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2025-infcode.md
---

# InfCode Adversarial Test-Patch Refinement

InfCode (Li et al., Beihang University and Beijing Tokfinity, a November 2025 preprint) resolves software issues inside a per-issue Docker container in two stages.

## Mechanism

- **Stage 1, adversarial loop:** a test generator and a code generator alternate. When the code passes the tests, the test agent adds harder ones. The loop ends at a hard iteration cap (the value is never stated) or immediately if the strengthened tests still pass. The aim is to make the scorekeeper something the loop improves.
- **Stage 2, selection:** a selector agent reads all candidate patches with their test patches, may execute them in the container, and drops those that are overfitted or unstable. Criteria are named only generally: functional correctness, coverage, execution success and repository compatibility.
- **Guard:** any file whose name starts with "test" is left out of the diff that gets evaluated, so an agent cannot weaken its own checker.

## Results (self-reported)

- With Claude 4.5 Sonnet on SWE-bench Verified: 79.4% (397 issues), first place on the leaderboard as of 14 November 2025, ahead of TRAE with Doubao-Seed-Code at 78.80%. Only five other entries are compared, with no cost or run count.
- SWE-bench Lite (300 issues) with DeepSeek-V3, one configuration per row: full 40.33% (121), without adversarial iteration 36.33% (109), without selection 32.33% (97). Selection mattered more than the loop.
- Against baselines on Lite: 40.33% at 0.26 dollars per issue versus KGCompass 36.67% (110) at 0.20 and Agentless with GPT-4o 32.00% at 0.70. Baselines came from their own papers or the leaderboard, with mixed backbones.
- Average tool calls per solved problem: Bash about 302.6 (61.0%), editor 167.01, searcher 22.06, submitter 4.74. The paper does not say which model or dataset this was measured on.

## Limits

- Inconsistent figures: in the text InfCode on DeepSeek-V3 solves 118 problems, while Tables 1 and 2 give 121 (40.33%); the text's "11 more than KGCompass" matches 121. Cite 121.
- The authors concede the test generator sometimes writes tests that deviate from the issue to induce failures, which misleads the code generator; this is not quantified.
- One run per cell, no confidence intervals, no ablation of test quality, and the selector's criteria get only a loose description. The construct-validity section claims cross-validation over independent test generations that does not appear in the results.
- Only Python benchmarks were evaluated; language generality is asserted. The leaderboard rank is dated.

## See Also

- [[Verification Loops]] — prerequisite-for
- [[Three-Layer Termination Check]] — related
- [[Proposer-Reviewer and Sidecar Gating]] — related
- [[AlphaCodium Flow Engineering]] — related
- [[Agentless Localize-Repair-Validate]] — alternative-to
