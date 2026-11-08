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

Two papers probe whether a model can tell what it knows. Kadavath et al. (arXiv 2207.05221, preprint) work from the model's probabilities. Yin et al. (Findings of ACL 2023) work from its text outputs and, per the extraction, avoid task-specific training.

## P(True) and P(IK)

Kadavath et al. test pretrained Anthropic models from 800M to 52B parameters. **P(True)** is the model's own probability that one of its samples is a correct answer. **P(IK)** ("I know") is the probability it gives to answering a question correctly when sampling at temperature 1; its ground-truth value is the fraction of such samples that are correct. P(True) is prompted, not trained; P(IK) is learned with a value head.

- Large models were well calibrated on lettered multiple choice and True/False formats (BIG-bench, MMLU, TruthfulQA, LogiQA, QuALITY). Replacing an option with "none of the above" lowered accuracy and calibration, and 20-shot did not fix it (MMLU, BIG-bench, 52B).
- A 52B RLHF policy that looked badly miscalibrated on MMLU, MMLU True/False and TruthfulQA (5-shot) was largely fixed by a single temperature.
- P(True) scored on the model's own samples without examples was poorly calibrated, sitting near 50% (TriviaQA, Lambada, arithmetic, GSM8k, Codex). Showing the model five of its own temperature-1 samples improved self-evaluation on short-answer tasks, and the authors read the growth with model size as verification being easier than generation. These are read from plots.
- A P(IK) classifier trained only on TriviaQA was weak on LAMBADA but much better when trained on all tasks (52B, ground truth binarised at 0.5). In one worked example, P(IK) for an obscure trivia question rose when relevant Wikipedia text was added to the context.
- Two 12B models, A and B, had slightly higher P(IK), by about 6 points, on questions only they answered correctly (TriviaQA test).

All of this is self-reported. P(IK) finetuning used a batch of 7,680 and a learning rate one third of pretraining, because the soft labels are noisy.

## SelfAware

Yin et al. combine 1,032 unanswerable questions and 2,337 answerable ones. The unanswerable ones were filtered from 2,858 collected from Quora and HowStuffWorks by unanimous agreement of three annotators; by manual analysis of 100 of them, 27% were subjective, 25% had no scientific consensus, 23% philosophical, 15% imagination and 10% had too many variables. A response counts as uncertain when some 5-word window comes within SimCSE similarity 0.75 of any of 16 reference sentences expressing uncertainty; at 0.75 the detector reached precision 100.00 and recall 85.00 against manual labels (100 text-davinci-002 direct responses). F1 treats unanswerable as positive. Twenty models were tested with no training in three input forms: direct, instruction and in-context.

- Human self-knowledge F1 was 84.93, the mean of two volunteers on 100 random samples. GPT-4 (gpt-4-0314, instruction form, 100 instances) reached the highest F1 of the models tested but stayed well below that.
- Compared with the direct form, in-context examples lifted davinci's self-knowledge by 27.96. Under in-context learning text-davinci-001 scored F1 65.12 and text-davinci-002 66.46, against 55.5 for davinci.
- F1 rose with model size in all three forms, most under in-context learning. Instruction tuning raised LLaMA-family scores: Vicuna-13B beat LLaMA-65B.
- Closed-book accuracy on the answerable questions ranged from 2.48 for text-ada-001 up to 42.64 for GPT-4.

## Limits

Kadavath: only pretrained models, and the authors expect RLHF models to be less well calibrated. Nearly all results are plots with no seeds, error bars or significance tests, and few-shot examples for P(True) come from the test set. On hard tasks small models appear calibrated only because they predict P(True) close to 0, and P(IK) may follow question difficulty rather than self-knowledge, given the A/B gap of only about 6%. Deception is not addressed, and the text has a "section XYZ" placeholder. Yin: the reference uncertainty sentences were drawn only from GPT-3 and InstructGPT outputs, only three input forms were tried, and each model ran once with no error bars. GPT-4 was scored on just 100 instances, and the human benchmark rests on two volunteers and 100 samples. Uncertainty is judged by surface similarity, not calibration, and the extraction raises, as its own inference, that in-context examples might teach a stock phrase of uncertainty instead of awareness. Models are from 2023, and the davinci endpoints are deprecated.

## See Also
- [[TruthfulQA]] — related (one of the calibration tasks in the Kadavath study)
- [[Hidden-State Hallucination Probes]] — alternative-to (reads truth from internal activations rather than from the model's stated probabilities)
- [[SelfCheckGPT]] — alternative-to (checks answers by sampling consistency instead of a model's own probability)
- [[Logprobs as Confidence Signal]] — related (probabilities used as a confidence signal)
- [[Contrast-Consistent Search]] — related (reads truth from hidden states instead of probabilities)
- [[ChatGPT Information Extraction Evaluation]] — related (verbalised confidence measured on extraction tasks)
- [[Open NLP Questions Large Language Models Do Not Solve]] — related
