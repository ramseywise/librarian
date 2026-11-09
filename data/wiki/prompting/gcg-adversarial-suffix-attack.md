---
title: GCG Adversarial Suffix Attack
tags: [prompting, pattern]
summary: "GCG appends an optimised token suffix to a harmful request by gradient-guided greedy search so an aligned model starts with an affirmative reply; suffixes tuned on open models transferred to some closed models in mid-2023 tests, and the paper also introduced the AdvBench harmful-behaviour set."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-zou-2023-universal-transferable-adversarial-attacks-aligned.md
---

# GCG Adversarial Suffix Attack

The Greedy Coordinate Gradient (GCG) attack searches for a suffix that, appended to a harmful request, makes an aligned model begin its reply with an affirmative phrase ("Sure, here is ..."). It minimises the negative log-probability of that target prefix. At each step it shortlists the top-k tokens by gradient for every suffix position, tries B random swaps drawn from those shortlists, and keeps whichever swap gives the lowest loss. It is a variant of AutoPrompt that searches all positions rather than one. For a **universal** attack, losses and clipped gradients are aggregated over many prompts (added incrementally) and over models that share a tokenizer. The paper also released **AdvBench**: 500 harmful strings and 500 harmful behaviours, later reused by other jailbreak and defence papers.

## Results

All numbers are the paper's own (self-reported); the extraction truncates most values, so only those it states are given.

- Individual harmful strings, first 100 of AdvBench, Vicuna-7B and LLaMA-2-7B-Chat, 20-token suffix, 500 steps, B=512, k=256: GCG matched or beat the baselines on exact match; PEZ and GBDA got 0%.
- A universal suffix from 25 training behaviours was tested on 100 held-out behaviours on LLaMA-2-7B-Chat and Vicuna-7B.
- Transfer used 388 behaviours and an ensemble of suffixes tuned on Vicuna and Guanaco, a behaviour counted as broken when any one of four suffixes worked. Targets were gpt-3.5-turbo-0301 and gpt4-0314 at temperature 0, Claude-2 and PaLM-2 (temperature 0.9, 8 candidates). Claude-1 reached 47.9% and Claude-2 stayed low; the request alone gave GPT-4 8.0% and Claude 0.0%.
- Concatenating three suffixes raised success on GPT-3.5 and lowered it on GPT-4.
- Thirty seconds of rewording by one author per failed behaviour brought GPT-3.5 to near 100%; this was not repeated on other models.
- Running 500 steps can overfit to the source models and lower transfer.

## Limits

- Individual and universal comparisons use two white-box models and the first 100 instances; Table 1 has no seeds or intervals.
- Transfer numbers come from mid-2023 snapshots, and the authors disclosed the attacks to vendors expecting them to stop working.
- The paper tests no defence and leaves adversarial training as an open question.
- Success on behaviours is judged loosely ("reasonable attempt", possibly by human judgement), the source of the 388 behaviours is not stated, and no compute or runtime is reported.
- Claude-2's resistance may come from a chat-interface content filter the API lacks, and Vicuna may be distilled from ChatGPT-3.5; both are the authors' untested hypotheses.

## See Also
- [[Prompt Injection]] — prerequisite-for
- [[PAIR Black-Box Jailbreak Refinement]] — alternative-to (prompt-level search against token-level)
- [[PEZ Gradient-Based Hard Prompt Discovery]] — related (a baseline in this paper)
- [[Self-Evaluation Defense Against Adversarial Suffixes]] — related (a defence tested against these suffixes)
- [[PGD Adversarial Training]] — related (the image-classifier adversarial robustness setting)
- [[Adversarial Examples (Intriguing Properties of Neural Networks)]] — prerequisite-for
