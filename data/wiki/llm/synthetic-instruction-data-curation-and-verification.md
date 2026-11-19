---
title: "Synthetic Instruction Data: Curation and Verification"
tags: [llm, pretraining-and-data, concept]
summary: "Huyen's dataset-engineering chapter frames post-training data by quality, coverage and quantity and gives a practitioner checklist for synthesising, verifying, distilling and processing it; this page records her guidance and reported figures, and points to the paper pages for each generation method."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch08-dataset-engineering.md
  - data/raw/papers/2026-11-08-llm-engineers-handbook-ch05-supervised-fine-tuning.md
---

# Synthetic Instruction Data: Curation and Verification

Chip Huyen's chapter (O'Reilly, written in 2024) addresses how a practitioner should curate, synthesise, verify and process training data, chiefly for post-training, so that a model receives data with enough quality, coverage and quantity. The figures here are quoted by the chapter from other work in the book and were not measured by it (reported).

## Generation methods, by page

- Hand-curated small sets: [[LIMA: Small Curated Instruction Data]].
- Task-collection tuning and its scaling: [[Flan-PaLM Instruction Finetuning Scaling]].
- Model-written instructions from seeds: [[Self-Instruct and Unnatural Instructions]]; harder rewrites: [[Evol-Instruct (WizardLM and WizardCoder)]]; code-seeded: [[OSS-Instruct (Magicoder)]].
- Large ChatGPT-generated sets: [[UltraChat and LaMini Instruction Datasets]].

## Guidance (Huyen)

Her definition of quality: data that is relevant, aligned with the task, consistent, correctly formatted, sufficiently unique and compliant. Her recommendations:

- Fit the data's shape to the training phase: raw sequences for self-supervised training, (instruction, response) pairs for supervised tuning, (instruction, winning, losing) triples for preference tuning, or ((instruction, response), score) for reward data.
- Build the mix to mirror how the application is really used, or compare candidate mixes through small-model scaling experiments.
- To judge whether more data is worth collecting, finetune on 25%, 50% and 100% of what exists and plot the curve. A small dataset suits PEFT on a stronger model; a large one suits full finetuning of smaller models. Staging the data (self-supervised before supervised, less relevant before relevant, synthetic before real) lowers how much high-quality data is required.
- Reverse instruction guards against hallucinated long outputs: begin from existing high-quality long-form content and have an AI write the prompts that would draw it out, so the responses stay human-written.
- Check synthetic data by running it, or with unit tests, AI judges, classifiers, back-translation, topic checks or heuristics. When a judge compares two answers, query it twice with the order swapped and accept a triplet only if the winner is the same both times.
- Blend synthetic with human data instead of substituting one for the other; when bootstrapping, train only on self-generated data that passed verification.
- Look at dataset licences and provenance, and at a model's licence before distilling from it, since many prohibit using outputs to train rivals.
- Processing order: inspect (length and token distributions, annotator disagreement, reading examples), then deduplicate (pairwise comparison, hashing such as MinHash or a Bloom filter, dimensionality reduction), then clean HTML and PII, then convert to the model's chat template. Retain a copy of the original data and sequence steps by cost.
- Annotation guidelines and evaluation guidelines are one and the same.

## Reported figures

- Llama 3 data mix, per phase (pre-training, SFT, preference finetuning): general English 50%, 52.66%, 81.99%; pre-training/SFT/preference shares for coding are 17, 14.89 and 6.93, for multilingual 8, 3.01 and 5.19, and for math and reasoning 25, 21.19 and 5.89. Exam-like data (8.14) and long context (0.11) occur in SFT only.
- Llama 3's coding pipeline generated problems, solutions and unit tests, repaired failures, translated across languages and back-translated; over 2.7 million synthetic coding examples went into Llama 3.1 SFT, retained only if they passed parsers, linters and AI-written unit tests.
- Nemotron-4-340B-Instruct drew 98% of its instruction and preference finetuning data from Mixtral-8x7B-Instruct-v0.1 output and surpassed that generator; the chapter stresses this was one model iteration.
- MetaMath rewrote 15,000 MATH and GSM-8K examples into almost 400,000, and models trained on them beat larger models on related math benchmarks (no accuracy given).
- For finetuning Llama 2-7B, synthetic math data came close to real data and showed no obvious saturation up to roughly one million samples (no accuracy given).
- Stanford Natural Language Inference corpus: at 100 examples the more advanced models finetune better, and at 550,000 five OpenAI models perform alike.
- Duplicating 0.1% of the data 100 times pulls an 800M model down to a 400M model's level, while the other 90% of tokens remain unique.
- Databricks said stripping stray Markdown and HTML tokens raised accuracy by 20% and shortened inputs by 60% (model, dataset and metric not given).
- DistilBERT, trained from scratch with BERT as teacher, is 40% smaller, retains 97% of language comprehension and runs 60% faster. BuzzFeed's LoRA-tuned Flan-T5, trained on text-davinci-003 outputs, lowered inference cost by 80%, quality unclear.
- Model collapse means irreversible defects from recursive training on AI-generated data. The chapter says it cannot be avoided when the whole training set is synthetic, that mixing in real data averts it, and that no paper gives a ratio. Imitating a proprietary model carries over its style but may not carry its factual accuracy or generalization beyond the training data.
- Annotations made in the later half of a session are lower in quality, probably from fatigue (no numbers). One Pixel Attack: changing one pixel alone causes errors on 16.04% of ImageNet test images and on 67.97% of CIFAR-10 ones.

## An instruction set built from crawled articles (LLM Engineer's Handbook, ch. 5)

Iusztin and Labonne used GPT-4o-mini over 1,000 to 2,000 character chunks of their crawled articles to produce 3,335 instruction-answer pairs, for under 0.5 dollars (self-reported). They rate instruction data for accuracy, diversity and complexity, and prefer comparative judge scoring with randomised answer order, length normalisation and a jury of several models, aiming for about 80% judge-human agreement. They add the evaluation set to the deduplication stage to decontaminate automatically. They recommend sets of 1 million or more samples for a general instruct model, 100 to 100,000 for a task-specific one, and as few as 1,000 high-quality samples for models around 70B (citing LIMA); the chapter gives Yi, OpenHermes and Dolphin, and Llama 3 as the basis. The worked fine-tune is not evaluated in the chapter.

## Limits

- This is a book chapter. Most figures come from other work, and many have a sentence of setup or none; the Databricks 20% and 60% names no model, dataset or metric.
- It dates from 2024, so statements about models and licences, and the remark that no model-collapse paper offers a safe synthetic-to-real ratio, could be out of date.
- The chapter itself notes that the successes of Nemotron-4 and of Li et al. with synthetic data concern one model iteration.
- Its scope is post-training data; pre-training lessons appear only where they are insightful.

## See Also
- [[Post-Training Reasoning Data Primer]] — related
- [[Rejection Sampling Fine-Tuning]] — related (verification-filtered self-generated data)
- [[Autodata Agentic Self-Instruct]] — related
- [[LIMA: Small Curated Instruction Data]] — instance-of
- [[Self-Instruct and Unnatural Instructions]] — instance-of
- [[Back-Translation with Monolingual Data]] — related
- [[GPT3Mix: LLM Text Augmentation]] — related
- [[TinyStories Synthetic Corpus and GPT-Eval]] — related (synthetic pretraining corpus rather than instruction data)
