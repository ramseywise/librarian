---
title: ContinualSkillBench
tags: [eval, reference]
summary: "ContinualSkillBench runs ordered streams of 100 tasks per domain to test whether agents that maintain SKILL.md libraries beat agents that only keep context and feedback; on Law, Finance and Healthcare the two scored about the same (normalized reward 0.582 against 0.585, self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-guan-2026-continualskillbench.md
---

# ContinualSkillBench

Guan et al. (Peking University and BIGAI, a 2026 preprint) built a benchmark of ordered task streams in five domains (Law, Finance, Healthcare, Office, Math). An agent can create or modify SKILL.md files between tasks under a prompted create-or-modify protocol; the reflection prompt tells it to abstract feedback into reusable methods and avoid task IDs and absolute paths, and each skill needs a YAML header or it will not load. It was run with Codex CLI and Claude Code harnesses.

## Findings (self-reported)

- **Skill maintenance against plain in-context learning.** Claude 4.7 Opus and GPT-5.3-Codex were the two models run on Law, Finance and Healthcare, with 100 ordered tasks each, gave 6 model-domain combinations. Normalized reward was 0.469 for Independent (history and skills reset on every task), 0.585 for pure in-context learning (same task order and evaluator feedback, no skill writing) and 0.582 for Sequential with skills.
- **Retained experience helps, unevenly.** Sequential beat Independent by +0.071 raw and +0.078 normalized, a macro average over 15 pairs of model and domain (three models: GPT-4o, GPT-5.3-Codex and Opus 4.7); this bundles retained context, feedback and skills together.
- **Format matters.** Against in-context learning, skills won or tied every one of the 6 Exact Match comparisons and won or tied 5 of 6 on Programmatic scoring, while in-context learning scored higher on Rubric scoring in 5 of 6.
- **Weaker writers fragment the library.** Across all five domains GPT-4o built 384 skills averaging 5.68 in quality and GPT-5.3-Codex built 205 averaging 7.94, with GPT-4.1-mini applying the rubric. The authors conclude pool growth is not learning.
- **The stream offers reuse.** 69.5% of eligible tasks can reuse at least one core skill from before; curated order gives 25.7% local coverage against 20.4% for random order in a 5-task window.

## Limits

- Authors concede fixed task sources that miss long-tail and distribution shift, and few models and harnesses because of API cost.
- The comparison of in-context learning with skills spans just two models and three domains, and the fragmentation analysis also covers two models.
- Reward blends rubrics judged by an LLM, task order assisted by an LLM and skill quality scored by an LLM, and raw and normalized reward can disagree.
- The paper reports no variance, seeds or significance tests, and the extraction infers that some Exact Match cells rest on roughly 10 to 14 tasks.
- Skills are prompted files, not a learned memory manager.

## See Also
- [[Skill Lift Evaluation]] — related (with-and-without skill comparisons)
- [[Memory Architecture]] — related (keep the raw trace or distil a routine)
- [[Skill Authoring Discipline]] — related
