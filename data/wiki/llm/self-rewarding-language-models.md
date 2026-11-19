---
title: Self-Rewarding Language Models
tags: [llm, preference-and-alignment, pattern]
summary: "One model both answers and judges: LLM-as-a-Judge scores on its own samples build the DPO pairs for each next iteration; on Llama 2 70B three iterations improved instruction following and judging, with length growth uncontrolled."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-yuan-2024-self-rewarding-language-models.md
---

# Self-Rewarding Language Models

Yuan et al. test whether one LLM can serve as its own reward model by being prompted as a judge inside iterative DPO, so that instruction following and reward modelling improve together over rounds. The judge is not frozen; it shares weights with the policy, which sidesteps the bottleneck of human feedback.

## Loop

1. M1 is Llama 2 70B fine-tuned on two seed sets from Open Assistant: 3,200 instruction-following examples (IFT) and 1,630 judging examples (EFT), each an evaluation prompt answered with a justification and a score out of 5. See [[OpenAssistant OASST1 Conversation Trees]].
2. In each round, a fixed Llama 2-Chat 70B writes new prompts using 8-shot Self-Instruct; the current model answers each with N=4 sampled responses and grades every one itself, averaging 3 judgements.
3. The best- and worst-graded responses become a DPO pair (the AIFT data), and the next model (M2, then M3) is DPO-trained ([[DPO Loss and Implicit Reward]]) starting from its predecessor.

## Results

All figures are (self-reported), Llama 2 70B, three rounds, one setting.

- AlpacaEval 2.0 win rate against GPT-4 Turbo climbs each round and M3 reaches 20.44% (GPT-4 judge, without length control). In Table 1 as printed, M3 sits above GPT-4 0613, Gemini Pro and Claude 2, though those systems rely on proprietary data or distilled targets.
- GPT-4 judging head to head: M3 beats the SFT baseline 62.5% to 9.8%, and M2 beats M1 55.5% to 11.7%. The authors, acting as annotators (50 prompts, 3 per pair, majority vote), concur, giving M3 66.0% wins.
- On a held-out Open Assistant set, the judge's pairwise agreement with human rankings goes from 65.1% for the SFT model to 81.7% for M3; most of that comes from EFT data (M1 against SFT: 65.1% to 78.7%).
- With the SFT model judging, the additive 5-point prompt agrees with humans 65.1% of the time, versus 26.6% for the multiple-choice prompt from Li et al. 2024.
- MT-Bench overall: 6.78 for M1, 7.25 for M3. Maths, code and reasoning improve less (3.83 up to 4.17).
- Mean AlpacaEval response length goes from 1092 at M1 to 2552 at M3, in units the paper does not name.
- Dropping EFT data leaves the loop with many fewer usable pairs (541 and 429) and models behind M2 and M3. SFT on 11,254 examples the model scored 5/5 does not beat the SFT baseline (29% against 30%), and adding EFT to IFT does not change instruction following (30.5% against 30.9% wins).
- Standard NLP benchmarks stay flat or dip slightly: GSM8K moves from 56.80 (Llama 2) to 57.70 (M3) while ARC-challenge slips from 57.40 to 53.13.

## Limits

- The authors describe these as early findings, from three rounds in a single setting with no scaling study, and expect gains from self-reward to level off in realistic conditions.
- Responses lengthen over the rounds and length tracks judged quality; no main result is length-controlled.
- Reward hacking is not looked at, and both the policy and the GPT-4 evaluator are language models. There is no safety evaluation.
- Human evaluation was done by the authors, on 50 prompts. A frozen Llama 2-Chat 70B, rather than the model being trained, produced the prompts.
- Variance, seeds, optimiser, hardware and compute are all unreported, and no code or weights are mentioned.

## See Also
- [[DPO Loss and Implicit Reward]] — prerequisite-for (the preference-tuning step each iteration uses)
- [[Constitutional AI and RLAIF]] — alternative-to (AI feedback from a fixed separate model)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (the judging primitive reused as a reward)
- [[OpenAssistant OASST1 Conversation Trees]] — prerequisite-for (source of the IFT and EFT seed data)
- [[Preference Optimization Algorithms]] — prerequisite-for
