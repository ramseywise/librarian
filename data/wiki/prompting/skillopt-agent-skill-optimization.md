---
title: SkillOpt Agent Skill Optimization
tags: [prompting, pattern]
summary: SkillOpt optimizes an agent's skill document as external state with weight-training controls, namely a bounded edit budget, a held-out acceptance gate, a rejected-edit buffer and an epoch-level slow update; the paper reports best or tied-best on every cell, with several reporting gaps.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-yang-2026-skillopt.md
---

# SkillOpt Agent Skill Optimization

A frozen target model runs rollouts with the current skill document. A separate optimizer model reflects on batches of successes and failures and proposes edits (append, insert, replace, delete). Edits are merged, ranked and clipped to an edit budget, which plays the role of a learning rate. A candidate skill is kept only when its score on a held-out selection split is strictly higher than the current skill's. Edits that fail the gate are stored in a buffer for the epoch. When the epoch ends, a slow update writes guidance into a protected block, and the optimizer keeps a separate meta skill. The best accepted skill is written out as a file. It is a relative of [[GEPA Reflective Prompt Evolution]] and [[Prompt Optimization]] generally, applied to skill documents.

## Reported results

All are (self-reported) unless noted.

- Best or equal-best on all 52 cells (six benchmarks, seven target models, three execution harnesses). Baselines were run by the authors.
- Dropping the edit-budget cap on GPT-5.5 lowers the three ablation benchmarks from 87.1, 77.5 and 61.3 to 84.6, 75.7 and 57.3.
- Removing both the meta skill and the slow update takes SpreadsheetBench from 77.5 to 55.0, the largest ablation drop.
- A SpreadsheetBench skill learned in the Codex harness lifts GPT-5.5 from 22.1 to 81.8 in Claude Code, against 80.4 in-domain. A GPT-5.4 skill barely helps GPT-5.4-nano.
- Final skills are 379 to 1,995 tokens, from 1 to 4 accepted edits.

## Limits

- Needs scored trajectories and a selection split held out from training; fits automatic verifiers best. Training needs extra rollouts and optimizer calls.
- No ablation without the acceptance gate, so its share of the gain is unknown.
- Seeds, repeats, error bars and decoding settings are not stated.
- Headline GPT-5.5 cells match sweep values, not the default row; the extraction notes the selection is unexplained. The default row also differs between two tables on LiveMath.
- SealQA is named in an appendix but appears in no table.

## See Also
- [[Prompt Optimization]] — prerequisite-for
- [[GEPA Reflective Prompt Evolution]] — alternative-to
- [[Reflexion]] — related (trajectory-driven reflection)
