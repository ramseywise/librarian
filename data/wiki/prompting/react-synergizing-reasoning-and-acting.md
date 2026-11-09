---
title: ReAct Synergizing Reasoning and Acting
tags: [prompting, concept]
summary: The ReAct paper's few-shot results on PaLM-540B, interleaving thought, action and observation steps; it trails CoT on HotpotQA alone (27.4 against 29.4 EM) but a ReAct/CoT-SC hybrid reaches 35.1, and it beats action-only prompting on ALFWorld and WebShop (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-yao-2022-react.md
---

# ReAct Synergizing Reasoning and Acting

ReAct (ICLR 2023) gives a frozen PaLM-540B between 1 and 6 hand-written few-shot trajectories, each made of thought, action and observation steps. On HotpotQA and Fever the agent uses a three-action Wikipedia API (search, lookup, finish); on ALFWorld and WebShop thoughts are sparse. Baselines come from stripping the same trajectories down: Standard, CoT, CoT-SC and Act (actions without thoughts). The paper also reports a small finetuning study, bootstrapped from ReAct trajectories, on PaLM-8B and 62B. This page records the paper's numbers; the general loop is covered by [[ReAct Pattern]].

## Results (self-reported)

- HotpotQA question-only, PaLM-540B, few-shot with 6 exemplars, exact match: ReAct 27.4, CoT 29.4, Act-only 25.7, Standard 28.7, CoT-SC 33.4. Fever (3 exemplars) accuracy: ReAct 60.9, CoT 56.3, Standard 57.1, CoT-SC 60.4.
- Hybrids: ReAct falling back to CoT-SC when no answer appears within 7 steps (5 on Fever) scores 35.1 on HotpotQA; CoT-SC falling back to ReAct when the majority answer has fewer than n/2 votes scores 34.2 on HotpotQA and 64.6 on Fever, the best Fever result. CoT-SC here means 21 samples at temperature 0.7; 3 to 5 samples in the hybrids match 21 samples of CoT-SC alone.
- A manual study of 200 HotpotQA trajectories (50 correct and 50 incorrect per method for ReAct and CoT) finds hallucination in 56% of CoT failures and none of the ReAct failures; 14% of CoT successes are false positives against 6% for ReAct. ReAct failures are 47% reasoning errors (including repetitive loops) and 23% empty or uninformative searches.
- ALFWorld, 134 unseen games, greedy decoding, 6 prompt permutations: best-of-6 ReAct succeeds on 71% against 45% for Act and 37% for BUTLER; the 6-prompt average is 57% and the worst ReAct trial (48%) beats the best Act and BUTLER trials. The ReAct-IM ablation (dense feedback thoughts only) scores 53 best-of-6.
- WebShop, 500 test instructions, one-shot prompt: ReAct 40.0 success rate against Act 30.1, IL 29.1 and IL+RL 28.7.
- After finetuning on 3,000 ReAct trajectories, 8B ReAct outperforms every prompting method at 62B, and finetuned 62B ReAct outperforms every prompting method at 540B (values appear only in a figure). Prompted ReAct is the worst of four methods at 8B and 62B.
- With GPT-3 (text-davinci-002), ReAct gets 30.8 on HotpotQA (500 random validation questions) and 78.4 on ALFWorld, whereas PaLM-540B gets 29.4 and 70.9.

## Limits

- Main experiments use PaLM-540B, which is not openly available; the GPT-3 check covers only a HotpotQA subset and ALFWorld.
- Prompted ReAct needs a strong model or finetuning, and the extraction records reasoning errors for 47% of ReAct failures against 16% for CoT; the authors suspect the loops come from greedy decoding.
- Large action spaces need more demonstrations than the context allows; all prompting methods stay well short of supervised HotpotQA (67.5 EM) and of expert humans on WebShop.
- There are no seeds, variance or significance tests; HotpotQA labels can be out of date, and the Wikipedia API is deliberately weak (exact page names).

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Chain of Thought]] — prerequisite-for
- [[Self-Consistency]] — prerequisite-for
- [[Reflexion]] — related
