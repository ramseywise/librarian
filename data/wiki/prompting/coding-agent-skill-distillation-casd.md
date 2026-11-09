---
title: Coding-Agent Skill Distillation (CASD)
tags: [prompting, pattern]
summary: "CASD hands an unmodified coding agent a static corpus of agent trajectories and lets it analyse the whole corpus with code, then write a skill file used as the system prompt; the paper reports it beating GEPA on three of four agentic benchmarks at lower cost (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-singh-2026-coding-agents-strong-prompt-optimizers.md
---

# Coding-Agent Skill Distillation (CASD)

Search-based prompt optimizers propose an edit, run fresh rollouts, score, and keep the edit if validation improves. CASD drops that loop. An off-the-shelf coding agent (Claude Code on Claude Sonnet 5) receives a results file of agent rollout trajectories and a one-paragraph instruction to analyse it directly and write a skill markdown file of behavioural rules; that file becomes the target agent's system prompt. The authors credit the gain to **reflection scope**: the agent computes statistics over the whole corpus, where minibatch reflection sees a few traces at a time.

## Results

Setup for all rows unless noted: target agent and user simulator GPT-5.4-mini with reasoning off, Sonnet 5 as the reflection model for every method, test accuracy averaged over 3 seeds, all optimizers limited to the same static rollout pool. All numbers are the paper's own (self-reported).

- Mean gain over baseline across four benchmarks: +16.6 points for CASD, +10.9 for GEPA, +5.3 for SkillOpt.
- ALFWorld (50 held-out games): baseline 56.7, CASD 83.3, GEPA 74.0. The SkillOpt figure uses its own scaffold and is not directly comparable.
- tau2-bench telecom (40 held-out tasks): baseline 19.2, CASD 39.2, GEPA 17.5, so GEPA fell below baseline; the authors blame overfitting to the pool GEPA reflects on.
- tau2-bench retail (40 tasks): CASD 40.0 and GEPA 39.2, with standard deviations of 2.5 and 7.2.
- SpreadsheetBench-Verified (50 items): GEPA 60.7 beat CASD 51.3.
- Cost: about $1.60 per CASD prompt, which is one coding-agent session; the four-benchmark total was $6.4 for CASD, $8.4 for GEPA and $142.5 for SkillOpt. The authors treat the rollout corpus as a byproduct, so its generation cost is not counted.
- Head-to-head, with GEPA and SkillOpt also given a separate validation set and unrestricted environment rollouts, CASD stayed ahead on two of four benchmarks.
- With the distilled skill, GPT-5.4-mini recovered 78% of the gap to its thinking mode on telecom and 55% on SpreadsheetBench while using about 0.6-0.8k output tokens per episode. The thinking-mode figures come from an earlier study.

## What the distiller does

Across 24 logged runs (816 tool calls) a run made 16-51 tool calls and produced a 5-8KB skill. Every run measured rewards or pass rates and episode lengths; 96% quantified termination and failure modes. The 12 CASD skills held 54 quantitative evidence citations, against none in four GEPA prompts. In the telecom case study, the top rule targeted fabricated identity-lookup arguments in 16 of 50 episodes, and the distiller also noticed exact repeats among its `get_details_by_id` calls (123 of 284).

The authors also give a theory, not tested empirically, that offline distillation suits small rollout budgets and iterative search should gain as budgets grow.

## Limits

- One target model and one coding agent; how results change with the distiller's capability was not tested.
- CASD cannot discover behaviours absent from the logged rollouts.
- The extraction notes only three seeds and three skills and no significance tests; the authors note that sampling error alone is roughly 7 points per seed at these test sizes (binomial). The CASD deviation is skill-to-skill, the baseline's is seed-to-seed.
- The extraction notes several gaps are within noise, GEPA wins SpreadsheetBench in both regimes, and in the telecom head-to-head SkillOpt comes out ahead (44.2).
- The extraction notes GEPA was run at a single budget of 120 metric calls; CASD uses an agentic tool-using harness while baselines use their native reflection.
- The extraction notes all four benchmarks are agentic and the authors are at Microsoft, with GEPA's authors being a different group.
- The extraction flags that the arXiv ID conflicts with the stamped date, so check the ID before citing.

## See Also
- [[Prompt Optimization]] — prerequisite-for
- [[GEPA Reflective Prompt Evolution]] — alternative-to (the search-based baseline)
- [[Skill Authoring Discipline]] — related (the skill file is the output artifact)
- [[Prompting Reasoning Models]] — related (a skill that substitutes for thinking tokens)
