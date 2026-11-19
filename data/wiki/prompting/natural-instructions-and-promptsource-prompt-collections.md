---
title: Natural Instructions and PromptSource Prompt Collections
tags: [prompting, reference]
summary: "Natural Instructions maps the crowdsourcing instructions of 9 datasets into a 61-task schema to test cross-task generalisation from instructions, while PromptSource is the Jinja2 template tool and community pool (P3) behind T0; both report their own results (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mishra-2022-cross-task-generalization-natural-language.md
  - data/raw/papers/2026-11-07-bach-2022-promptsource.md
  - data/raw/papers/2026-11-08-webson-2022-do-prompt-based-models-really.md
---

# Natural Instructions and PromptSource Prompt Collections

Natural Instructions (Mishra et al.) maps crowdsourcing instructions into a schema to test following unseen tasks. PromptSource (Bach et al.) is a tool and community pool for writing prompt templates per dataset, used for T0 (see [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]]).

## Natural Instructions (Mishra et al., ACL 2022)

**Cross-task generalisation** means training on seen tasks and testing on unseen ones with no task-specific training data for the unseen. The dataset splits the crowdsourcing templates of 9 NLP datasets into 61 minimal subtasks and maps each by hand onto a schema with a title, a prompt, a definition, things to avoid, emphasis and caution, and positive and negative examples with reasons and suggestions. The splits are random, or hold out one category, one dataset or one task. BART-base (140M) is fine-tuned with the instruction prepended and scored by ROUGE-L; GPT-3 is used as is, without tuning.

Findings (self-reported):

- Random split: full instructions give ROUGE-L 32 against 13 with no instructions (BART-base, 3 epochs, lr 5e-5), and beat un-tuned GPT-3 (davinci-instruct, greedy, 16 max tokens) by 8 points (32 against 24). Leaving out question generation, BART scores 6 without and 17 with instructions, while GPT-3 reaches 33.
- Elements: prompt only 20, prompt plus definition 30, full 32, prompt plus definition plus positive examples 33 (best). Definition is key for classification (7 to 50); positive examples help question generation most (53-55). Removing negative examples hurts GPT-3 a lot (44 without against 24 with) and BART little (35 against 32).
- When instructions are given, unseen-task performance rises with the number of seen tasks (up to about 50); with none, nothing is gained.
- Task-specific BART models average 66 against 32 for the best generalising model. Human annotators exceed 96% accuracy on 240 instances.
- The schema encoding (about 950 tokens) beats raw crowdsourcing instructions (average 2.5k tokens) for GPT-3, for example QASC 51.3 against 3.7. On tasks both cover, zero-shot GPT-3 does better with these long instructions than with PromptSource templates (Quoref QA, GPT3-Instruct 47 against 43).
- Curating one task takes between 6 and 34 hours, and parsing instances is the slow step.

## PromptSource (Bach et al., ACL 2022 demo)

A **prompt** here is a function mapping a dataset example to an input and target text. PromptSource pairs a Streamlit interface with Jinja2 templates, integrated with HuggingFace Datasets, so a writer can view outputs on many examples; prompts are documented, code-reviewed and merged into the **P3** (Public Pool of Prompts). Usage is `DatasetTemplates("snli")`, pick a template, `apply(example)`.

- By January 2022 the pool has more than 2,000 prompts across about 170 datasets (self-reported). Contributors were encouraged to write many prompts for each dataset (five to ten or beyond), worded in varied ways.
- In early informal tests, reported without numbers, a prompt that failed to name the valid completions tended to do worse than one that listed them.
- T0 was fine-tuned on a subset of P3.

## Limits

- Natural Instructions: text instructions, mostly for QA datasets from 9 sources; 61 tasks in 6 coarse categories; at most 6.5k instances per task. Only BART-base is tuned, so BART against GPT-3 mixes model size, tuning and prompt format; no seeds or significance tests; ROUGE-L only. Models remain far from the task-specific 66. The scaling trend with task count is shown only to about 50 tasks. Superseded in scale by FLAN, T0 and Super-NaturalInstructions.
- PromptSource: there are no experiments or user study, so design claims rest on a pilot prompt-writing effort; priming has no native support; no simple metric measures prompt quality, which relies on code review; and P3 covers English only.
- Webson and Pavlick report results contradicting the Natural Instructions claim that elaborate instructions help (see [[Irrelevant and Misleading Prompt Templates]]).

## See Also

- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — prerequisite-for
- [[CrossFit NLP Few-Shot Gym]] — related (contemporaneous cross-task generalisation setup)
- [[Irrelevant and Misleading Prompt Templates]] — related (reports contradicting the claim that elaborate instructions help)
- [[Prompt Templates and Variables]] — related
- [[UnifiedQA Format-Agnostic QA]] — related (multi-task unified encoding within seen tasks)
