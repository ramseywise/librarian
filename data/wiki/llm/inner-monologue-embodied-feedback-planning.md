---
title: Inner Monologue Embodied Feedback Planning
tags: [llm, gui-and-embodied-agents, concept]
summary: "Inner Monologue appends success, object and scene feedback as text to a frozen LLM planner's prompt so a robot can retry and replan; with disturbances SayCan scored 0% on mobile manipulation against 75% (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-huang-2022-inner-monologue.md
---

# Inner Monologue Embodied Feedback Planning

Huang, Xia, Xiao et al. (preprint arXiv:2207.05608, cs.RO, 2022) examine how well LLM planners can use environment feedback, supplied as language in a closed loop and with no further training, to get robots to finish instructions. They hypothesise that feeding success, object and scene feedback to the prompt as text makes planning sturdier and better over long horizons than open-loop LLM planning.

## Mechanism

The LLM stays frozen and picks skills one at a time from few-shot prompts. Once a step ends, text feedback (success, visible objects, sub-goals reached, answers from a human) is added to the prompt, allowing a retry or a new plan. The paper builds three versions, each with its own LLM, skills and feedback modules. The feedback sources are:

- **Success detection:** a binary judgement of whether the low-level skill succeeded, given in language.
- **Passive scene description:** consistently provided, structured scene feedback injected without the planner asking.
- **Active scene description:** unstructured answers to queries the planner makes.
- Human feedback.

## Reported results (self-reported)

- Real kitchen (Everyday Robots, PaLM planner, learned success detector, human object feedback, three task families): Object + Success feedback raised total success over [[SayCan Affordance-Grounded Skill Selection]] across no-disturbance and disturbance conditions. With adversarial disturbances on mobile manipulation SayCan scored 0% and Object + Success 75% (Success alone 25.0%).
- Real tabletop (UR5e robot, InstructGPT 1.3B planner, MDETR detector, with noise injected into the policy): Object + Success gave 90% total success against 20% for object feedback alone (open loop).
- Sim tabletop (InstructGPT 1.3B, test-time noise): Object + Scene feedback was best on the unseen task of putting blocks in matching bowls, where CLIPort scored 0%. On putting blocks on mismatched bowls, object-only planning reached 62% and Object + Scene 86%.
- Over 10 kitchen episodes, ViLD scored 85.7% precision, 72.0% recall and 88.9% accuracy, while MDETR scored 39.6%, 87.5% and 68.2% on the same three measures.
- Some emergent behaviours were seen, namely switching goals, proposing goals itself, accepting multilingual input and answering questions about the scene, to differing degrees of consistency.

## Limits

- Sec 4.1 and 4.3 assume oracle scene descriptors (human or scripted); learned versions were checked only in Table 5.
- Three failure sources are named: the success detector (a false negative triggers a retry; a false positive leaves the planner partly blind), planner mistakes, and control mistakes. The LLM at times disregarded feedback or suggested skills involving objects that were not there.
- What the LLM can accomplish is capped by the low-level policies.
- Emergent capabilities were inconsistent without similar prompt examples.
- Trial counts are small (10 runs on the real tabletop) with no confidence intervals or seeds.
- Each domain used different LLMs, skills and feedback, so cross-domain comparisons are not controlled; InstructGPT 1.3B and PaLM-540B are dated.

## See Also
- [[SayCan Affordance-Grounded Skill Selection]] — prerequisite-for (the open-loop planner and kitchen baseline)
- [[Code as Policies Language Model Programs]] — related
- [[ReAct Synergizing Reasoning and Acting]] — related
- [[Chain-of-Thought Prompting]] — prerequisite-for (a robot thought is used with Object + Scene feedback)
- [[RoboCat Self-Improving Robot Generalist]] — related
