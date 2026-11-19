---
title: OSS-Instruct (Magicoder)
tags: [llm, pretraining-and-data, pattern]
summary: "OSS-Instruct shows a teacher LLM a random open-source code snippet and has it write a self-contained problem and solution, aiming for more diverse and less biased code instruction data than Self-Instruct or Evol-Instruct; Magicoder models trained on about 75K such pairs are reported to beat the base models on HumanEval+ (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wei-2023-magicoder.md
---

# OSS-Instruct (Magicoder)

OSS-Instruct has an LLM invent a coding problem and a solution grounded in a seed snippet of real open-source code. The paper's hypothesis is that grounding the teacher in real snippets reduces the built-in bias of LLM-written data and gives more varied, realistic and controllable instruction data than [[Self-Instruct and Unnatural Instructions]] or [[Evol-Instruct (WizardLM and WizardCoder)]].

## Method

The teacher, gpt-3.5-turbo-1106, receives a random snippet of 1 to 15 lines from starcoderdata and writes a standalone problem with its solution. Roughly 75K cleaned pairs tune either of two bases, CodeLlama-Python-7B and DeepSeek-Coder-Base-6.7B, giving the Magicoder models. A second tuning stage on evol-codealpaca-v1 produces MagicoderS, so the two generators are used together.

## Results (all self-reported)

- MagicoderS-CL-7B tops ChatGPT on HumanEval+ (CodeLlama-Python-7B base; OSS-Instruct first, Evol-Instruct second; greedy decoding under EvalPlus). OSS-Instruct alone also improves HumanEval+ over the base (75K samples, 2 epochs, greedy). The extraction gives no values for either.
- Tuning straight on 75K comment-and-function pairs mined from the same seed corpus brings no HumanEval+ improvement and reduces MultiPL-E.
- A weaker teacher, Mixtral-8x7B-Instruct, writes data whose student still outscores that teacher on HumanEval+ (20K samples, CodeLlama-Python-7B, 2 epochs).
- Of three synthetic code datasets, OSS-Instruct has the least TF-IDF overlap with HumanEval (max similarity per problem across 164 problems; Self-Instruct 0.169 and Evol-Instruct 0.131; the extraction omits the OSS-Instruct value).
- Tuning on 32K non-Python OSS-Instruct samples still improves Python HumanEval+ (CodeLlama-Python-7B, 2 epochs).
- Dropping noisy partial-code samples slightly hurts HumanEval+ (68K cleaned against 75K raw, which scores 55.5).
- Decontamination found only 9 further samples to remove, because the starcoderdata seeds were already decontaminated.

## Limits

- Tests stop at 7B parameters.
- The OSS-Instruct prompt is elaborate and may call for a strong teacher; weaker ones may write implausible data.
- Main tables are single runs with greedy decoding and no seeds or intervals; baseline scores come from the EvalPlus leaderboard and the WizardCoder paper rather than reruns; WizardCoder-CL-7B is left out of MultiPL-E because of latency.
- The DeepSeek-Coder comparison is short since that model's data and instruction tuning are undisclosed, and token counts differ (+90M/+240M versus +2B).
- Most data comes from gpt-3.5-turbo-1106, and only the Mixtral 20K experiment separates the method from distillation off the teacher.
- Loss masking and chat template are not described.

## See Also
- [[Self-Instruct and Unnatural Instructions]] — prerequisite-for
- [[Evol-Instruct (WizardLM and WizardCoder)]] — alternative-to
- [[Synthetic Instruction Data: Curation and Verification]] — related
