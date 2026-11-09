---
title: "PDDL-INSTRUCT Logical-CoT Planning"
tags: [foundations, pattern]
summary: "PDDL-INSTRUCT tunes an LLM to write symbolic plans step by step, restating preconditions, effects and the full state after every action, with an external plan validator supplying feedback during training; Llama-3-8B reaches 94% valid plans on Blocksworld (self-reported, three PlanBench domains)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-verma-2025-teaching-llms-plan.md
---

# PDDL-INSTRUCT Logical-CoT Planning

PDDL-INSTRUCT (a 2025 preprint) is a fine-tuning method for symbolic planning in the PDDL/STRIPS format, not a prompting or tool-use method. Plans are linear action sequences. For each action the model must write out the preconditions it checks, the effects it applies (what gets added and deleted) and the whole state that results, and finally a goal check. The extraction calls this the restate-the-state pattern.

## Method

Training has two phases. Phase 1 is instruction tuning on such step-by-step logical chains. Phase 2 sends the model's own plans to VAL, an external plan validator, and tunes on the feedback. Feedback is either binary (valid or invalid) or detailed (it names the failed precondition or the wrong effect), with up to 10 or 15 feedback iterations. The authors reason that a checker outside the model sidesteps the poor self-correction of LLMs, and that it makes unfaithful chains less likely because every step is checked; the second claim is an assertion, not a tested one.

## Reported results (self-reported)

Setup: PlanBench, three domains, 100 test tasks each, plan validity checked by VAL, one generation per problem, with no feedback loop at test time.

- **Llama-3-8B** gets valid plans on 94% of Blocksworld tasks, 64% of Mystery Blocksworld and 79% of Logistics. The untuned model manages 28%, 1% and 11%. GPT-4 reaches 91%, 59% and 78% from baselines of 35%, 3% and 6%.
- **Feedback type.** Detailed beats binary in every domain (89 against 94, 49 against 64, 72 against 79 for Llama-3).
- **Both phases matter.** Phase 1 alone gives 78, 32 and 23; Phase 2 alone gives 72, 17 and 45.
- **Remaining errors** come mostly from misapplied effects and violated preconditions, and they cluster in the obfuscated domain: 36.0% total failure on Mystery Blocksworld, 21.0% on Logistics, 6.0% on Blocksworld.
- **Cost.** About 30 hours of training on two 24 GB GPUs and 2.3 s per problem at inference.

## Limits

- Baselines are the untuned models; there is no few-shot CoT, sample-and-validate or classical planner comparison, and they are not compute-matched against the feedback training.
- Only Llama-3-8B and GPT-4 are tested, and how GPT-4 was tuned is unclear. The plus-or-minus values in one table are unexplained.
- Training and test seem to draw on the same domains, but the paper asserts transfer across domains, and no experiment on a held-out domain is described. Only a STRIPS subset and satisficing plans are covered.
- The authors say the effect of the iteration count is unconfirmed.
- The extraction warns against citing this for choosing among tools or for DAG plans.

## See Also
- [[PlanBench o1 Evaluation]] — related (same benchmark family)
- [[Algorithm of Thoughts Plus (AoT+) State Memoization]] — related (also restates state per step)
- [[Plan-and-Solve Prompting]] — related
