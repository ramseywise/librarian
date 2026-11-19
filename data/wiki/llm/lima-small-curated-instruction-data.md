---
title: "LIMA: Small Curated Instruction Data"
tags: [llm, fine-tuning, concept]
summary: "LIMA fine-tunes a 65B LLaMa on 1,000 hand-curated prompt-response pairs with supervised loss only, tests the Superficial Alignment Hypothesis, and reports responses equal or preferred to GPT-4 in 43% of human comparisons; ablations favour data diversity and quality over quantity (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zhou-2023-lima.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch08-dataset-engineering.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
---

# LIMA: Small Curated Instruction Data

LIMA measures how much of a model's instruction-following comes from pretraining and how much from large instruction-tuning sets and RLHF. The authors bet on the Superficial Alignment Hypothesis: nearly all knowledge and capability is acquired in pretraining, and alignment only teaches which of the formats already learnt to use when talking to users, so a small curated set ought to be enough. It is the reverse of the 1,836-task mixtures in [[Flan-PaLM Instruction Finetuning Scaling]] and of the machine-written sets in [[Self-Instruct and Unnatural Instructions]]. All numbers are self-reported.

## Method

The base is LLaMa 65B, tuned for 15 epochs on 1,000 curated examples: 750 taken from Stack Exchange, wikiHow and Reddit, and 250 written by the authors. No RL or preference modelling is used. A dev set of 50 prompts selects a checkpoint from epochs 5 to 10. On 300 test prompts, one sampled response per prompt is judged against five baselines by crowd workers and by GPT-4. Ablations use 7B LLaMa with ChatGPT as grader.

## Results

- Human comparisons (65B, 1,000 examples, 300 test prompts, one sampled response each): LIMA is equal or better than GPT-4 in 43% of cases, than Bard in 58%, and than DaVinci003 (RLHF) in 65%.
- Alpaca 65B, trained on 52 times as much data, is preferred less often than LIMA (LIMA wins 53%). As annotator, GPT-4 chooses LIMA over its own answer 19% of the time.
- A random 50 test prompts: 88% of LIMA answers satisfy the prompt, 50% are excellent, and all but 6 prompts are followed. On 20 out-of-distribution prompts, 20% fail, 35% pass and 45% are excellent.
- Safety: 80% of 30 sensitive prompts and 6 of 10 malicious prompts get a safe reply, with 13 safety examples among the training data.
- Ablation (7B LLaMa; ChatGPT as grader; five samples for each test prompt; 2,000 examples drawn from each source): filtered and diverse Stack Exchange scores 3.83, wikiHow 3.49, unfiltered Stack Exchange 3.33. Growing the quality-filtered Stack Exchange set from 2K to 32K examples (16 times) gives no gain in response quality.
- Dialogue: 30 hand-written dialogue chains lift the excellent share of multi-turn answers from 45.2% to 76.1% across 10 live conversations; the model with single-turn data only drifts off the prompt inside 3 interactions in 6 of those 10 conversations.

## Practitioner reading

Huyen's chapter quotes the 43% figure and says LIMA is less robust than products. Her advice is to begin with a small, carefully made set, say 50 examples; in her words, finetuning on 50 to 100 examples nearly always shows improvement, and if 50 show nothing, a larger set rarely helps, though hyperparameters and prompts deserve a check first (author's guidance, no experiment cited). She also mentions the Yi team's report that 10K carefully crafted instructions outperform hundreds of thousands of noisy ones (reported, no number given).

## Xiao and Zhu on the same result

Xiao and Zhu cite a 1,000-sample instruction set that sufficed to fine-tune LLaMa 65B to a level matching or beating models fine-tuned on far more, and use it to introduce the superficial alignment hypothesis: learning happens mainly in pre-training, and later fine-tuning adds little to the knowledge base.

## Limits

- The authors admit that building such examples takes real effort and is hard to scale.
- Compared with product-grade models LIMA is less robust: a poor sample or an adversarial prompt often yields a weak answer.
- The safety evidence is 30 prompts plus 13 training examples, and prompts with implicit malicious intent often draw unsafe answers.
- The diversity ablation sets Stack Exchange against wikiHow, which the authors say has confounds. The ablations use 7B and a ChatGPT grader, whereas the headline result uses 65B and 300 prompts, one sample each.
- Authors in groups A and B were in close contact, so test prompts and training prompts share priors.
- No seeds, hardware or compute figures appear, the text gives no link to code or weights, and baseline answers were sampled in April 2023, so the products compared have since changed.
- Inter-annotator agreement on 50 shared examples is 78 to 82%.

## See Also
- [[Flan-PaLM Instruction Finetuning Scaling]] — alternative-to
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — alternative-to
- [[Synthetic Instruction Data: Curation and Verification]] — related
- [[Post-Training Reasoning Data Primer]] — related (small curated sets in reasoning post-training)
- [[Textbook-Quality Data: phi-1 and phi-3]] — related (small, curated data for pretraining)
- [[LLaMA 1 and Llama 2 Open Foundation Models]] — related
- [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]] — related
- [[PALMS Values-Targeted Fine-Tuning]] — related (80 hand-written samples for values rather than instruction following)
