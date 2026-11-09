---
title: World Knowledge Model for Agent Planning
tags: [foundations, llm, pattern]
summary: "WKM gives an agent a separately trained knowledge model: task knowledge written once from contrasting good and bad trajectories, and state knowledge retrieved per step and mixed into action probabilities; 7-8B models beat fine-tuned baselines on ALFWorld, WebShop and ScienceWorld (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-qiao-2024-agent-planning-world-knowledge-model.md
  - data/raw/papers/2026-11-06-chu-2026-agentic-world-modeling.md
---

# World Knowledge Model for Agent Planning

WKM (a NeurIPS 2024 paper from Zhejiang University and Alibaba) adds a second small model to a fine-tuned agent so that planning has a global prior and a local check.

## Mechanism

- **Task knowledge.** The agent is first tuned on expert trajectories, then re-explores the training tasks; its worse trajectories count as rejected. The agent model compares chosen and rejected ones and writes workflow and commonsense notes per task. At inference the knowledge model writes this once and it is prepended to the prompt.
- **State knowledge.** Summaries of each expert step are stored as triplets (previous action, state knowledge, next action) in a nearest-neighbour base. At each step the model writes state knowledge, retrieves matching triplets, and turns next-action counts into a distribution. The chosen action maximises a weighted mix of the agent's first-token probabilities and that distribution. State knowledge never enters the agent's context.
- Two LoRA adapters share one backbone. Inference costs about 2.5 times the plain agent.

## Results (self-reported)

Setup: LoRA on Mistral-7B, Gemma-7B and Llama-3-8B; average reward; baselines include prompted ReAct and Reflexion and three fine-tuned methods.

- Mistral-7B: ALFWorld seen/unseen 73.57 / 76.87, WebShop 65.48, ScienceWorld 62.12 / 53.62; gains of 1.08 to 5.44 points over the best fine-tuned baseline.
- It beat one-shot GPT-4 on ALFWorld (44.29 to 73.57 seen) and WebShop but not on ScienceWorld.
- Task knowledge helped more than state knowledge; putting state knowledge in the prompt hurt (65.43 / 66.69 against 73.57 / 76.87); trusting the retrieval base alone collapsed ALFWorld to 1.58 / 0.00.
- A 7B knowledge model improved GPT-4 on ALFWorld (44.29 to 50.71 seen).

## Agentic world modeling survey

A 2026 survey in the same group of sources proposes three levels of world model for agents (L1 to L3) and reports no experiments; it is context for what WKM is not. The authors of WKM themselves say it is not a true world model, since it cannot be combined with search to predict the environment.

## Limits

- The extraction notes figure values for the ablations could not be mapped to bars, and that the survey's levels are conceptual only.
- Text-only simulated environments, 7-8B backbones, no seeds or intervals, baselines from 2023 to early 2024; state knowledge depends on a training-set base so it helps less on unseen tasks; the authors concede it cannot update with the world or agent feedback, and a modified model could steer an agent toward harm.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — related
- [[DreamGym Synthetic Experience RL]] — alternative-to (learned model of the environment, used for RL)
- [[Agent Fundamentals]] — related
- [[DECKARD LLM-Hypothesized World Model]] — related
- [[ScienceWorld Benchmark]] — related
