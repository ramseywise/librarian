---
title: KnowNo Conformal Ask-for-Help
tags: [foundations, concept]
summary: "KnowNo has an LLM planner propose multiple-choice options, turns next-token probabilities into conformal prediction scores, and asks a human when the set is not a single option; with 400 calibration examples it gives a task-success guarantee, and cuts help by 10-24% in simulation (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ren-2023-robots-that-ask-help.md
---

# KnowNo Conformal Ask-for-Help

Ren et al. (arXiv 2307.01928, CoRL 2023) address when an LLM-driven robot should ask for help instead of acting.

## Mechanism

- The LLM proposes four multiple-choice options plus "an option not listed here".
- Its next-token probabilities over the choices become conformal prediction scores, calibrated on held-out examples.
- If the resulting prediction set holds one option, the robot acts; otherwise it asks the human.
- With N=400 calibration examples and delta=0.01, task completion is at least 1-epsilon with probability 1-delta, regardless of how accurate the LLM is. The guarantee assumes the human help is faithful, the text fully grounds the scene, and actions are executable.

## Reported results

- Human help falls by 10-24% against a thresholding baseline at matched success (self-reported).
- Hardware tabletop, 50 trials: task success 0.74 against 0.72 for the Simple Set baseline, with a help-step rate of 0.58 against 0.72 (self-reported).
- Asking the model to flag its own uncertainty in the prompt gives no control (Prompt Set at 35% in the Spatial setting). A 20-sample ensemble costs 20 times the inference.
- Labelling calibration data takes about 4 hours per 400 multi-step examples.

## Limits

- Calibration data must be drawn from the deployment distribution; a shift voids the guarantee. Needs logit access.
- Scenarios are small and hand-built, and there is no user study of help burden.
- The extraction notes the reported numbers hold for a per-step ask rule applied to a multiple-choice proposal, and do not carry over to a model flagging itself as unsure.

## See Also
- [[SayCan Affordance-Grounded Skill Selection]] — prerequisite-for (the skill-scoring planner setting)
- [[Selective Risk Guarantees: SGR and Conformal Sets]] — prerequisite-for (conformal guarantees for a score)
- [[Confidence-Gated Escalation]] — related (escalating on a score)
