---
title: KnowAgent Action Knowledge Base
tags: [harness, concept]
summary: Planning method that writes a hand-built action set and allowed-transition graph into the agent prompt and fine-tunes on rule-filtered self-generated trajectories; reported to cut invalid actions and beat ReAct prompting on HotpotQA and ALFWorld (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhu-2024-knowagent.md
---

# KnowAgent Action Knowledge Base

KnowAgent (preprint, arXiv v3 Feb 2025) targets *planning hallucination*: action sequences that break action rules or common sense, such as a lookup made with no earlier search, or picking an apple from a table without checking that both are present. Its remedy is an explicit action knowledge base: the available actions and the transitions allowed between them, written out as text in the prompt. On HotpotQA the actions are Retrieve, Search, Lookup and Finish, and, for instance, a Search step can be followed by another Search, a Retrieve, a Lookup or a Finish. Trajectories keep the ReAct thought, action and observation layout, extended with an ActionPath at each step. The prompt has four sections: an overview of the action knowledge, a definition of each action, principles for path generation, and demonstrations.

A second stage, *knowledgeable self-learning*, has the model generate trajectories, keeps only correct ones that obey the rules (no invalid or disordered actions), prefers the shorter path when iterations cover the same task, and fine-tunes with LoRA. The paper uses two iterations.

## Results (self-reported)

Setup: Llama-2-chat backbones with LoRA and two self-learning iterations. HotpotQA uses 100 questions per difficulty level across 3 levels, scored by F1; ALFWorld is tested on 140 seen and 134 unseen tasks and scored by success rate.

- Llama-2-13b: HotpotQA average F1 39.26 against 24.17 for ReAct; ALFWorld unseen 58.71 against 9.70. The extraction notes that the abstract's figures of 15.09% and 49.01% are differences in percentage points and not relative gains.
- On ALFWorld the fine-tuned model beats the prompted GPT-4 ReAct baseline (43.57 seen, 38.81 unseen) at both 13b (54.29, 58.71) and 70b (77.14, 78.36).
- Action knowledge in the prompt alone, without fine-tuning, lifts 13b ReAct on ALFWorld from 13.58 to 30.00 (seen) and 9.70 to 38.06 (unseen).
- HotpotQA with 13b, planning-hallucination rates: invalid actions 0.35% against 2.08% for ReAct and 6.87% for Reflexion; misordered actions 1.23% against 3.54% and 3.87%.
- Fewer than 300 self-synthesised trajectories per iteration, against 500 GPT trajectories for the FireAct and NAT baselines. At 70b the HotpotQA margin over FireAct is 48.14 against 48.04.
- Training takes about 20 hours per cycle (about 40 in total) against about 50 for FireAct, on 8 V100 32G GPUs with Llama-2-7b on ALFWorld.
- Hand-written knowledge against knowledge distilled from gpt-4-0613: HotpotQA 33.47 against 25.22 at 7b and 39.26 against 25.72 at 13b; ALFWorld 52.24 against 51.49 at 13b. The text claims little difference, which holds only for ALFWorld.

## Limits

- The authors concede two tasks only, single agents only, and a manual, labour-intensive knowledge base that GPT-4 distillation does not remove.
- At 13b FireAct is better on easy HotpotQA questions, and at 70b the edge fades on hard ones (37.76 against 44.60) because the long prompt hurts long contexts.
- Single runs and small test sets with no variance or significance tests (the extraction's observation); the GPT-4 ReAct baseline is prompted rather than fine-tuned, and Llama-2 is dated.
- The extraction notes that the "knowledge" amounts to a transition graph, written by hand, over a small action set and is not external factual knowledge.

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Reflexion]] — alternative-to
- [[Tool Design as Harness Surface]] — related
- [[World Knowledge Model for Agent Planning]] — alternative-to (planning knowledge learned rather than hand-written)
