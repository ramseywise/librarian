---
title: Memory Curse Expanded Recall
tags: [memory, concept]
summary: "A 2026 study of repeated social games finds that giving LLM agents a longer window of their own interaction history lowers cooperation in 18 of 28 model-and-game settings by the paper's own threshold; the extraction's caveats show the effect is noisy and the 'cursed' label is applied loosely."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-liu-2026-memory-curse.md
---

# Memory Curse Expanded Recall

The "memory curse" is the paper's name for cooperation falling as an agent's recall of past rounds grows. The extraction available here is an addendum that corrects an earlier report, so this page keeps to what the addendum states. History length (HL) is the number of past rounds shown to the agent; the four games are abbreviated PD, TG (the Trust Game), TD and PG (the addendum does not expand the others).

## Results

- For GPT-OSS-20B in the dilemma game, the score is 92.1 ± 1.8 with the shortest history (HL=2) but 20.6 ± 15.1 with the longest (HL=80), so the endpoint is noisy (self-reported).
- "Sanitization", replacing part of the history with synthetic cooperative rounds, partly rescues cooperation in the Trust Game: with 2 synthetic rounds (3 seeds, 500 rounds each) Gemma scores 84.0 against 9.5 at the full HL=80 baseline, GPT-OSS-20B 36.3 against 3.4, Llama-70B 97.4 against 6.9. The extraction notes the rescue fades fast: Scout falls from 87.9 at 2 rounds to 11.6 at 40 (self-reported).
- Reasoning ("CoT") penalty at HL=80, each model's worst game: Llama-70B Trust Game 100.0 to 6.9, Qwen 85.2 to 8.0, Gemma 100.0 to 35.3 (self-reported).
- Asymmetric groups (some agents forgive, some hold grudges): contagion is clear only for GPT-OSS-20B (47.4 to 28.2 to 15.9) in the extraction's reading; in the Trust Game the forgiver-minus-grudge gap is +10.3 to +28.1 points in every model.
- A word-count analysis finds the frequency of cooperation words, relative to HL=2, falls to between 0.90x (Llama-70B) and 0.43x (GPT-OSS-20B) at HL=80, while paranoia-word frequency stays near flat.

## Limits

- The "18 of 28" count is a classification: the extraction says to read it as 18 of 28 settings falling below the paper's immune threshold, not 18 collapsing. The rule is applied loosely (a Trust Game setting listed immune shows 90.2 at HL=10), and some settings counted as cursed are neither severe nor monotonic; Mistral-7B in the dilemma game slips only from 96.9 to 85.3.
- The reasoning ablation is weaker than its headline: in most HL=80 cells the no-reasoning variant does as well or better, though it is worse in four, and it is unstable. The "reasoning amplifies" mechanism is conjecture.
- Small inconsistencies between reruns appear across tables (for example Gemma symmetric HL=2: 64.5 versus 74.0). The word dictionaries are keyword lists and the paper has no limitations section.
- The fine-tuning fix used LLM-judge-filtered traces (98% ended cooperative) on Mistral-7B-Instruct-v0.1; its HumanEval check has little signal (2.44 to 1.83). Trace samples are single-round quotes, illustrative only.

## See Also
- [[Context Failure Modes]] — prerequisite-for
- [[Memory as Context]] — prerequisite-for
- [[Memory Lifecycle]] — related (what to forget)
- [[Memory Decay Weighting]] — related
