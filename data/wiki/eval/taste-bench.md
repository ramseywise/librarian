---
title: Taste-Bench
tags: [eval, reference]
summary: "A 502-question benchmark of decision forks mined from agent trajectories, where a model must pick the better of two directions before the outcome is visible; the top of 14 models scored 59.7% against 25% for random under a both-orders rule, accuracy fell from 62.3% to 21.0% as the deciding evidence moved later, and a distilled student's advice raised a small executor's SWE-bench Pro success on 41 tasks (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pan-2026-tasteful-agent.md
---

# Taste-Bench

Pan et al. (arXiv 2609.25804, 2026) define an agent's **taste** as its ability to choose the better direction at a decision fork before the outcome is visible. Taste-Bench measures it without human annotation: fork labels come from the recorded outcomes of parallel attempts that diverged, or from detours where an agent abandoned an approach and recovered.

## Construction and scoring

A generator model (GPT-5.6 Sol) proposed 4,657 candidate forks from two pools: 2,677 graded rollouts on 517 SWE-bench Pro tasks (engineering) and 1,132 METR MALT runs on 47 RE-Bench and HCAST tasks (research). After a rubric filter (1,809 left), a trivial filter (729 left) and a four-judge panel, 502 questions were released (10.8%): 390 engineering and 112 research. Two reviewers agreed with the mined label on 170 of 172 explicit judgments on 100 sampled questions (kappa 0.973), but only after seeing the recorded continuations and outcomes.

A question counts as correct only if the model is right in both the seeded and the reversed option order, so chance is 25% and an always-first model scores 0%. The average is the 1:1 mean of research and engineering accuracy.

## Results (self-reported)

All on 14 models, one shared prompt, a 65,536-token budget, no visible chain of thought, one run per model.

- **Overall.** GPT-5.6 Sol scored 59.7% and GPT-5.5 59.5%; Claude Opus 5 scored 55.5%.
- **Later evidence is harder.** Mean accuracy over the 14 models fell from 62.3% when the deciding evidence was in the trajectory prefix, to 42.9% (inferable), 31.5% (next step) and 21.0% (more work). The levels were annotated by GPT-5.5, which saw the supported label.
- **Reasoning effort did not help.** Moving from lowest to highest effort changed Sol by −0.2 points (95% CI −3.2 to +2.8) and Luna by +2.2 points (CI −1.6 to +6.0), on two models and three settings each.
- **Relation to SWE-bench Verified.** Across 11 models the Pearson correlation with Verified scores was +0.63 on the average (95% CI +0.04 to +0.89) and +0.37 on engineering alone.
- **Detour forks.** Mean accuracy was 58.1% on parallel engineering, 50.9% on parallel research, 50.8% on detour research and 35.9% on detour engineering.
- **Distillation.** A Qwen3.6-27B student (LoRA, trained to imitate the same model shown the supported candidate) reached 47.9% out of fold against 30.0% for the base, with training on the 390 engineering questions in two task-disjoint folds.
- **End to end.** On 41 held-out SWE-bench Pro tasks with 98 forks, an executor (SWE-agent 1.1.0 with Qwen3.6-27B, 75 model calls) succeeded 14.6% of the time with no advice, 39.0% with correct advice and 33.7% with the student's advice.

## Limits

The authors list: SWE-bench Verified scores are public numbers from one harness and the reasoning-effort setting is not matched across models; the correlation interval is wide; only 13 questions have the top horizon level so it was merged with another. The extraction adds: there is no human taste baseline, and the 98.8% agreement shows consistency with the outcome once seen, not that the decision caused it; questions were kept only if at least one of four judges failed them without the trajectory, so difficulty is partly built in; the generator, horizon labeller and engineering trajectory agents overlap with tested models; the research half has 112 questions from 8 (parallel) and 22 (detour) tasks and the bootstrap ignores task clustering; the advice came from forks mined from earlier runs of the same tasks and includes a mandatory-verification instruction with no control for it; 21 of 98 student forks pointed to the wrong route.

Internal inconsistencies noted by the extraction: 33.7% cannot be a count out of 41 for a single run, and the run count is not stated; Sol at the same setting differs by about 2.6 points between Table 6 and Table 7, as large as the effect the reasoning test targets; one model scores 15.7% with 459 of 1,004 answers unparsable, and parse failures depress rankings yet are excluded only from the SWE-bench correlation; the text says effort does not improve accuracy while Luna's research subset rises from 43.8% to 54.5%; and the advice rule combines both orders so its numbers are not the headline accuracy.

## See Also
- [[Trajectory Over Outcome]] — related (decision quality at a fork, apart from path and outcome)
- [[LLM Judge Biases]] — related (the both-orders rule guards against position bias)
- [[Repository-Level Coding Benchmarks]] — related (SWE-bench Pro forks supply the engineering half)
- [[Eval Contamination Defenses]] — related
