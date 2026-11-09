---
title: AgentTuning and AgentInstruct
tags: [foundations, concept]
summary: Supervised fine-tuning of Llama-2-chat on 1,866 filtered GPT-4 agent trajectories (AgentInstruct) mixed 20/80 with ShareGPT; the paper reports large held-in gains and a held-out gain that is significant only at 70B (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zeng-2024-agenttuning.md
---

# AgentTuning and AgentInstruct

AgentTuning (2024) asks how to give an open model agent skills without losing general ability. GPT-4, and in part GPT-3.5, interact with six environments in the style of AgentBench; trajectories are filtered on final reward, and the ones kept carry ReAct-style thoughts. The result, **AgentInstruct**, is a lightweight set of 1,866 verified trajectories with a chain-of-thought rationale per step, derived from 35,341 instructions across the six tasks; the paper also uses *task derivation*, building trajectories from related existing datasets and enriching them with GPT-4 thoughts. Llama-2-chat models (AgentLM) are fine-tuned on a blend of 20% AgentInstruct and 80% ShareGPT, with loss computed on model outputs only (the mixing weight eta is 0.2).

## Results (self-reported)

Six held-in and six held-out tasks, greedy decoding, scores normalised across the evaluated models.

- Held-in overall scores: 2.75 for GPT-4, 1.59 for GPT-3.5 and 0.27 for Llama-2-70b-chat. ALFWorld (50 instances, 1-shot): Llama-2-70b-chat 6.0, AgentLM-70B 86.0.
- Held-out: the paper reports a 176% improvement for AgentLM-70B over Llama-2-70b-chat; GPT-3.5's overall is 1.49. The extraction's own figure for AgentLM-70B is truncated.
- On the general tasks (MMLU, HumanEval, GSM8K, MT-Bench) AgentLM-70B scores 0.96 and Llama-2-70b-chat 0.95.
- Ablation at 7B: filtering plus CoT beats unfiltered or no-CoT training (unfiltered with CoT 1.34 held-in and 0.47 held-out; filtered without CoT 1.38 and 0.56; filtered with CoT 0.65 held-out).
- Data mix, held-out: at 7B the mixed-data model scores 0.67 against 0.64 for general-only training, and mixed gives almost the same gain as general-only at 7B and 13B (0.78 against 0.81 at 13B) and a significant gain only at 70B (1.40 against 0.98).
- A single-task ablation mainly boosts that task, and the single-round Mind2Web data gives little cross-task benefit. A rule-based error analysis finds fewer basic errors (invalid action, repetition, refusal).
- Contamination: ALFWorld has 6 dirty examples and WebShop 1, with a WebShop token contamination rate of 47.18%, which the authors argue is benign.

## Limits

- Only six held-in and six held-out tasks, and the held-out ones resemble the held-in (web, household).
- The trajectories come from GPT-3.5 and GPT-4, which bounds AgentLM; like GPT-3.5, it fails on held-out tasks that are very hard, Minecraft among them.
- Each setting was run once, with no seeds or significance tests, and compute and training details are not stated; eta was chosen on 13B and applied to all sizes.
- Not reinforcement learning: pure SFT on successful trajectories, with no learning from failures.
- Llama 2 and GPT-3.5/4 are 2023 models.

## See Also
- [[Agent-FLAN Agent Tuning Data Design]] — alternative-to
- [[AgentBench]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — related
- [[ReAct Pattern]] — prerequisite-for
