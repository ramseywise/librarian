---
title: MMLU, C-Eval and CMMLU Knowledge Exams
tags: [eval, reasoning-and-math, comparison]
summary: "Three multiple-choice exam benchmarks for broad subject knowledge: MMLU (57 English tasks, 14,079 test questions) and its Chinese counterparts C-Eval (52 subjects) and CMMLU (67 subjects); what each measured about 2020-2023 models, and how prompt style and answer extraction moved the scores."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-hendrycks-2021-measuring-massive-multitask-language-understanding.md
  - data/raw/papers/2026-11-08-huang-2023-c-eval.md
  - data/raw/papers/2026-11-08-li-2024-cmmlu.md
---

# MMLU, C-Eval and CMMLU Knowledge Exams

All three benchmarks are four-way multiple-choice tests drawn from exam-style questions across many subjects. C-Eval and CMMLU follow the MMLU format for Chinese. Numbers below are each paper's own (self-reported) and come from 2020-2023 models.

## MMLU (Hendrycks et al., 2021)

Fifty-seven tasks grouped as humanities, social science, STEM and other; each is scored zero-shot and few-shot. The split is 15,908 questions: 5 dev questions per subject, 1,540 validation and 14,079 test.

- Few-shot GPT-3 175B scores 43.9% on average (up to 5 demonstrations); GPT-3 at 2.7B, 6.7B and 13B stays close to the 25% chance level. Zero-shot GPT-3 175B scores about 37.7%.
- UnifiedQA, an 11B T5-based model trained on other QA data but never on MMLU, reaches 48.9%, ahead of the much larger few-shot GPT-3.
- Unspecialised Mechanical Turk workers score 34.5%; the estimated expert ceiling is about 89.8%, taken from 95th-percentile exam takers and partly guessed where no statistics existed.
- GPT-3 is lopsided: 69% on US Foreign Policy down to 26% on College Chemistry, and 9 of its 10 lowest-accuracy tasks are calculation-heavy STEM subjects. Its Elementary Mathematics result (29.9%) is below both College Mathematics (35.0%) and College Medicine (47.4%).
- Calibration: zero-shot confidence can differ from accuracy by up to 24%, the few-shot gap is up to 14%, and the confidence-accuracy correlation is r=0.81 few-shot against r=0.63 zero-shot.
- The authors consider verbatim memorisation unlikely: the model's log-probability of a question correlates negatively with accuracy (r=-0.43 zero-shot, r=-0.56 few-shot).
- Adding about 2,000 Professional Law examples gives RoBERTa-base 32.8%; continued pretraining on about 1.6M legal case summaries first raises it to 36.1%.

## C-Eval (Huang et al., 2023)

52 subjects in the Chinese exam setting, with a 1:9 validation-to-test split modelled on MMLU (1,346 validation questions) and private test labels to limit contamination. C-Eval HARD is a subset of 8 math, physics and chemistry subjects needing advanced reasoning.

- In zero-shot answer-only mode, GPT-4 alone averages over 60%. GLM-130B, the strongest Chinese-oriented model, is 7.0 points behind ChatGPT overall: 2.2 behind on social science, 1.1 on humanities and 12.3 on STEM.
- On C-Eval HARD most models hover around chance; GPT-4, ChatGPT and Claude are the only ones at least 10 points above it.
- Five-shot prompting lowers accuracy for instruction-tuned models such as GLM-130B (44.0 to 40.3); the authors cite instruction-finetuning work to explain this.
- Chain-of-thought gives comparable or lower averages than answer-only for all models tested. GPT-4 improves on College Physics (50.6 to 60.2), but on C-Eval HARD CoT lowers ChatGPT from 41.4 (five-shot answer-only) to 35.0, and LLaMA-65B from 31.7 to 21.4.
- The validation average follows the test average closely (GPT-4 zero-shot: 66.7 and 66.4), so the authors propose it as a fast development signal. Shuffling the option order five times moved ChatGPT's zero-shot average little (variance 0.6, average 50.5).
- Instruction-tuned models around 10B parameters score below 40%, which the authors say contradicts parity claims made for Vicuna and Alpaca.

## CMMLU (Li et al., 2024)

11,528 questions in 67 subjects with a 5-shot dev set per subject, scored by macro average. Two answer strategies are compared: next-token prediction (choose whichever of the letters A to D the model rates highest) and free generation with the choice pulled out by regular expressions.

- GPT-4 is best at 70.95% five-shot. Most of the 20-plus models stay under 60%, which is the pass mark in Chinese exams. Among open multilingual models LLaMA2-70B is best, and Baichuan2-13B (base) the best Chinese open model, beating ChatGPT at 13B parameters. STEM is GPT-4's hardest category (65.23) against Other (74.79).
- A chain-of-thought prompt cuts zero-shot accuracy overall for most models (Xverse-13B-Chat from 52.96 to 39.27), although ChatGPT's STEM score edges up (45.22 to 46.58) even as its total falls. A rise in unmatched regex responses accompanied the Xverse drop.
- Few-shot examples help base models, while SFT and RLHF models decline with one example and show no consistent trend after.
- Negation questions (about 10.7% of the data) lower most models' accuracy; sub-option questions (about 10.8%) lower accuracy by 10-20% (GPT-4 zero-shot 51.14 against 69.74).
- Next-token scoring came out ahead of free generation for each of six chat models (Baichuan2-13B-Chat five-shot 59.89 against 54.44); regex failures reach 6.44% for that model.
- CMMLU correlates with RACE-M (r=0.973) and PIQA (r=0.88) across six models.
- Exact-match overlap with C-Eval is 74 questions and with M3KE 158 (about 1% of CMMLU); label noise is estimated at about 2%.

## What the three show together

Chain-of-thought and few-shot prompting did not reliably help on either Chinese exam; both papers report drops for chat or instruction-tuned models. See [[Benchmark Prompt Format Sensitivity]] for the wider pattern, and [[Chain-of-Thought Prompting]] for the method.

## Limits

- All three are multiple-choice only and report a single run per model with no confidence intervals (C-Eval's only variance figure is over option permutations); MMLU is text-only. Models are 2020-2023 vintage, so the figures are dated.
- Contamination is mitigated or checked only indirectly (MMLU log-probability correlation, C-Eval private test labels, CMMLU overlap counts), and not excluded.
- MMLU: only GPT-3 and UnifiedQA evaluated at scale, so model size cannot be separated from pretraining data; UnifiedQA is sensitive to input format; ground-truth labels were not audited.
- C-Eval: no decoding settings are given; zero-shot CoT is missing because its answers could not be extracted reliably; three Chinese commercial models were not evaluated (not authorised).
- CMMLU: GPT-4 and ChatGPT were evaluated at different dates (May and July 2023) with free generation, so they are not directly comparable with logit-scored open models; the correlation with other benchmarks rests on six models.

## See Also
- [[AGIEval]] — alternative-to (human-exam benchmark in English and Chinese)
- [[CLUE Chinese Benchmark]] — related (earlier Chinese language-understanding suite)
- [[Eval Contamination Defenses]] — related
- [[Minerva Quantitative Reasoning]] — related (reports MMLU-STEM results)
- [[LLaMA 1 and Llama 2 Open Foundation Models]] — related
- [[Qwen and Qwen2.5 Technical Reports]] — related
