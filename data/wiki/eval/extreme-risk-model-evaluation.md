---
title: Extreme-Risk Model Evaluation
tags: [eval, concept]
summary: "Shevlane et al.'s 2023 framework splits evaluation for extreme risks into dangerous-capability and alignment (propensity) tests, names nine dangerous capabilities, and wires results into training, deployment, transparency and security decisions; a position paper with no experiments, it lists its own limits and hazards, including that training models to pass the tests removes their value as a risk indicator."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-shevlane-2023-model-evaluation-extreme-risks.md
---

# Extreme-Risk Model Evaluation

Shevlane et al. (arXiv 2305.15324, 2023; authors from several labs and institutes) set out a
framework for evaluating general-purpose frontier models for extreme risks from misuse and
misalignment. It reports no experiments, datasets or results; Figure 2 is labelled purely
illustrative. The authors call it an ambitious blueprint, not current practice.

## Two kinds of evaluation

1. **Dangerous capabilities:** whether the model has the ability to cause extreme harm.
2. **Alignment (propensity):** whether it would apply its capabilities harmfully.

As a heuristic, the authors would treat a model as highly dangerous when its capabilities
together could suffice for extreme harm, whether through misuse or misalignment. Their non-exhaustive list has nine
entries. Among them are cyber-offense, deception, persuasion and manipulation, and weapons acquisition;
the rest are political strategy, long-horizon planning, AI development, situational awareness
and self-proliferation. Generically useful abilities such as browsing are left out, and combinations
are called the riskiest. Alignment evaluations should look for pursuit of unsupplied long-term
goals, power-seeking, resisting shutdown, collusion between AI systems, and holding out against malicious
users who try to unlock dangerous capabilities. A narrow pass, for example an agent stating it
does not object to shutdown, is said to say little about behaviour given a real opportunity.

## How results feed decisions

Results feed risk assessments, which shape or constrain four kinds of decision: training (delay or
pause, adjust methods, train a smaller model), deployment (whether and with what guardrails,
staged release, re-evaluation after updates, internal deployment included), transparency
(incident reports, shared risk assessments) and security (red teaming, monitoring, isolation,
rapid response). Fixes should address the underlying issue rather than the evaluation score.
Inputs are internal evaluation, external research access and external audit, and the authors
say internal evaluation has no substitute because insiders have deeper access.
Their design criteria include surfacing latent capabilities, for example through prompt
engineering or fine-tuning, and robustness to a model that behaves differently when evaluated.

## Hazards the authors name

- Results, datasets and elicitation techniques can themselves advance or spread dangerous
  capabilities; evaluation datasets are dual use because others could fine-tune on them.
- If developers train directly to pass the evaluations, the evaluations stop indicating risk,
  whether through accidental leakage into pretraining data or deliberately. The remedy suggested is
  private held-out evaluations. Merely discarding models that fail also selects for methods
  that produce deceptively aligned models, in the authors' words.
- Running the tests carries harm too, such as worker distress or a poorly managed self-proliferation
  test ending in actual proliferation.

## Limits

The paper gives no thresholds and no validated evaluations, and shows no evidence that any
evaluation predicts harm; and excludes structural and incompetence risks. Its own limitations section (numbered
six though it says five) covers factors beyond the model, unknown threat models, capability
overhang (abilities researchers do not realise a model has, such as chain-of-thought prompting after
GPT-3), deceptive alignment, emergent capabilities that undermine forecasting from smaller
models, an immature audit ecosystem and overtrust. It calls evaluation necessary but not
sufficient. It describes the 2023 landscape and predates most published dangerous-capability
suites and frontier safety policies. Its only number is a cited 2022 survey of AI researchers, 36% of whom saw a plausible route to a
catastrophe this century comparable to a full nuclear war.

## See Also
- [[Eval Contamination Defenses]] — related (held-out evaluations against training on the test)
- [[Execution Boundaries and Guardrails]] — related (deployment and security decisions the results feed)
- [[Live Penetration Testing of Agents and Professionals]] — related (a cyber-offense capability measured in a live setting)
- [[Trajectory Over Outcome]] — related
- [[Forecasting Rare Model Behaviours]] — related (forecasting worst-case misuse and misaligned-action risk from a small eval)
- [[Goal-Directedness Measure]] — related (a measured propensity score, and a position paper on agentic harms)
- [[LM Red Teaming]] — related (automated test-case generation against a target model)
- [[Goal-Directedness Measure]] — related (a measured propensity score, and a position paper on agentic harms)
- [[LM Red Teaming]] — related (automated test-case generation against a target model)
