---
title: Universal Verifier for Computer-Use Agents
tags: [eval, pattern]
summary: "A prompted trajectory verifier for web computer-use agents built on four choices (task-only rubrics scored separately, process and outcome scored apart, controllable versus uncontrollable failures, per-criterion screenshot selection); with GPT-5.2 it reached outcome kappa 0.64 and 0.58 against human labels on two sets of 140 and 106 Fara-7B trajectories, above two baseline verifiers, WebJudge and WebVoyager (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-rosset-2026-art-building-verifiers-computer-use.md
---

# Universal Verifier for Computer-Use Agents

Rosset et al. (arXiv 2604.06240, 2026) describe the Universal Verifier (UV), a pipeline that reads a computer-use agent's trajectory and screenshots and decides whether the task succeeded. The authors say its agreement with human labels comes from architecture, not from a stronger backbone model.

## The four design choices

1. **Rubrics from the task alone.** Specific, non-overlapping criteria are generated before and separately from scoring. The paper reports that generating and scoring in one call leads the model to write criteria tailored to what the agent did.
2. **Process and outcome apart.** A rubric score gives the process reward and a binary label gives the outcome reward.
3. **Controllable and uncontrollable failures.** Failures the agent could not control are separated, and scored so that errors do not cascade through later criteria.
4. **Top-k screenshots per criterion.** Each criterion selects its own most relevant screenshots, so all screenshots get attended to.

## Results (self-reported)

Outcome Cohen's kappa against human labels, UV with GPT-5.2:

| Set | UV (GPT-5.2) | WebJudge (o4-mini) | WebVoyager (GPT-4o) |
|---|---|---|---|
| Internal: WebTailBench, 140 Fara-7B trajectories, in-house experts | 0.64 | 0.44 | 0.31 |
| Browserbase Online-Mind2Web: 106 Fara-7B trajectories, two annotators each | 0.58 | 0.26 | 0.13 |

- **False positives.** Outcome false-positive rate for UV was 0.01 internal and 0.08 on the Browserbase set; WebVoyager (GPT-4o) was at 0.45 and 0.60, and WebJudge (o4-mini) at 0.22 and 0.40 (internal, Browserbase).
- **Backbone swap.** Moving WebVoyager and WebJudge to GPT-5.2 cut WebVoyager's internal false-positive rate from 0.45 to 0.10, but its false-negative rate rose from 0.24 to 0.44 and kappa only reached 0.43, still below UV's 0.64.
- **Against humans.** On the Browserbase set UV's outcome kappa of 0.58 and process kappa of 0.43 fall inside the ranges between the two human annotators (0.53 to 0.57 and 0.36 to 0.45). Process agreement was lower than outcome agreement throughout.
- **Annotator exposure.** When annotators saw the UV's reasoning, their outcome kappa rose from 0.39 to 0.63, and 16.6% of their outcome judgements changed (34 changes, 31 from success to failure).
- **Auto-research.** A coding agent (Claude Code v2.1.87 with Opus 4.6) improving the verifier from blank prompts plateaued near kappa 0.55 on the internal set, which the paper frames as 70% of expert quality for 5% of the time, while the human expert needed 32 experiments across three weeks to get to roughly 0.7. Starting from the expert's best verifier, the agent exceeded the expert's peak under a no-false-positive-increase rule. Outcome kappa ranged 0.64 to 0.71 across identical prompts.

## Limits

The UV is a GPT-5.2-based prompted system (roughly 3,000 lines of code, 2,000 of prompts) designed by a single expert, the first author, and the ablation sets are small (140 and 106 trajectories). Human labels came from in-house experts and one outside vendor, and the authors concede outcome "success" is subjective and define it as primary intent. The false-negative rate was 0.32 internal and 0.31 on Browserbase, so the verifier is conservative, and the Browserbase false-positive rate of 0.08 is not near zero. At scale the UV is the reference label rather than human truth, and against it the native verifiers have false-positive rates above 20%. The auto-research result is a single setup, and the paper says some of the work was itself AI-generated. On AgentRewardBench, 8 of 30 human-labelled successes were judged false positives under the authors' own guidelines (about 0.27). No comparison is made with trained verifiers or with non-web or non-visual agents, and code and data were listed as forthcoming.

## See Also
- [[LLM-as-a-Verifier]] — alternative-to (another way to build a verifier from a prompted model, on terminal-agent trajectories)
- [[Trajectory Over Outcome]] — related (process and outcome scored separately)
- [[Computer Use Visual Grounding]] — related
- [[LLM-as-Judge Evaluation]] — related (the verifier is a judge over screenshots)
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — related
