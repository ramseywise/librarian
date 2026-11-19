---
title: Self-Instruct and Unnatural Instructions
tags: [llm, pretraining-and-data, pattern]
summary: "Two 2022 methods that prompt a language model to write its own instruction-tuning data from a few human seeds: Self-Instruct bootstraps 52K instructions from 175 seed tasks, Unnatural Instructions generates 240,670 examples from 15 seeds; both report noisy data and benchmark results near human-curated sets (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wang-2023-self-instruct.md
  - data/raw/papers/2026-11-07-honovich-2023-unnatural-instructions.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch08-dataset-engineering.md
---

# Self-Instruct and Unnatural Instructions

Both papers test whether a pretrained model can write its own instruction-tuning data with very little human effort, and whether tuning on it matches tuning on human-curated data. They are concurrent; Unnatural Instructions seeds from Super-NaturalInstructions and generates with InstructGPT002. Later pages cover rewriting instructions ([[Evol-Instruct (WizardLM and WizardCoder)]]) and code-seeded generation ([[OSS-Instruct (Magicoder)]]). Every figure is self-reported.

## Self-Instruct

The loop starts with a pool of 175 human-written tasks. Each round draws 8 tasks from the pool, asks GPT3 davinci for new instructions, labels each as classification (a small closed label set) or not, then writes instances either input-first or output-first. A ROUGE-L cutoff of 0.7 and some heuristics discard near-duplicates and junk; survivors join the pool. The same GPT3 is finetuned on the output through the OpenAI finetuning API. The filtered result: 82,439 instances across 52,445 instructions, of which 11,584 are classification tasks and 40,861 are not.

- Zero-shot SuperNI ROUGE-L climbs from 6.8 to 39.9, a gain of 33.1, close to InstructGPT001's 40.8 (119 tasks of 100 instances each, definition only, greedy decoding; GPT3 davinci 175B tuned for 2 epochs on the 52K instructions). T5-LM 11B gets 25.7 in that setup.
- GPT3 tuned on 50K T0 instances gets 37.9, below 39.9. Mixing Self-Instruct data into 50K SuperNI instances moves GPT3 from 49.5 to 51.6.
- On 252 expert-written user-oriented instructions, the Self-Instruct model trails InstructGPT001 by 5% when rating B counts as valid, and is well ahead of the T0-tuned and SuperNI-tuned GPT3 (two author-evaluators, A-D scale, one evaluator's ratings reported).
- In a 200-instance sample, 92% of instructions are valid, 79% of inputs appropriate, 58% of outputs correct, and 54% of instances valid in every field (a single author as annotator).
- Human-evaluation quality levels off beyond about 16K instructions, and the SuperNI improvement levels off at around hundreds of instructions. Replacing every output with InstructGPT003's and retuning beats the original data by 10% (share rated A).
- Generating the data cost about $600 in API fees, and tuning on all of it $338 (davinci at $0.02 per 1000 tokens, December 2022).

## Unnatural Instructions

text-davinci-002 is shown 3 Super-NaturalInstructions demonstrations and writes a fourth instruction, input and constraints (nucleus sampling); outputs come from greedy decoding and 3 simple filters apply. Template expansion then asks the model to reformulate each core task, collecting two alternative phrasings per example; the 15 seed examples grow to 240,670 in total. The student, T5-LM 11B, faces T0++, Tk-Instruct, FLAN-T5 and a T5-LM tuned on 64,000 Super-NaturalInstructions examples.

- At 64,000 examples the Unnatural-tuned model is ahead of the Super-NaturalInstructions baseline on T0 zero-shot, but behind it on the Super-NaturalInstructions test (T5-LM 11B).
- With paraphrases added (full 240,670) LMentry is 50.7; T0 zero-shot improves and Super-NaturalInstructions ROUGE-L drops.
- FLAN-T5 does better, using about 60 times the data. On BIG-bench Hard in QA format the core data and baseline are close (29.5 and 29.7).
- A manual check of 200 core examples found over half correct; 87 were wrong, 43 of those with a bad output; the 200 cover 117 distinct tasks.
- Ablations: using untuned GPT-3 to generate inputs costs 4.5 points and as output generator it collapses (2,000 examples, 1,500 steps, 3 seeds); dropping the constraints field from output generation costs 3 points (2,000 examples, Super-NaturalInstructions validation set); one-step input-and-output generation scores below two-step (2,000 examples, validation set, 3 seeds).

## Practitioner view

Huyen's chapter describes Alpaca: a Llama-7B tuned with text-davinci-003 pairs (52,000 of them) that came from the 175 Self-Instruct seeds, behaving like the teacher at 4% of its size (reported by the chapter).

## Limits

- Self-Instruct: it inherits the language model's tail-phenomena limits, and gains may favour frequent tasks; it may work best only for large models, with no size study; in the sample, 54% of instances are valid throughout, and outputs are the noisiest field; the evaluators were two authors who wrote the instructions; just GPT3 davinci was tried, with no seeds or variance and tuning details hidden behind the API. Inter-rater kappa is 0.57 in the body and 0.58 in Appendix B.2.
- Unnatural Instructions: 43.5% of a 200-example sample had an invalid instruction, input or output, which the authors concede; one student (T5-LM 11B) and one main generator; the core data imitates the Super-NaturalInstructions format, so other formats need the paraphrases; the main table looks like a single run without variance; harm analysis is a manual look only; the correctness annotation protocol is undescribed.
- The Unnatural extraction omits several result values (LMentry and BIG-bench Hard comparisons, per-example cost), so those comparisons are directional only here.

## See Also
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — prerequisite-for (the human-curated collections both papers compare against)
- [[Evol-Instruct (WizardLM and WizardCoder)]] — extends (rewrites instructions toward difficulty)
- [[OSS-Instruct (Magicoder)]] — extends (seeds generation with real code snippets)
- [[UltraChat and LaMini Instruction Datasets]] — extends
- [[Autodata Agentic Self-Instruct]] — related
- [[Synthetic Instruction Data: Curation and Verification]] — related
