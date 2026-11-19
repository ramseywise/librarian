---
title: CrossFit NLP Few-Shot Gym
tags: [llm, fine-tuning, reference]
summary: "Ye, Lin and Ren's CrossFit challenge: 160 few-shot NLP tasks in text-to-text form, eight seen/unseen partitions and an Average Relative Gain metric; on BART-Base, multi-task upstream learning beat MAML-family methods (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ye-2021-crossfit.md
---

# CrossFit NLP Few-Shot Gym

Ye, Lin and Ren (EMNLP 2021) ask whether a pre-trained text-to-text model can pick up cross-task generalisation from tasks it has already seen, the upstream learning stage, so that it later learns unseen tasks better from a handful of examples. They supply a problem setup (the CrossFit Challenge), a task collection (the NLP Few-shot Gym) and an empirical study.

## Setup

- The Gym has 160 few-shot tasks drawn from Huggingface datasets and recast as text-to-text, with a task ontology and eight seen/unseen partitions. Few-shot samples take 16 examples per class or 32 examples in total, over 5 seeds.
- Metric: **Average Relative Gain (ARG)**, the before-to-after relative change from upstream learning on each test task, averaged across test tasks. In the paper's illustration, a 40% gain on one task and a 25% loss on another average to 7.5%.
- Method: BART-Base first learns the seen tasks by multi-task learning, MAML, first-order MAML or Reptile, then is fine-tuned on each unseen task's few-shot training set. Gain is measured against fine-tuning BART-Base directly.

## Results (self-reported, BART-Base)

- Random partition, which splits the tasks 120 / 20 / 20 for train, dev and test: multi-task learning has the top ARG at 35.06%. The meta-learners gain less: MAML (one inner step) 28.50%, Reptile 25.90% and FoMAML 22.69%.
- Held-out-MRC, where the 42 training tasks are QA tasks other than MRC: multi-task gets 32.81%, MAML 27.28%, FoMAML and Reptile 28.85%.
- Held-out-MCQA, trained on 29 non-multiple-choice QA tasks, is the hardest transfer: multi-task 12.20%, MAML 4.69%.
- Pooling upstream methods and partitions, roughly half the test tasks gain more than 5%, 35.93% stay within 5% either way and 12.60% lose more than 5%.
- Per-task gains from multi-task learning and from MAML move together (Spearman 0.66 in the Random partition).
- Training on 45 non-classification tasks helped classification test tasks about as much as training on 45 classification tasks: multi-task ARG 11.68% for the classification set (2.1), 11.82% for half-and-half (2.2) and 11.91% for the non-classification set (2.3).
- Growing the upstream data per task up to 8 times improved ARG by only about 4% (Held-out-Para, multi-task), so extra upstream data does not by itself guarantee better transfer.
- Upstream gains hold up with 1024 target-task shots and fade when millions of target examples are available (tested from the Held-out partitions for MCQA, MRC and NLI, with 32 to 4096 training examples and the full set).
- One task can behave very differently under different training sets: Race-High gains 26.71% by multi-task learning in the Random partition against 7.27% in Held-out-MCQA, and 6.59% against -6.28% by meta-learning.
- Tasks that resemble the pre-training objective, such as Glue-COLA and Domain Crawl, can get worse after upstream learning. The authors suggest catastrophic forgetting but did not test it.
- Pattern-exploiting training lowered the average on BART-Base with and without upstream learning (Held-out-GLUE, better only on CoLA and MRPC, read off a figure).

## Limits

- The authors accept that their ontology and partitions, built from task format and goal, capture only one facet of task similarity and are flawed.
- The meta-learners get a single inner-loop step, were not tuned exhaustively and react strongly to hyperparameters and seeds, so their weaker showing may not be intrinsic. FoMAML training loss was unstable on T5-v1.1-Base.
- The main analysis uses BART-Base (139M) only; BART-Large and T5-v1.1-Base appear just for Held-out-Para with first-order methods.
- No consistent rule emerged for which training tasks help a given test task. Upstream learning rate, batch size, steps and optimiser are not reported, and no significance tests are run.
- PET failed with the encoder-decoder models used; the explanation offered is a hypothesis.
- The work predates instruction-tuned large decoder models and uses small models fine-tuned on few shots, not prompted.

## See Also

- [[MAML: Model-Agnostic Meta-Learning]] — related (an upstream method compared here)
- [[Transfer and Multi-Task Learning Conditions]] — related
- [[UnifiedQA Format-Agnostic QA]] — related (CrossFit extends its multi-task QA to 160 tasks)
- [[T5 Text-to-Text Transfer Transformer]] — prerequisite-for (the text-to-text format)
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related
