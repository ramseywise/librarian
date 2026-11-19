---
title: Prompt Programming and Task Location
tags: [prompting, concept]
summary: "Reynolds and McDonell argue that few-shot examples mainly locate a task the model already knows, so a well-formed 0-shot natural-language prompt can match or beat few-shot; evidence is one GPT-3 translation task, the rest is a qualitative design vocabulary (signifiers, memetic proxies, metaprompts)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-reynolds-2021-prompt-programming-large-language-models.md
---

# Prompt Programming and Task Location

Reynolds and McDonell (2021) ask whether the few-shot format makes GPT-3 learn a task at run time or only locates it. Their hypothesis: examples mainly locate an already learned task (**task location**) rather than meta-learn it, so good 0-shot prompts can match few-shot ones. They define **prompt programming** as the craft of writing prompts for an autoregressive LM much as one would write for a human author.

## The one quantitative test

Setup: WMT'14 French-to-English, SacreBLEU, GPT-3 API engines Babbage (6.7B inferred) and Curie (13B inferred); the GPT-3 paper's prompts reproduced, plus two custom prompts ("Simple Colon" and "Master Translator") at 0, 1 and 10 shots.

- A Simple Colon 0-shot prompt, just the two language names, beats the OpenAI-reported 0-shot on both engines, and on Curie beats the reported 1-shot and comes close to the reported 64-shot (38.3).
- With the Simple Colon format, 1-shot does worse than 0-shot on both engines. The authors blame semantic contamination, the example being read as part of one continuing narrative, which they saw by inspecting outputs and did not quantify. Simple Colon 10-shot is about equal to 0-shot.
- Master Translator 0-shot gives the best Babbage score.
- The authors assert the GPT-3 0-shot baselines were underestimated and that many of the weakest zero-shot prompts used in the GPT-3 paper, QA above all, would improve if worded more like natural language; no data beyond translation backs this.

## Design vocabulary

- **Direct task specification**: a 0-shot prompt telling the model to do a task it already knows.
- **Signifier**: a pattern that keys the intended behaviour, such as a task name, a compound description or a purely contextual cue like the colon prompt.
- **Memetic proxy**: a character or characteristic situation standing in for a complex intention.
- **Metaprompt**: a seed encapsulating a general intention that unfolds into a task-specific prompt once the task question is added. In the worked example, a prompt telling the model to split the problem into steps, run on f(f(3)) where f(x)=x*x, produced a stepwise answer on davinci at temperature 0, but the output is inconsistent (the first line gives 27, the correct value is 81).
- **Catastrophic failure**: the task is not attempted (continuing in French, blank output). The authors propose reporting these separately in benchmarks; that they explain the 0-shot gaps is proposed, not tested.

Other named methods in the paper: constraining behaviour and serialising reasoning.

## Limits

- Quantitative evidence is one task on two engines, mean BLEU only, no variance or significance; the authors cite budget and time.
- The published OpenAI numbers were not reproduced (0-shot gave 15.9 and 18.7 against 15.5 and 22.4; 1-shot gave 21.8 and 24.1 against 31.6 and 31.4); 64-shot was replaced by 10-shot; engine sizes are inferred.
- Metaprompt and serial-reasoning claims rest on single hand-picked examples; the paper flags derailment risk.
- The work targets the 2020 GPT-3 API; newer models and instruction tuning change the picture. The paper calls itself exploratory.

## See Also

- [[Prompts as Document Completion]] — related
- [[Few-Shot Prompting]] — prerequisite-for
- [[GPT-3 and Few-Shot In-Context Learning]] — related (the paper disputes the meta-learning reading of few-shot)
- [[Random-Label Demonstration Ablations]] — related (agrees with the premise that demonstrations are for task location)
- [[Zero-Shot Chain-of-Thought]] — related (the step-splitting metaprompt)
