---
title: Goal-Directedness Measure
tags: [eval, concept]
summary: "Everitt et al. score goal-directedness as how much of an LLM's measured capability it actually uses on a larger task, on a scale from a random policy to full use; in a Blocksworld test of 8 models, most fell short, and measurements taken fell when a step sat inside a bigger task (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-everitt-2025-evaluating-goal-directedness-large-language.md
  - data/raw/papers/2026-11-08-chan-2023-harms-increasingly-agentic-algorithmic-systems.md
---

# Goal-Directedness Measure

Everitt, Garbacea, Bellot et al. (arXiv 2504.11844, 2025, a preprint with no venue stated) separate
two things that usually get merged: how well a model does a task, and how willingly it uses the
capabilities it has. They define goal-directedness as the propensity to use capabilities, so what
matters is whether the model is willing to employ an ability it has.

## The score

GD = (E[R_pi] - E[R_pi0]) / (max E[R_pi*c] - E[R_pi0]).

- R_pi is the return the agent actually earns on the task.
- R_pi0 is the return of a uniformly random policy, the floor.
- The ceiling is the return from using every capability fully, where those capabilities are
  measured one subtask at a time.

GD = 1 means full use and GD = 0 means random. Capability is inferred from subtasks, then
compared with the composite task, so the gap is the finding. The extraction suggests
this adds a failure mode to component-by-component grading: a component scores well alone, and
the agent still under-uses it inside the larger task. See [[Trajectory Over Outcome]].

## Results (self-reported)

Setup for all: Blocksworld with 3, 4 and 5 blocks; 30 seeds per task and subtask; 8 models
(gemini-2.0-flash, gemini-1.5-pro and gemini-1.5-flash; gpt-4o-2024-11-20, gpt-4-turbo-2024-04-09 and
gpt-3.5-turbo-0125; claude-3-5-haiku-20241022 and claude-3-7-sonnet-20250219), queried
in March and April 2025 through LangChain. GD is estimated by Monte Carlo, 10,000 simulations for
each task and setting, with 95% bootstrap intervals clustered by block count. Runs that had not
finished after roughly 100 steps are dropped, and thinking models are left out because they
hallucinated environment responses. The paper's text gives almost no numeric GD values; the
extraction read figures from bar charts, so the numbers below marked "by eye" are approximate.

- Most models fall short of full goal-directedness. Gemini 2.0 Flash and, alongside it, Claude 3.7 Sonnet are
  nearest, though still somewhat short on Information Gathering and Combined, and the authors add
  that they cannot be sure. By eye, gpt-3.5 sits near 0.48 on Information Gathering.
- Every model measures less per block when height estimation is a step inside a larger task
  (the paper says without exception). By eye, standalone bars run from about 3.5 up to 7 measurements for
  each block, composite bars from about 1.2 to 3.
- GD and performance come apart. Although none is perfect on Plan and Execute, two come close to full GD:
  Gemini 2.0 Flash, and also Claude 3.7 Sonnet. GPT-4 and GPT-4o execute almost flawlessly alone yet
  match the rest on the composite task, which gives them lower GD.
- The ordering of models is broadly stable over the four composite tasks, and agrees with two
  other measures: the median number of height measurements, and rebuilding a falling 15-block
  tower. Gemini models on the tower and Gemini 1.5 Flash on measurements are the exceptions.
- Prompting (Gemini 2.0 Flash, Information Gathering only): a motivating prompt lifts
  performance and a demotivating one lowers it, though the motivated model remains far from the
  full-capability level.
- Context length does not explain the drop. Only the Gemini models were stepped through the
  subtasks in a single context; they generally did better than on the composite task, except
  Gemini 1.5 Flash.

## Agency characteristics in a position paper

Chan, Salganik, Markelius et al. (FAccT 2023, arXiv 2302.10329) argue, without experiments, that
algorithmic systems are becoming more agentic and that harms should be anticipated before
deployment. They name four characteristics that raise agency, especially in combination:
underspecification (how far a goal can be met without a spelled-out method), directness of
impact (no human in the loop), goal-directedness (acting as if trained for a quantifiable
objective) and long-term planning. Their goal-directedness is defined by how far the system acts as if trained toward a quantifiable
objective; Everitt's is a measured propensity to use capability. They cite, with no numbers, that that reward hacking can jump abruptly as models grow or train longer, and that RL training raises how often an LLM states instrumental
goals such as gaining wealth or resisting shutdown, while cautioning that stating a goal is not
pursuing it. Their proposed practices are simulation and scenario planning, documentation
(datasheets, model cards, reward reports), agency metrics, compute limits and an agency threshold
as a deployment bar for sectors such as health care and finance.

## Limits

- A single synthetic environment, Blocksworld; the authors say they would ideally want hundreds
  of tasks over tens of domains.
- The method infers capability from isolated subtasks. That presumes the model can combine them,
  and that short subtasks demand less goal-directedness than long ones. A bigger task might be more
  motivating, or leave time to repair mistakes.
- Only the goal stated in the prompt is probed, with no intrinsic goals or fine-tuned objectives
  (brevity, helpfulness) that might compete with the task.
- Some models reach full GD on Cognitive Effort and still fall short elsewhere, so one
  decomposition at full score is not proof of full goal-directedness.
- Only non-scaffolded models are covered: no fine-tuning study, and no reasoning models. The
  prompting analysis uses one model and one task. The cross-task agreement has no p-values and is
  called roughly the same by the paper. The models date from early 2025.
- The extraction notes that the GD formula's spacing came out garbled and that figure readings are
  approximate.
- Chan et al. offer no experiments; their evidence is cited from other work. They accept that
  long-horizon acting, understanding of the world and hallucination remain technical barriers,
  say that progress toward agency is difficult to benchmark, and leave agency metrics as future
  work. The systems they name date from early 2023.

## See Also
- [[Extreme-Risk Model Evaluation]] — related (its alignment tests also probe propensity, not just capability)
- [[Trajectory Over Outcome]] — related (a behavioural signal, measurement counts, beside outcome grading)
- [[Agent Plasticity]] — related
- [[Agent Security Risk Taxonomy]] — related
