---
title: Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)
tags: [llm, fine-tuning, concept]
summary: "Four 2021-2022 papers fine-tune a language model on many tasks rewritten as instructions or prompts and test it on held-out tasks: FLAN, T0, Super-NaturalInstructions (Tk-Instruct) and MetaICL. Each paper's result, with its setup, is below, along with where they disagree."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wei-2021-finetuned-language-models-zero-shot.md
  - data/raw/papers/2026-11-07-sanh-2021-multitask-prompted-training-enables-zero.md
  - data/raw/papers/2026-11-07-wang-2022-super-naturalinstructions.md
  - data/raw/papers/2026-11-07-min-2022-metaicl.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
---

# Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)

The four papers below share one test: tune a model on many tasks, then evaluate it on tasks it never saw. They differ in base model, task collection and what counts as unseen. FLAN's paper defines instruction tuning as finetuning on a set of datasets that are described through instructions. Every figure here is the papers' own (self-reported).

## FLAN (Wei et al., 2021)

LaMDA-PT 137B is finetuned on 62 text datasets in 12 task clusters, each verbalised with 10 hand-written instruction templates. For each held-out cluster a separate model is tuned with that cluster and its related clusters removed; a dataset is unseen only if nothing from its task cluster was in tuning.

- FLAN 137B zero-shot wins against GPT-3 175B zero-shot on 20 of 25 datasets (self-reported; best dev template, GPT-3 figures taken from Brown et al.). Against few-shot GPT-3 it wins on 10.
- Against GLaM 64B/64E zero-shot it wins on 13 of the 19 datasets with available numbers (self-reported; best dev template).
- Going from 1 to 7 tuning clusters moves held-out average accuracy from 49.9 to 63.5 (self-reported; NLI, commonsense and closed-book QA held out, clusters added largest first, 137B).
- Models of 8B and below do worse on held-out tasks after instruction tuning, while 68B and 137B do better (self-reported; average of 13 held-out tasks across sizes 422M to 137B).
- Natural-language instructions give a four-cluster held-out average of 55.2; no template gives 37.3 and dataset-name prompts give 46.6 and 47.0 (self-reported; zero-shot, NLI, reading comprehension, closed-book QA, translation).
- Adding datasets per cluster lifted held-out results by almost 10%, whereas adding templates changed little (self-reported; 1 versus 4 datasets per cluster, 1, 4 or 10 templates per dataset).
- On the SuperGLUE dev average, prompt tuning starting from FLAN reaches 78.1 with 32 training examples and 87.4 with the full set, against 63.8 and 79.1 starting from LaMDA-PT (self-reported).
- Tuning consumed under 2% of the pretraining steps.

## T0 (Sanh et al., 2021)

LM-adapted T5 (3B and 11B) is trained by maximum likelihood over a shuffled blend of 39 datasets (T0), 49 (T0+) or 55 (T0++), each shown through many PromptSource templates; P3, the Public Pool of Prompts, holds 2073 prompts over 177 datasets. Zero-shot evaluation holds out entire tasks: NLI, coreference, sentence completion and word-sense disambiguation plus 14 [[BIG-bench]] tasks, reporting median and interquartile range over prompts. Answers use rank classification: score each option by log-likelihood and take the top one.

- T0 11B equals or beats every GPT-3 model on 9 of 11 held-out datasets while being roughly 16x smaller (self-reported; T0 median over prompts, GPT-3 up to 175B with one prompt).
- On 14 BIG-bench tasks, some T0 variant beats every baseline (up to 68B) on all but StrategyQA (self-reported; zero-shot).
- Prompts per dataset: moving from 1 to 5.7 raised the median on 8 of 11 datasets; counting prompts written for other tasks (8.03 per dataset) raised it on 9 of 11 (self-reported ablation).
- Training on 39, 49 and then 55 datasets raised the median on each of the 5 held-out datasets, but variation across prompt wordings did not reliably fall.
- On RTE, GPT-3 davinci given those ten prompts sits near chance for the nine prompts not written for the task: median accuracy 52.96%, IQR 1.28% (self-reported; davinci assumed 175B).
- Stripping instructions from HellaSwag prompts takes the T0 11B median from 33.65% to 57.93% (self-reported).

## Super-NaturalInstructions (Wang et al., 2022)

This community-built meta-dataset has 1,616 tasks across 76 task types, each with a definition and positive and negative examples. 757 English tasks train; 154 evaluate (119 English, 35 cross-lingual). T5-11B (Tk-Instruct) and mT5-13B (mTk-Instruct) are tuned on instruction plus input and judged by ROUGE-L on open-ended generation.

- Tk-Instruct 11B outscores InstructGPT 175B on the 119 unseen English tasks (self-reported; definition plus two positive examples, text-davinci-001 scored on 20 instances per task); mTk-Instruct 13B does the same on the 35 non-English tasks.
- On the English track T0 11B is only a little above T5-LM.
- Held-out performance rises log-linearly with the number of training tasks up to 757 (self-reported; T5-3B, English track) and with model size from T5 small to xxl. The paper presents the size result as contradicting ZeroPrompt's claim of little size impact.
- Gains stop at roughly 64 instances per training task (T5-3B). Training T5-large on 757 tasks gives the same result as T5-3B on 128.
- A definition plus two positive examples was the strongest input encoding when training and test used the same one.

## MetaICL (Min et al., 2022)

GPT-2 Large (770M) is meta-trained by drawing a task, drawing k+1 examples, concatenating them and maximising the log-probability of the final label. At test time it reads k examples and picks the candidate with the highest conditional probability; the channel variant models the input given the label instead. No templates are used; an ablation adds instructions (channel MetaICL, 32 meta-train and 12 target tasks), and instructions improve MetaICL more than the multi-task zero-shot baseline. Evaluation spans 142 datasets, seven meta-train and target splits and 52 distinct target tasks.

- Channel MetaICL beats the strongest raw-LM baseline (Channel In-context) on the high-resource to low-resource split and is best in 6 of 7 settings (self-reported; GPT-2 Large, k=16).
- GPT-2 Large with MetaICL equals or beats GPT-J (6B) raw-LM baselines, but not everywhere: for non-QA to QA with unseen domains GPT-J gets 55.7/54.4 and Channel MetaICL 47.2/45.0.
- Plain multitask zero-shot training, with no in-context objective, mostly fails to beat the best raw LM at 770M. The paper presents this as contradicting FLAN and T0 at that size.
- Meta-training on diverse tasks beats a non-diverse set of 13, and accuracy levels off around k=16.

## Where the papers disagree

- Size: FLAN saw instruction tuning hurt at 8B and below; the T0 extraction records T0 finding gains at 3B; MetaICL saw plain multitask zero-shot fail to help at 770M. The extractions say direct comparison is hard because model type, size and splits differ.
- Super-NaturalInstructions reports a log-linear size effect against ZeroPrompt's claim.

## Xiao and Zhu's dataset figures

Xiao and Zhu cite the FLAN instruction-tuning collection (Longpre et al. 2023) as built from 1,836 tasks and holding 15 million samples, and describe earlier academic-task instruction datasets as spanning more than 100 NLP tasks and over a million samples, all in one format.

## Limits

- FLAN: assigning tasks to clusters is subjective; only short, usually one-sentence instructions were tried; the scaling ablation used one cluster split; context was 1024 tokens and data mostly English; tasks phrased as language modeling (commonsense, coreference) did not benefit; zero-shot DROP and SQuADv2 numbers for GPT-3 use same-passage exemplars and are not comparable.
- T0: zero-shot still trails models finetuned per task; the task taxonomy is heuristic and some held-out tasks may overlap the QA training data; the authors stay agnostic on why prompts help; differences from FLAN are untested hypotheses; contamination against C4 reaches 9.12% for HellaSwag and 5.2% for RTE hypotheses; steps, schedule and seeds are unstated, with one run and no significance tests.
- Super-NaturalInstructions: English-heavy with short responses; ROUGE-L is a weak proxy where copying the input scores high (rewriting, error correction); InstructGPT data may overlap the evaluation tasks; scaling analyses use T5-3B on the English track, one run; InstructGPT and GPT-3 were scored on just 20 instances per task.
- MetaICL: long contexts are needed; only a 770M causal LM and only classification or multiple-choice tasks were tried; meta-training plus fine-tuning still wins; choice of meta-training tasks causes non-negligible variance; random label words do relatively poorly.

## See Also
- [[Flan-PaLM Instruction Finetuning Scaling]] — extends (scales the FLAN recipe in tasks and model size, adding chain-of-thought data)
- [[XP3, BLOOMZ and mT0]] — extends (T0's recipe applied to multilingual models)
- [[Self-Instruct and Unnatural Instructions]] — alternative-to (model-generated instructions in place of curated task collections)
- [[LIMA: Small Curated Instruction Data]] — alternative-to (1,000 curated examples against large task mixtures)
- [[Few-Shot Prompting]] — prerequisite-for
- [[RLHF Pipeline]] — related (InstructGPT's SFT stage)
- [[UnifiedQA Format-Agnostic QA]] — related
- [[T5 Text-to-Text Transfer Transformer]] — prerequisite-for (the text-to-text base)
- [[MT-DNN Multi-Task Learning and Ensemble Distillation]] — related (earlier multi-task fine-tuning on GLUE)
- [[T-Few and (IA)3 Few-Shot PEFT]] — extends (PEFT on T0)
- [[Natural Instructions and PromptSource Prompt Collections]] — related
- [[CrossFit NLP Few-Shot Gym]] — related
