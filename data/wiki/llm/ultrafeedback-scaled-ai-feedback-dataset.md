---
title: UltraFeedback Scaled AI Feedback Dataset
tags: [llm, preference-and-alignment, reference]
summary: "A GPT-4-annotated preference and critique dataset over 63,967 instructions and 17 models, built with aspect decomposition and joint scoring of four completions, plus the UltraRM reward model and UltraCM critique model trained on it."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-cui-2023-ultrafeedback.md
---

# UltraFeedback Scaled AI Feedback Dataset

Cui et al. (ICML 2024) investigate whether GPT-4 feedback, collected at scale and across varied data, can stand in for human preference labels when aligning open-source chat models. Their working assumption is that breadth of instructions and responses, together with annotation designed to reduce bias, makes AI feedback dependable and cheap to scale. They cite Constitutional AI and RLAIF ([[Constitutional AI and RLAIF]]) as the earlier AI-feedback work. Both [[SimPO and PRO Reference-Free Preference Optimization]] and [[Tulu 3 Post-Training Recipe and RLVR]] train or run ablations on UltraFeedback.

## Construction

- Instructions: 63,967 drawn from six public sets (TruthfulQA, FalseQA, Evol-Instruct, UltraChat, ShareGPT, FLAN) and decontaminated. 13-gram matching against the AlpacaEval, Evol-Instruct and UltraChat test sets turned up 48 contaminated samples.
- Completions: 255,864 in all. Each instruction gets answers from 4 models picked at random out of a pool of 17, with a random principle placed in the system prompt.
- Annotation: GPT-4 scores with the work split by aspect, using score rubrics, and rates all four completions together with written rationales.
- Models trained on it: UltraRM and the critique model UltraCM on LLaMA2-13B, followed by best-of-n and PPO runs on UltraLM-13B.

## Results

Self-reported unless noted.

- UltraRM, trained on a mixture of UltraFeedback, SHP, Summarize and Anthropic Helpful (749,702 pairs, of which UltraFeedback supplies 340,025, SHP 198,556, Anthropic Helpful 118,263 and Summarize 92,858), averages 71.0% preference accuracy across four human preference sets (Anthropic Helpful, WebGPT, Summarize, SHP). With UltraFeedback fine-grained scores alone the average is 66.8%. Using overall scores in the mix drops its average to 69.9%, mainly on WebGPT (62.0 against 65.2).
- On AlpacaEval against text-davinci-003 (UltraLM-13B, 16 samples at temperature 1, GPT-4 judge), a single sample wins 76.53%, best-of-2 wins 84.64% and best-of-16 under UltraRM wins 91.54%.
- PPO against UltraRM lifts UltraLM-13B to an average win rate of 69.7 across three benchmarks, a 16.8 percent improvement on the starting model (80 PPO iterations, 512 samples each, learning rate 1e-6, mini-batch 64; judged by GPT-4 at temperature 0.7). Across nine exact-match benchmarks, the average only moves from 63.3 to 64.3.
- UltraCM-13B scores 5.92 out of 7 on critique quality as rated by GPT-4 (9 datasets, 50 instructions each). Baselines in the paper's own setup: gpt-3.5-turbo 6.17, SelFee-13B 5.41, Shepherd-13B 3.23.
- Agreement was measured on 400 pairs with 3 student annotators, ties counted, and a chance level of 33%: GPT-4 matches an individual human 59.7% of the time and the human majority 68.6%, while humans match one another around 56.4 to 58.1%.
- On a 57-item reasoning subset with expert-set answers, GPT-4's judgements come out win 42.1, tie 26.3, lose 31.6, so it undervalues reasoning.
- The SteamSHP baseline shows heavy position bias on Anthropic Helpful: 72.0 with the chosen answer first, 38.8 with the rejected one first, 55.4 on average.

## Limits

- The premise that GPT-4 imitates human annotators is hard to confirm, because GPT-4's agreement with humans (59.7%, or 68.6% against the majority) is about the same as humans' agreement with each other.
- Data are single-turn dialogues, weak on maths and code, and contain no safety-focused conversations.
- Decontamination covers three test sets only.
- Evaluation depends on GPT-4 as judge, which undervalues reasoning.
- The annotation prompt, the PPO KL settings, hardware, compute and seeds are not given. The comparison of fine-grained and overall scores is confounded, since joint scoring and separate calls differ too.
- The paper's impact statement concedes annotation biases of position, length and style.

## See Also
- [[Constitutional AI and RLAIF]] — related (AI feedback standing in for human labels)
- [[Bradley-Terry Preference Model]] — prerequisite-for (the pairwise ranking loss, with a margin, behind UltraRM)
- [[SimPO and PRO Reference-Free Preference Optimization]] — related (trained on this dataset)
- [[LLM-as-Judge Evaluation]] — related (GPT-4 as annotator and judge)
