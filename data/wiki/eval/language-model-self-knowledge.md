---
title: Language Model Self-Knowledge
tags: [eval, concept]
summary: "Two 2022-23 ways to test whether a model knows what it knows: Kadavath et al. have models score their own samples (P(True)) or train a head to predict whether they will answer correctly (P(IK)), and Yin et al.'s SelfAware set (1,032 unanswerable questions) scores whether a model voices uncertainty, with GPT-4 below a human F1 of 84.93 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-kadavath-2022-language-models-mostly-know-what.md
  - data/raw/papers/2026-11-08-yin-2023-do-large-language-models-know.md
---

# Language Model Self-Knowledge

Two papers probe whether a model can tell what it knows. They differ in what counts as evidence: Kadavath et al. (arXiv 2207.05221, preprint) read the model's probabilities, while Yin et al. (Findings of ACL 2023) read its words.

## P(True) and P(IK)

Kadavath et al. test pretrained Anthropic models from 800M to 52B parameters. **P(True)** is the probability a model gives to the proposition that a specific sample is the correct answer. **P(IK)** ("I know") is the probability it gives to answering a question correctly when sampling at temperature 1; its ground-truth value is the fraction of such samples that are correct. P(True) is prompted, not trained; P(IK) is learned with a value head.

- Large models were well calibrated on lettered multiple choice and True/False formats (BIG-bench, MMLU, TruthfulQA, LogiQA, QuALITY). Replacing an option with "none of the above" lowered accuracy and calibration, and 20-shot did not fix it (MMLU, BIG-bench, 52B).
- A 52B RLHF policy that looked badly miscalibrated on MMLU, MMLU True/False and TruthfulQA (5-shot) was largely fixed by a single temperature.
- Zero-shot P(True) on the model's own samples was poorly calibrated, sitting near 50% (TriviaQA, Lambada, arithmetic, GSM8k, Codex). Showing the model five of its own temperature-1 samples improved self-evaluation on short-answer tasks, and the authors read the growth with model size as verification being easier than generation. These are read from plots.
- A P(IK) classifier trained only on TriviaQA was weak on LAMBADA but much better when trained on all tasks (52B, ground truth binarised at 0.5). In one worked example, P(IK) for an obscure trivia question rose when relevant Wikipedia text was added to the context.
- Two 12B models, A and B, had slightly higher P(IK), by about 6 points, on questions only they answered correctly (TriviaQA test).

All of this is self-reported. P(IK) finetuning used a batch of 7,680 and a learning rate one third of pretraining, because the soft labels are noisy.

## SelfAware

Yin et al. pair 1,032 unanswerable questions with 2,337 answerable ones. The unanswerable ones were filtered from 2,858 collected from Quora and HowStuffWorks by unanimous agreement of three annotators; by manual analysis of 100 of them, 27% were subjective, 25% had no scientific consensus, 23% philosophical, 15% imagination and 10% had too many variables. A response counts as uncertain if any 5-word window has SimCSE similarity above 0.75 to one of 16 reference uncertainty sentences; at 0.75 the detector reached precision 100.00 and recall 85.00 against manual labels (100 text-davinci-002 direct responses). F1 treats unanswerable as positive. Twenty models were tested with no training in three input forms: direct, instruction and in-context.

- Human self-knowledge F1 was 84.93, the mean of two volunteers on 100 random samples. GPT-4 (gpt-4-0314, instruction form, 100 instances) reached the highest F1 of the models tested but stayed well below that.
- In-context examples raised davinci's self-knowledge by 27.96 over the direct form. Under in-context learning text-davinci-001 scored F1 65.12 and text-davinci-002 66.46, against 55.5 for davinci.
- F1 rose with model size in all three forms, most under in-context learning. Instruction tuning raised LLaMA-family scores: Vicuna-13B beat LLaMA-65B.
- Closed-book accuracy on the answerable questions rose from 2.48 (text-ada-001) to 42.64 (GPT-4).

## Limits

Kadavath: only pretrained models, and the authors expect RLHF models to be less well calibrated. Nearly all results are plots with no seeds, error bars or significance tests, and few-shot examples for P(True) come from the test set. Small models look calibrated on hard tasks only by predicting P(True) near 0. P(IK) may track question difficulty rather than self-knowledge, since the A/B difference is only about 6%. Deception is not addressed, and the text has a "section XYZ" placeholder. Yin: reference sentences come only from GPT-3 and InstructGPT outputs, only three input forms were tried, and each model ran once with no error bars. GPT-4 was scored on only 100 instances and the human benchmark is two volunteers on 100 samples. Uncertainty is judged by surface similarity, not calibration, and the extraction flags that in-context examples may teach the phrasing "the answer is unknown" rather than awareness (its own inference). Models are from 2023, and the davinci endpoints are deprecated.

## See Also
- [[TruthfulQA]] — related (one of the calibration tasks in the Kadavath study)
- [[Hidden-State Hallucination Probes]] — alternative-to (reads truth from internal activations rather than from the model's stated probabilities)
- [[SelfCheckGPT]] — alternative-to (checks answers by sampling consistency instead of a model's own probability)
- [[Logprobs as Confidence Signal]] — related (probabilities used as a confidence signal)
