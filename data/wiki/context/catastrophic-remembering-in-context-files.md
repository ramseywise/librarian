---
title: Catastrophic Remembering in Context Files
tags: [context, concept]
summary: "Agent instruction files such as CLAUDE.md grow monotonically in the wild (+226% over a file's life, 1,867 repos), and a simulated study finds that annotating edits with notes to the next maintainer cuts the excess growth sharply; the fix was never tested on a real file."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chakrabarti-2026-why-does-claude-md-keep.md
---

# Catastrophic Remembering in Context Files

The paper names a failure it calls catastrophic remembering: an LLM-maintained instruction file keeps accumulating rules because the maintainer cannot see why an old rule exists, so deleting it looks risky. Contrast with catastrophic forgetting.

## Observational data (1,867 repositories)

- Across 247,694 tracked instruction lifetimes, a file's instruction count rises 226% over its life (self-reported, repository analysis). The median last version holds 39 instructions (90th percentile 131). Files gain 4.9 instructions per commit on average over 19,267 commits (self-reported, same analysis). Among repositories with multiple versions (n=1,576), 64.3% grew and 26.6% shrank (self-reported).
- The hazard of deletion falls with an instruction's age (slope -0.032 per commit, 95% CI -0.047 to -0.019; self-reported, repository analysis). 77.3% of deaths happen in rewrites or migrations; a rewrite cuts a file to 59.5% of its size, and within 10 commits the file regrows to 91.5% of its prior size (all self-reported, repository analysis).

## Controlled study (simulated)

An inverted IFEval loop with claude-haiku-4-5 as both maintainer and executor, where each history rewrites a prompt over time.
- At 15 steps (552 histories, 3 seeds), excess size is +60.4% with no comments, -5.8% with informative "prompt comments" (notes addressed to whoever maintains the file next, removed before the executor reads the prompt) and +53.2% with comment-shaped noise (self-reported, simulated loop).
- At 51 steps (184 worlds, one seed), +211.3% falls to +1.4% (self-reported, simulated loop). A narrative of past attempts without outcomes was the worst arm (+70.0%, self-reported, same loop).
- On WildIFEval (64 worlds, 16 distractors), satisfaction rises from 50.4% to 62.0% (+11.6 points, CI 5.1 to 18.3); a second judge gives +7.8 (all self-reported, simulated loop).

## Limits

- The loop is synthetic, where covers hold 2 to 3 instructions, far below the real median of 39, one small model, and single-seed long-horizon tables. The effect appears only in a tuned regime of five conditions found by search, and vanishes (+3.0%) if the verifier's specification is disclosed. About one prompt in eight ends up empty under the protocol, so a person should stay in the deletion path.
- Evaluation uses an LLM judge. The repository analysis is observational (matcher validated on 50 annotated transitions). The comment mechanism was never tested in a real CLAUDE.md.
- The paper quotes 76.8% for the rewrite-or-migration share on one page and 77.3% in Section 3.2.

## See Also
- [[Context Failure Modes]] — prerequisite-for
- [[Measuring Fixed Context Overhead]] — related
- [[Context Compaction]] — related
- [[Bad Memory File-Based Prompt Injection]] — related
- [[AGENTS.md Context File Evaluation]] — related (measured effect of repository context files on task success)
