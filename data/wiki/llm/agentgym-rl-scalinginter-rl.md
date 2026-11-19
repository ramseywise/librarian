---
title: AgentGym-RL and ScalingInter-RL
tags: [llm, agent-training, pattern]
summary: "A multi-turn RL framework with one HTTP server per environment, plus ScalingInter-RL, which raises the maximum interaction horizon in stages during training; the paper reports a 7B model matching larger models across five environments (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-xi-2025-agentgym-rl.md
---

# AgentGym-RL and ScalingInter-RL

AgentGym-RL (Xi et al., Fudan, ByteDance Seed and others, September 2025) trains LLM agents for long-horizon decisions with multi-turn RL, from scratch without SFT, in five environments: WebArena, Deep Search, TextCraft, BabyAI and SciWorld.

## Framework

Environment, agent and training are decoupled modules. Every environment runs as an HTTP server with four endpoints (`/observation`, `/available_actions`, `/step`, `/reset`). The stack builds on veRL and AgentGym. Algorithms on offer: PPO, GRPO, RLOO, REINFORCE++, SFT, DPO, plus rejection sampling in the AgentEvol style. The authors also fixed a memory leak in TextCraft and a clock leak in SciWorld, and for WebArena added parallel Chromium instances and a full-reset interface. The reward is an outcome score between 0 and 1, binary or partial. Main settings: GRPO with KL coefficient 1e-3 and sampling temperature 1.0, 4 trajectories per query for WebArena and 8 elsewhere, max turns 15 (WebArena), 4 (Deep Search) and 20 (the rest).

## ScalingInter-RL

The maximum number of interaction turns is raised in stages: h(t+1) = h(t) + delta-h every delta steps on a monotonic schedule. In a Deep Search run of about 350 steps, a fixed maximum of 10 turns scored higher early than 5 but collapsed as training went on; the authors attribute this to high variance, credit-assignment difficulty and spurious behaviours, and say a short horizon is stable but plateaus. The staged schedule avoided both. Phase boundaries came from the total optimisation steps with no tuning, and no concrete h values or delta are given.

## Reported results (self-reported)

Setup: Qwen2.5-3B/7B-Instruct, in-domain train and test splits, small test sets (50 WebArena queries, 400 sampled search queries, short BabyAI sub-task lists), no seeds.

- Average gain of 33.65 points over the base for the 7B model, which the paper says matches or exceeds OpenAI o3 on some environments. ScalingInter-7B averages about 58.6%, against about 47% for Llama3.1-70B and about 43% for Qwen2.5-72B; the paper reads this as post-training and test-time compute beating parameter scaling, but it compares one RL-trained model with untrained larger ones.
- Per environment, ScalingInter-7B scores 26.00 on WebArena against 34.00 for o3, and 38.25 on Deep Search against 49.50. On TextCraft it reaches 91.00, just under Gemini-2.5-Pro at 94.00. It tops o3 on BabyAI (96.67 against 94.44) and on SciWorld (57.00 against 41.50).
- Gains are largest in rule-clear worlds: SciWorld 1.50 to 50.50 for the 7B model. TextCraft for the 3B model went from 14.00 to 75.00. WebArena and Deep Search gains were moderate.
- GRPO beat REINFORCE++ (3B TextCraft: 75.00 against 28.00; 3B BabyAI: 93.33 against 70.00; 7B TextCraft and BabyAI: 83.00 against 73.00 and 92.22 against 84.44), enough that 3B GRPO beat 7B REINFORCE++ on two environments. The authors cite high-variance Monte Carlo returns; no ablation isolates the cause, and PPO and RLOO were not reported.
- More test-time turns and pass@K sampling raise scores, and the RL model stays ahead: at 64 samples the RL model's margin over the base is 5.5% for Deep Search, and for SciWorld it is 7.05%, on the same setup.
- Case studies: base agents loop on a dead UI element; RL agents recover from a missing page, turn to the search box and back out through doors. Failures remain, such as redundant clicks and scrolling in WebArena.

## Limits

- The authors concede in-domain only (no generalisation to new environments or tools shown), simple digital tasks, and single-agent training.
- No variance or seeds; the horizon ablation is one environment (Deep Search, max 5 vs 10 vs staged); no process reward or credit-assignment method tested; no compute comparison despite the claim that staging cuts compute; no SFT baseline in the main tables.
- Internal inconsistencies: the text gives 16.00% for AgentGym-RL-7B on WebArena where Table 1 shows 22.00; it claims a 30-point TextCraft gain where the tables show +49 (91.00 vs 42.00); "more than 10% on WebArena" against 9.76 to 26.00; and it says the SciWorld Chem-Mix sub-task scored zero for every model, which could not be checked because the column headers were garbled. The text also calls GRPO's baseline learned, though GRPO's is group-relative.
- Baselines are mid-2025, so the "matches frontier" claim has aged.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[ScienceWorld Benchmark]] — related
- [[WebArena]] — related
- [[RL Training Frameworks for LLMs]] — related
- [[Agent Lightning v1.0 Harnessed Agentic RL]] — related
- [[DAPO]] — related
