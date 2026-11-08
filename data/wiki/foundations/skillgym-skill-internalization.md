---
title: SkillGym
tags: [foundations, reference]
summary: "SkillGym is a set of 2,756 containerised task environments built around human skills, with 8,364 verified teacher trajectories used for SFT; fine-tuning a Qwen3.5-35B-A3B student lifted GDPval-AA, Terminal-Bench 2.1 and SkillsBench scores, and the trained agent without skills beat its skill-assisted base (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ge-2026-skillgym.md
---

# SkillGym

Ge et al. (ECNU and Shanghai AI Lab, a 2026 preprint) build task environments from skills in the ClawHub registry, then distil teacher agents into a smaller model with supervised fine-tuning. No reinforcement learning was run; the "RL environment" framing is a plan, and rewards are binary outcomes from code verifiers.

## Dataset and filter

- The set has 2,756 environments across 12 categories and 63 sub-categories. Of these, 1,081 (39.2%) are skill-dependent and 1,675 are fallback tasks that passed the verifier. 8,364 successful trajectories average 49.0 tool calls; only 36.8% explicitly invoke the target skill. Build time averaged 4.5 hours per task with GPT-5.4.
- A **contrastive skill-dependency filter** calls a task skill-dependent when a reference agent succeeds given the skill but fails when it is withheld. No ablation compares training on those tasks against the fallback tasks.
- The teacher setups paired Claude Code with DeepSeek V4 Pro and with GLM-5.2, and paired Codex with GPT-5.4 and with Nex-N2-Pro.

## Results (self-reported)

- Full-parameter SFT on 16 H200 GPUs, one checkpoint per harness, no seeds. Under Claude Code: +199 Elo on GDPval-AA v2 (220 tasks), +19.10 points on Terminal-Bench 2.1 (89 tasks), +28.13 and +14.68 on SkillsBench v1.1 (87 tasks) with and without skills. The Codex checkpoint gained +37 Elo on GDPval and then +35.96, +27.69 and +20.39 on the other three measures in the same order.
- Without skills at inference the trained agent beat its skill-assisted base: 26.81% against 23.34% (Claude Code) and 21.08% against 5.33% (Codex). Skills still helped the trained agent.
- With skills, the 35B student scored 51.47% on SkillsBench against Sonnet 4.6 at 47.2 and DeepSeek V4 Pro Preview at 50.1, from public scores run in different harnesses; it did not reach GPT-5.4 or Opus 4.8 on Terminal-Bench.
- Mixing teachers helped terminal and skill metrics but hurt GDPval (for example GLM alone 1212 Elo against 1173 for all teachers).

## Limits

- Authors concede the Codex comparison is confounded (different system prompts), skill dependence is evidence under one reference configuration, the harness-pooling ablation does not separate diversity from teacher mix and data volume, and no RL was done.
- Reference scores mix harnesses; single run per cell with no intervals; one student model; only successful trajectories were used (17.4% pass); this is distillation from stronger teachers.
- Task templates are hand-built per sub-category, and coverage is uneven (one nosql-databases task, no successful culinary-arts trajectories).

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Skill Lift Evaluation]] — related (SkillsBench is one of its benchmarks)
- [[Terminal-Bench]] — related
- [[APIGen]] — related (verifier-gated synthetic agent data)
- [[Salesforce Koa]] — related (RL post-training of a tool-use model, SFT against RL comparison)
