---
title: "SwiftSage Fast-Slow Agent"
tags: [harness, pattern]
summary: "SwiftSage pairs a small behavior-cloned module that acts by default with a prompted large model that plans only when a hand-written heuristic says the small one is stuck, and reports higher ScienceWorld scores at far fewer tokens per action than ReAct, Reflexion and SayCan (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-lin-2023-swiftsage.md
---

# SwiftSage Fast-Slow Agent

SwiftSage (a 2023 paper) splits an interactive agent into two modules. SWIFT is a flan-t5-large model of 770M parameters, behavior-cloned from oracle trajectories, and it acts by default. SAGE is GPT-4, prompted to plan and to ground the plan into actions, and it fills an action buffer that is then executed step by step. A hand-written heuristic decides when control passes from SWIFT to SAGE, so the large model is called only when the small one appears to be failing.

## Reported results (self-reported)

The benchmark is ScienceWorld, 30 task types with 270 test variations (the first ten per task). SWIFT on its own scores 49.22. With gpt-3.5-turbo as the large model, SwiftSage keeps 62.22 while ReAct falls from 36.43 to 19.76, so the dual design degrades more gracefully when the planner is weaker.

Cost is the main argument. Tokens per action are 757.07 for SwiftSage against 1,855.84 for SayCan, 1,971.03 for ReAct and 2,983.46 for Reflexion. Score per action is 2.73 against 0.65, 0.79 and 0.13 for the same three. It does not win everywhere: on task 6-1 it scores 49.40 against Reflexion's 70.35.

## Limits

- Reflexion was allowed up to four rounds against one for SwiftSage, which the authors call unfair, and the baselines need human subgoal annotations.
- SWIFT is trained on oracle trajectories, so it cannot repair its own mistakes.
- The switching rule is hand-written, tested on ScienceWorld alone, and no variance is reported.

## See Also
- [[Fast-Slow Thinking Architecture]] — related (the same split, discussed for voice agents)
- [[Reflexion]] — alternative-to
- [[Text-Game Agent Environments (Jericho, ALFWorld, CALM)]] — related
- [[Cost-of-Pass and Efficient Agent Design]] — related (the survey cites SwiftSage as adaptive deliberation)
