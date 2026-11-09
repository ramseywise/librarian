---
title: Learned Skill and Action Libraries
tags: [loop, concept]
summary: "Four papers grow a library the agent writes for itself (Voyager code skills, LearnAct Python actions, COS-PLAY protocols, WikiSkill text skills); each gates entries on a check, and each reports the library helping, with controls that differ in strength."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-wang-2023-voyager.md
  - data/raw/papers/2026-11-08-zhao-2024-empowering-large-language-model-agents.md
  - data/raw/papers/2026-11-06-wu-2026-co-evolving-llm-decision-skill.md
  - data/raw/papers/2026-11-06-tang-2026-wikiskill.md
---

# Learned Skill and Action Libraries

The common idea is that an agent improves with frozen or lightly trained weights by writing reusable artifacts into a store and retrieving them later. The four systems differ in what an entry is and what must be true before it is stored.

## The four designs

- **Voyager** (Wang et al., 2023, Minecraft). GPT-4 writes code for tasks an automatic curriculum proposes, revises it for up to four rounds using game feedback, error messages and a GPT-4 critic, then stores verified programs in an embedding-indexed library. Over 160 iterations and 3 trials it found 3.3 times more unique items than the best baseline (self-reported). Ablations: a random curriculum cut items by 93%, removing self-verification cut them by 73%, and without the library it plateaued late.
- **LearnAct** (Zhao et al., COLM 2024). A GPT-4 learner writes Python functions over the basic actions, runs an agent on three training instances, selects a failed case whose error involves an action and either updates a function or adds a note to its description. Four candidates are sampled per iteration and the one with the best success-plus-step-accuracy score is kept. At test time a plain agent uses the learned actions. The paper reports gains over ReAct plus Reflexion on AlfWorld and over Voyager on Robotic Planning (self-reported), that the best result comes at about two iterations, and that longer learning overfits the training cases.
- **COS-PLAY** (Wu et al., 2026). The decision agent and a skill bank are trained together (SFT cold start on 60 seed trajectories per game, then GRPO). Skills are protocols with a contract, and the bank is managed by refine, materialize, merge, split and retire operations. A contract is saved only when enough episodes confirm it, for example 26 of 28 episodes in the worked example. A Qwen3-8B reached an average reward of 924.4 on four single-player games against 717.4 for GPT-5.4 (self-reported; 16 evaluation rollouts). A policy paired with a skill bank taken from another training stage scored below the base model, which is the paper's evidence for co-evolution.
- **WikiSkill** (Tang et al., Google Research, 2026). A Wiki Maintainer compiles trajectories into a persistent wiki and a Skill Proposer writes skill text from it; an update is kept only if it strictly improves on a validation split, and otherwise only the skills roll back. Across five models and five benchmarks the average margin over the best baseline was +3.3 to +12.0 points (self-reported, mean of 3 evolution runs). Removing the wiki and Maintainer dropped Gemini-3.5-Flash from 63.7 to 48.7. Skills evolved by one model sometimes hurt another: Gemini on SpreadSheet fell from 50.5 to 18.1 with a 4B model's skills.

[[SkillWeaver Compositional Skill Routing]] covers how stored skills are routed and [[Skill Authoring Discipline]] covers writing them by hand; this page covers how they are grown.

## Limits

- Voyager: 3 trials, no variance tests, baselines re-implemented by the authors, a high-level API that removes perception, and a GPT-4 snapshot since deprecated.
- LearnAct: two text-based domains, GPT-4 as the learner everywhere, 3 runs with no variance reported, and the abstract's 32% is relative, not points.
- COS-PLAY: the extraction notes that "25.1%" does not match the table averages (924.4 over 717.4 is +28.9%), Diplomacy shows 64 skills in Table 2 and 121 discovered in Figure 3c, and the Avalon "1%" claim sits beside a 3-point gap to Gemini.
- WikiSkill: the no-wiki arm also removes the Maintainer, so the 15-point drop mixes two changes; test splits are small and no variance is shown.
- Cross-model transfer of skills is not uniformly positive, so a library built by one model is not safe to hand to another unchecked.

## See Also
- [[Skill Authoring Discipline]] — related
- [[SkillWeaver Compositional Skill Routing]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Reflexion]] — prerequisite-for
