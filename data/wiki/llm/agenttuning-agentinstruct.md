---
title: AgentTuning and AgentInstruct
tags: [llm, agent-training, concept]
summary: Supervised fine-tuning of Llama-2-chat on 1,866 filtered GPT-4 agent trajectories (AgentInstruct) mixed 20/80 with ShareGPT; the paper reports large held-in gains and a held-out gain that is significant only at 70B (self-reported).
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zeng-2024-agenttuning.md
  - data/raw/papers/2026-11-06-yin-2023-agent-lumos.md
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

## Lumos: separate planning and grounding modules

Agent Lumos (Yin et al., ACL 2024) is another SFT-only agent recipe. It trains two modules, a planner that writes subgoals and a grounder that turns each subgoal into executable actions, using roughly 55K annotations for each module (55,382 planning, 55,499 grounding). The annotations are not generated from scratch: GPT-4 converts the ground-truth reasoning steps of existing benchmarks (math, QA, web, multimodal) into the unified chat format, because GPT-4 itself reaches only about 20% step success on Mind2Web. Loss is on assistant tokens only. Two variants exist: Lumos-O plans in one pass, and Lumos-I plans iteratively with execution feedback after each subgoal.

Reported results (self-reported; LLaMA-2-7B unless noted, same base and data across variants):

- Planning and grounding split vs one integrated module vs chain-of-thought training: StrategyQA / HotpotQA 65.7 / 45.9 for Lumos-I, 62.3 / 39.6 integrated, 58.3 / 22.1 CoT; GSM8K 50.5 for Lumos-O, 45.5 integrated, 40.4 CoT; Mind2Web 27.6 vs 25.3. Gains on the multimodal sets are small, and Lumos-O falls below the integrated module on ScienceQA and StrategyQA. Chain-of-thought training was never run on the web tasks.
- Mind2Web step success: 27.6 (7B) and 31.3 (13B) against GPT-4 at 22.6 and GPT-3.5-turbo at 15.7 (the GPT figures are taken from AgentBench); the Mind2Web-trained Lumos-I is not held out there. On HotpotQA, with GPT-3.5-turbo serving as the QA tool, it scores 45.9 where ReAct gets 40.8 and ReWOO 42.4.
- High-level subgoals beat low-level ones (65.7 / 45.9 vs 63.3 / 44.3); Lumos data beat the earlier ReWOO-open data on 2,000 sampled examples.
- Lumos-O is faster but weaker on QA: 100 GSM8K instances take 102 s against 851 s for Lumos-I, and HotpotQA 556 s against 1,007 s; on math Lumos-O scores higher (50.5 vs 47.1).
- Unseen tasks (WebShop, InterCodeSQL) work only when the module inputs carry two or three few-shot examples; WebShop reward is about 46-47 against 23.9 for Vicuna-v1.3-33B, but Claude-instant (49.7) scores about the same or higher, and InterCodeSQL success stays at 3.5-7.3.
- Mixing in Alpaca data keeps general instruction following (ROUGE-L of 39.3, compared with Alpaca alone at 39.8).

## Limits

- Only six held-in and six held-out tasks, and the held-out ones resemble the held-in (web, household).
- The trajectories come from GPT-3.5 and GPT-4, which bounds AgentLM; like GPT-3.5, it fails on held-out tasks that are very hard, Minecraft among them.
- Each setting was run once, with no seeds or significance tests, and compute and training details are not stated; eta was chosen on 13B and applied to all sizes.
- Not reinforcement learning: pure SFT on successful trajectories, with no learning from failures.
- Llama 2 and GPT-3.5/4 are 2023 models.
- Lumos (above): only four task types, no backtracking or replanning, and QA still uses GPT models as tools; SFT only, with annotations that depend on GPT-4 conversion; its "unseen" tasks need few-shot prompts; the baselines are 2023 models; the appendix puts the math decline from unified training at 0.7% and 1.4%, but the figures in Table 7 are 1.4 and 0.5.

## See Also
- [[Agent-FLAN Agent Tuning Data Design]] — alternative-to
- [[AgentBench]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — related
- [[Agent Data Protocol (ADP)]] — extends (unifies agent SFT datasets, including AgentInstruct)
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — related
- [[Self-Instruct and Unnatural Instructions]] — related (general instruction data written by a model from seeds)
