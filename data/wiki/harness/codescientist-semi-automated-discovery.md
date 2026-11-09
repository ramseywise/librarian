---
title: CodeScientist Semi-Automated Discovery
tags: [harness, pattern]
summary: "CodeScientist generates ideas from papers and code blocks, runs experiments, and relies on external reviewers plus a vetoing expert; the denominators matter, because 6 surviving discoveries came from 250 runs on 50 human-picked ideas."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-jansen-2025-codescientist.md
  - data/raw/papers/2026-11-06-jayaram-2026-towards-automating-scientific-review-google.md
---

# CodeScientist Semi-Automated Discovery

CodeScientist (Jansen et al., Allen Institute for AI, March 2025) builds ideas from a set of 57 papers on agents and virtual environments and ten reusable code blocks, with a base model of Claude Sonnet 3.5. A human picks the ideas to run.

## The denominators (self-reported)

About 2,000 ideas were generated, 50 were chosen by humans, each had five experiment attempts (250 runs), 19 ideas were flagged because at least one run was interesting, 13 passed three external reviewers, and 6 passed the internal expert as well (32% of the 19). The internal reviewer acted as a veto, reading code and logs and re-running with more samples. Only 41% of runs finished successfully; 32% hit the debug limit and 18% the time limit.

## Why the expert rejected discoveries

The paper gives reasons: baselines or models too simple (6), an effect that vanished with more samples (3), major implementation errors (2), too little detail (1).

## A review-side companion

Google's Paper Assistant Tool (Jayaram et al., June 2026) defines four roles for AI in peer review by analogy with vehicle autonomy levels: a tool for authors, a tool for reviewers, a supporting reviewer, and full automation. On 26 papers with 29 equation or proof errors, its multi-stage pipeline found 89.7% against 55.2% for zero-shot Gemini 3.1 Pro (self-reported; an author audited an LLM grader). It was piloted with authors only, on over 4,700 submissions across two conferences; only about 55.8% and 64.8% of survey respondents found the feedback mostly grounded.

## Limits

- CodeScientist's Table 4 caption says 11 rejected while 13 are listed, and the reason counts sum to 12.
- The extraction did not read the appendix experiment reports line by line, and the internal reviewer was an author.
- The review-tool figures use a different grader from the original benchmark, so they are not comparable; the survey is self-selected with no control group; and the abstract's "34%" is a percentage-point gap.

## See Also
- [[Deep Research Agent Systems]] — prerequisite-for
- [[Loop Autonomy Ladder]] — related
- [[Paper-Replication Completion Gate]] — related
- [[Proposer-Reviewer and Sidecar Gating]] — related
- [[AI Scientist Automated Research Pipeline]] — related
