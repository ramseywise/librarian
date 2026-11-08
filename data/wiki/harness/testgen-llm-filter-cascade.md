---
title: TestGen-LLM Filter Cascade
tags: [harness, pattern]
summary: Meta's test-generation tool passes LLM-written unit tests through three deterministic filters (builds, passes five repeated runs, adds coverage) before any engineer sees them; reported at Instagram and Facebook with a 73% acceptance rate.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-alshahwan-2024-automated-unit-test-improvement-using.md
---

# TestGen-LLM Filter Cascade

TestGen-LLM (Alshahwan et al., Meta, FSE 2024) generates Kotlin unit tests for Android code with two internal LLMs and keeps only what survives a chain of filters, applied per test case. A test must build, then pass on every one of five repeated executions (a test failing any run is deemed flaky), then raise line coverage as measured by Jacoco. Anything that fails a filter is discarded. The filters are deterministic scripts, so the gate does not depend on the model grading its own output. Per-test filtering replaced class-level checks after reviewers found a landed diff holding four tests that were only superficially different; a filter checking test bodies for syntactic equality was introduced after generated tests turned out to be near-verbatim copies or very different.

## Results (self-reported unless noted)

- Controlled evaluation on 86 Kotlin components of Instagram Reels and Stories, four prompts, two LLMs: 75% of test classes had a new test that builds, 57% had one that also passes reliably, and 25% had one that also increases line coverage. An ensemble helped: LLM1 found 13 tests (15% of files) and LLM2 found 16 (19%).
- Deployment across three test-a-thons (29 October to 29 December 2023): 196 of 1,979 classes improved, which the body calls about 10% and the abstract 11.5%. Engineers accepted 73% of recommendations, which the paper compares with 50% for an earlier Meta repair deployment (a different task).
- Per-attempt yield is low: 831 of 23,535 trials on Instagram and 490 of 8,996 on Facebook, which makes the pipeline one of producing many candidates and then filtering.
- Acceptance by run: 36 of 42 diffs (Instagram December), 144 of 280 (Facebook December); 61 of the Facebook diffs received no review.
- Temperature: the text reports about 4% success at 0.0, 0.2 and 0.5 and sets the default to zero.
- Median coverage gain per landed test in the first test-a-thon was 2.5 lines.
- Reviewers rejected tests for reasons the filters cannot detect: a test that ran a previously unexecuted method but had no assertion passed the coverage filter and was rejected by the reviewer.

## Limits

- Line coverage is a proxy for improvement (the authors say so); branch and mutation coverage were not feasible at scale. The filters check validity and coverage, not that an assertion is correct.
- Internal, undisclosed 2023 models; experience report with no ablation against an unfiltered baseline and no bug-finding or mutation measure. Test-a-thons are not a typical diff-time setting. No retry loop yet.
- Internal inconsistencies in the paper: the abstract says 11.5% where the body says about 10%; the text says about 4% success at every temperature while Table 4 shows 0.01 per trial at 0.2 and 0.5.
- Deployment samples are unbalanced (LLM2 and temperature 0 dominate) and coverage accumulates, confounding the temperature results.

## See Also

- [[Verification Loops]] — prerequisite-for
- [[Three-Layer Termination Check]] — related
- [[AlphaCodium Flow Engineering]] — related (also generates extra tests to gate a solution)
