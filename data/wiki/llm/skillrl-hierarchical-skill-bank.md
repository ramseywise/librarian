---
title: SkillRL Hierarchical Skill Bank
tags: [llm, agent-training, pattern]
summary: "SkillRL has a teacher distil an agent's successes and failures into a two-level skill library that is retrieved into context while a GRPO policy trains, and extended whenever a task category falls below a success threshold; on ALFWorld it reached 89.9% against 77.6% for GRPO alone (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-xia-2026-skillrl.md
---

# SkillRL Hierarchical Skill Bank

SkillRL (Xia, Chen, Wang and colleagues, NeurIPS 2026) asks how an agent could distil what it experiences into reusable, abstract skills that grow with the policy through RL, instead of storing noisy raw trajectories. Its hypothesis is that experience transfer needs abstraction: a hierarchical library distilled from successes and failures and evolved during RL should beat raw-trajectory memory and plain RL.

## Mechanism

- **SkillBank.** Two levels: general skills and task-specific skills, each with a name, a principle and a when_to_apply field, retrieved adaptively.
- **Distillation.** A teacher LLM (o3) turns base-agent rollouts into the bank: successes become strategy skills and failures become lessons.
- **Cold start.** The student (Qwen2.5-7B-Instruct) is first SFT'd on teacher traces that use skills.
- **RL with evolution.** GRPO trains with the retrieved skills placed in context, and after every validation epoch the teacher writes new skills for any category whose success is under a threshold. The bank grew during the 150 steps: 55 skills at the start (12 general, 43 task-specific), 100 at the end (20 general, 80 task-specific).

## Results (self-reported)

Setup: a Qwen2.5-7B-Instruct policy, o3 as teacher, GRPO, one reported run, no error bars. Some baselines (GRPO, RLOO, ReAct, Reflexion) come from the GiGPO paper rather than being rerun; the authors built the Mem0+GRPO baseline.

- ALFWorld 89.9% overall and WebShop 72.7%; the ALFWorld gain over vanilla GRPO (77.6) is 12.3 points, with 23.0 and 22.8 on the Cool and Pick2 subtasks.
- Other ALFWorld baselines: Mem0+GRPO 54.7 (WebShop 37.5), MemRL with the policy frozen 21.4, EvolveR 43.8, ExpeL 46.3 (prompt-based). Against prompted closed models on ALFWorld it is 41.9 points above GPT-4o and 29.6 above Gemini-2.5-Pro.
- Search QA (trained on NQ and HotpotQA, seven sets): average 47.1% against 38.5% for [[Search-R1 Reasoning with Search RL]] and 43.1% for EvolveR; Bamboogle 73.8% against 54.4%.
- Ablations (ALFWorld / WebShop): task-specific skills only 76.8 / 61.4; raw trajectories instead of skills 61.7 / 50.2 (largest drop); no cold-start SFT 65.2 / 46.5; no dynamic evolution 84.4 / 70.3.
- Prompt length averaged about 1,450 tokens for the raw-memory baseline and under 1,300 for SkillRL (about 10.3% less). Evolution reached over 80% success within 60 steps against about 90 for the no-evolution run.
- Teacher ablation (Tinker platform, added experiments): Kimi-K2.5 distilling its own skills without o3 improved ALFWorld from 71.2 to 88.5 and WebShop from 45.9 to 73.4 (91.4 and 77.6 with o3). Qwen2.5-7B distilling its own skills reached just 42.5 on ALFWorld, 19.6 on WebShop and 35.7 on search, so o3 was needed at 7B.

## Limits

- Needs a high-capability teacher for distillation and SFT data; the authors call the 7B self-distillation result a capability threshold.
- About 30 hours on 8 H100 per experiment. A growing bank may add retrieval noise, and updates are periodic rather than real-time.
- No seeds or error bars; one base model in the main tables.
- Text inconsistencies: RL batch size 16 against 64; ablation drops stated as up to 25% and 20% against the tables; PPO cited but absent from Table 1; a claimed 10-20x token compression from distillation is an assertion, with only about 10% prompt reduction measured.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Learned Skill and Action Libraries]] — prerequisite-for
- [[SkillGym]] — related
- [[Reflexion]] — prerequisite-for (verbal lessons without weight updates; a baseline here)
- [[ExpeL Experiential Learning]] — prerequisite-for (prompt-based experience rules; a baseline here)
