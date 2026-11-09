---
title: HeavySkill Heavy Thinking Skill File
tags: [harness, pattern]
summary: A two-stage parallel-then-deliberate reasoning pipeline packaged as a plain-text skill file, with benchmark results that compare it against single trajectories and majority vote rather than against a harness.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2026-heavyskill.md
---

# HeavySkill Heavy Thinking Skill File

HeavySkill (Wang et al., Meituan LongCat Team, arXiv preprint, May 2026) argues that what drives orchestrated harnesses is one model capability it calls heavy thinking: K parallel reasoning trajectories followed by one deliberation pass that synthesises them. The authors ship it as a skill file the orchestrator reads and runs, and state that one unchanged file worked in Claude Code as well as in a custom harness of their own. Results are self-reported.

## Reported numbers (self-reported)

Setup: sampling at temperature 1.0 with top-p 0.95 and top-k 10, a single iteration, K set to 8 or 16, four summaries per problem (HM@4), same model for both stages unless stated. No seeds, error bars or run counts; AIME25 and HMMT25 have 30 problems each.

- STEM (Table 1): HM@4 beats mean single-trajectory accuracy for every listed model but does not always beat majority vote. At K=8, GPT-5 Thinking on AIME25 is 96.7 for both; Claude 4.5 Thinking on BeyondAIME is vote 66.0 against HM 63.3; Kimi K2 Thinking on HMMT is vote 90.0 against HM 93.3 and on GPQA-Diamond 82.3 against 86.9.
- General tasks (Table 2): on IMO-AnswerBench, GPT-OSS-20B moves from 65.8 to 71.0 and Kimi K2 from 69.1 to 77.2; Arena-Hard marginal or slightly negative.
- Tool use (Table 3, Python interpreter, 50 rounds): HM@4 comes out ahead of Vote@4 in five of the six cells; Qwen3-32B on AIME25 is the exception (vote 83.3, heavy 80.0).
- Rescue analysis on R1-Distill-Qwen-7B (10k queries, K set to 16): for queries with a parallel pass rate under 0.5, more than 500 were rescued and about 1,400 were still unsolved. For queries scoring higher than 0.5, accuracy held at over 98%, with about 30 queries made worse.
- A different model can deliberate: Qwen2.5-32B-Instruct beat Mean@K over R1-Distill-Qwen-7B generations. Over 4 iterations HM@K rises while HP@K falls.

## Limits

- All experiments are Python workflows rather than a skill executing inside a harness, so none contrasts a harness that has the skill with one that lacks it. Portability to Claude Code is asserted without data, and the skill file recommends K of 3 to 5 while all results use 8 or 16.
- The scope covers STEM, code and instruction following, all with checkable answers; the paper says gains are weaker on preference tasks. Cost is not reported (the extraction estimates about K+1 times the tokens), with no compute-matched baseline beyond voting.
- The extraction notes the paper's internal inconsistencies: Table 2 shows Heavy-Pass@4 of 86.0 against Pass@K of 89.5 for GLM 4.6 on IMO-AnswerBench while the text says 86.0 against 75.1; for GPT-OSS-20B on LiveCodeBench the text gives a rise from 69.7% to 85.5%, yet 85.5 in the table is the pass figure; the text says "consistently" for tool use despite the Qwen3-32B exception; and an IFEval row is attributed to a different model than the table.
- The abstract mentions learnability and RL scaling, yet the body contains no RL section, and only an appendix figure shows curves.
- The harness-reduces-to-capability claim is a thesis; the gains are a known best-of-K plus synthesis effect.

## See Also
- [[Harness Anatomy]] — related
- [[Self-MoA Single-Model Aggregation]] — related (aggregation of parallel samples)
- [[Progressive Disclosure and Skill Packs at Library Scale]] — related (skill files)
