---
title: PlanBench o1 Evaluation
tags: [eval, reference]
summary: "A September 2024 research note that runs OpenAI's o1-preview and o1-mini on the PlanBench Blocksworld and Mystery Blocksworld sets, with accuracy, cost, time and unsolvable-instance results; a classical planner scores 600/600 at a small fraction of the cost."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-valmeekam-2024-llms-still-can-t-plan.md
---

# PlanBench o1 Evaluation

Valmeekam, Stechly and Kambhampati (Arizona State University, preprint, not peer reviewed) test o1-preview and o1-mini on PlanBench, a planning benchmark built on Blocksworld. Mystery Blocksworld is the same domain with obfuscated action and predicate names. Randomized Mystery uses random-string names and full PDDL prompts. The test set is 600 static instances of 3-5 blocks with plans of 2-16 steps, one run, temperature 1.0. The 49,660-character extraction covers the whole paper including appendices.

## Results

All o1 numbers are self-reported.

- Blocksworld, zero-shot: o1-preview solved 587 of 600 instances (97.8%) and o1-mini 340 (56.6%) (self-reported). Among the conventional LLMs, the leader is LLaMA 3.1 405B, which solved 376 of 600 (62.6%) zero-shot (self-reported, same single-run setup).
- Mystery Blocksworld: o1-preview 317/600 (52.8%) zero-shot and 247/600 (41.6%) one-shot; o1-mini 115/600 (19.1%) zero-shot (self-reported). Randomized Mystery zero-shot: o1-preview 224/600 (37.3%) (self-reported). Among the ten earlier LLMs tested (natural-language prompts, zero- and one-shot), none reaches 5% on Mystery; the best is GPT-4 one-shot at 26/600 (4.3%) (self-reported, same setup). Gemini 1.5 Pro has no Mystery result because its safety filter refused.
- Giving the Mystery-to-Blocksworld translation key in the prompt lifts GPT-4 only to 10%, which the authors take to mean that the models fail to chain reasoning steps together (the authors' interpretation).
- On Blocksworld, giving one example does not always beat zero-shot. The extraction infers from the order of table columns that LLaMA 3.1 405B falls from 62.6% to 47.3%.
- Across 110 bigger regular Blocksworld problems (between 6 and 20 blocks, shortest plans running 20 to 40 steps), o1-preview solved 23.63% (self-reported), mainly those whose plans were under 28 steps.
- Unsolvable instances (100 produced by appending a single `on(x,y)` condition to the goal, PDDL prompts, o1-preview): on Blocksworld 27% are correctly flagged unsolvable, 19% get an empty plan and 54% get a full impossible plan; on Randomized Mystery the figures are 16%, 5% and 79%. False negatives on 600 solvable instances: 0% on Blocksworld, 11.5% on Randomized Mystery (all self-reported).
- Cost per 100 instances (Table 4): the o1-preview run is the priciest at $42.12, followed by o1-mini at $3.69, GPT-4o at $0.65, Claude 3.5 Sonnet at $0.44 and GPT-4o-mini at $0.02 (self-reported). Average time per instance: o1-preview 40.43 s on Blocksworld, 83.37 s on Mystery zero-shot, 111.11 s on Randomized Mystery; the Fast Downward classical planner takes 0.265 s and solves 600/600 everywhere (self-reported). The authors' o1 experiments cost $1897.55 in a week. The hidden reasoning tokens of o1 are charged like output tokens, and users cannot set how many are produced.
- Reasoning-token use does not rise as expected with plan length or search nodes; the authors suspect a cap in the preview.
- The authors describe confident, wrong justifications from o1 (for instance, treating a goal as satisfied because it held briefly at some moment mid-plan).

## Alternatives the paper points to

The authors propose pairing a smaller LLM with a sound external verifier (LLM-Modulo). The 82% (subset of the original Blocksworld set) and 70% (Logistics) figures are cited from earlier work, not run here (self-reported by that work). They also cite the idea of using an LLM to translate problems into a format for a classical planner.

## Limits

- Preliminary: the tested models were o1-preview and o1-mini, since the full o1 had not been released. Models are from September 2024 and later reasoning models are untested.
- One static 600-instance set, no variance or seeds; the authors concede a static set serves only as an upper bound.
- GPT-4o-mini and a parser turned plans into PDDL, a conversion step that may add errors. Temperature 1.0 and non-determinism reduce replicability.
- The mechanism of o1 (RL-trained chain of thought) is the authors' speculation; traces are hidden.
- PDDL prompts drive the unsolvable and Randomized Mystery tests, whereas the main tests use natural language, and Table 3 mixes zero- and one-shot rows, so these numbers are not like-for-like.
- The extraction flags that Table 1 column-to-model mapping is inferred from column order; verify against the PDF before quoting any per-model figure.

## See Also
- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — prerequisite-for
- [[Verification Loops]] — related (external verifier as the LLM-Modulo remedy)
- [[Prompting Reasoning Models]] — related
- [[Best-of-k Headline Inflation]] — related (single-run, upper-bound reporting)
