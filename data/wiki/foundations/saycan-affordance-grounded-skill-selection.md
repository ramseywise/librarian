---
title: SayCan Affordance-Grounded Skill Selection
tags: [foundations, concept]
summary: "SayCan picks a robot's next skill by multiplying a language model's score for the skill text by a learned value-function affordance for the current scene; with PaLM 540B on 101 instructions it planned correctly 84% of the time and executed 74% in a mock kitchen (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-ahn-2022-do-as-i-can-not.md
---

# SayCan Affordance-Grounded Skill Selection

Ahn, Brohan, Brown et al. (arXiv 2204.01691, preprint, 2022) ask how a robot can use a large
language model to follow long, abstract instructions even though the model knows nothing of what
the robot is able to do in its present surroundings. Their hypothesis: weighting the model's judgement of a skill by
an affordance for that skill grounds it, and a better model should give a better robot.

## Mechanism

The robot has a fixed set of skills, each a behaviour-cloning or RL policy with a text description.
At each step:

1. The LLM scores each skill description: how likely it is to be a valid next step
   for the instruction (task-grounding).
2. Each skill's learned value function gives an affordance for the current state
   (world-grounding).
3. The two are multiplied, and the skill with the highest product is executed (Algorithm 1 of
   the paper takes the argmax over skills of the affordance term times the LLM term).
4. Its description is appended to the prompt and the loop repeats until the model says "done".

The LLM is prompted, not trained. The paper's generative baseline instead lets the model produce
free text and projects it onto a skill.

## Results (self-reported)

Setup: PaLM 540B SayCan on a mobile manipulator, 101 instructions in 7 families, in a mock office
kitchen unless stated. Three human raters judge plan and execution success, and two must agree.
Plan success means the chosen skills are right, whether or not they execute.

- Mock kitchen: 84% plan, 74% execution. Real kitchen: 81% plan, 60% execution.
- Removing the value-function grounding lowers plan success to 67%; the generative baseline
  reaches 74%. On the 11 Embodiment instructions, no-value-function planning scores 18% against 64%.
- Behaviour cloning on the raw instruction with no LLM executes 0% overall; the BC USE ablation
  reaches 60% for single primitives but only 9% execution overall.
- Long-Horizon (15 instructions) is hardest: 73% plan, 47% execution. NL Nouns (15 instructions)
  plans 67% against 100% for NL Verbs; the authors attribute it to 20 nouns (15 objects, 5
  locations) against 6 verbs.
- Of the errors in the 101-instruction evaluation, 65% were LLM failures and 35% affordance failures.
- Full SayCan with FLAN 137B replaced by PaLM 540B rises from 70% to 84% plan and 61% to 74%
  execution, which the authors say roughly halves errors. Without the value function (generative
  only, USE projection), plan success is 74% for PaLM 540B, 72% for 62B, 38% for 8B and 43% for FLAN 137B.
- Prompt examples (language-based simulator, 50 instructions, plan must terminate): 0 examples 10%,
  4 examples 82%, the 17-example final prompt 88%.
- Case studies: 21 drawer queries plan 100% but execute 33%; multilingual queries succeed on 11 of
  12 (English, Chinese, French, Spanish; a long French one fails). Vanilla scoring does not handle
  negation, and chain-of-thought prompting is reported, qualitatively, to fix it.

## Limits

- Each instruction is run once and rated by two-of-three human agreement; there are no seeds,
  intervals or significance tests.
- The evaluation instructions were developed alongside the system, and skills were trained in the
  mock kitchen, so those numbers are in-distribution.
- The authors name the breadth and robustness of the low-level skills as the bottleneck. The
  system runs open loop, so it has no way to respond when a high-value skill fails.
- It inherits LLM limits, including trouble with negation and ambiguous references. Navigation
  assumes known object locations, the place affordance is fixed at 1.0 and the calibration parameters
  are set empirically.
- The robot comparison of model sizes covers only PaLM 540B and FLAN 137B; 8B and 62B appear only
  in the generative plan test.

## See Also
- [[Action Chunking]] — related (the planner-and-policy split in robot control)
- [[Agent Fundamentals]] — related (the tool-using loop with a grounded action set)
- [[Chain of Thought]] — related (used for the negation case study)
- [[KnowNo Conformal Ask-for-Help]] — extends (adds a calibrated decision to ask a human)
