---
title: Shepherd Critic Model
tags: [eval, reference]
summary: "Shepherd is a LLaMA-7B fine-tuned on about 8K curated community critiques to point out errors in another model's answer; GPT-4 pairwise judging favoured it 87.0 against Alpaca-7B but near-tied it with SelFee-7B and ChatGPT (self-reported), and the same paper found GPT-4 Likert scoring disagreed with humans."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-wang-2023-shepherd.md
---

# Shepherd Critic Model

Shepherd (Wang et al., arXiv 2308.04592, 2023) is a critic: given a question and a model's answer, it writes feedback naming errors or suggesting improvements. It is LLaMA-7B fine-tuned on roughly 8K examples, in contrast with SelFee, a comparator trained on 178K.

## Training data

The community data was drawn from Stack Exchange and 16 subreddits and filtered on keywords, edit history and votes. A further 1,317 examples were annotated by one expert per example at $8 each. For testing, CritiqueEval holds 52 Pushshift questions posted between June 2022 and June 2023, built to limit contamination.

## Results (self-reported)

Test set: 352 instances (50 from each of six public sets plus the 52 CritiqueEval ones).

- **GPT-4-0613 as pairwise judge.** Average win rate was 87.0 against Alpaca-7B, 53.0 against SelFee-7B and 56.0 against ChatGPT. The paper does not define "win rate"; the extraction infers that ties count as half a win.
- **Human pairwise judgement.** 72.4 against Alpaca, 59.7 against SelFee and 49.6 against ChatGPT, a tie. Rater number and agreement are not reported.
- **Dataset flip.** Against ChatGPT the human figure ranged from 38.0 on AlpacaFarm to 66.3 on CritiqueEval.
- **GPT-4 as a 1 to 7 Likert rater.** It gave Alpaca 4.7 where humans gave 2.91, and put ChatGPT first at 6.25, then SelFee at 5.49, Shepherd at 5.37 and Alpaca at 4.69, while humans put SelFee at 3.84, below Shepherd at 4.41. The authors say GPT-4 appeared to favour a specific format, and recommend pairwise comparison, which they say matched humans better.
- **Failure shape.** Compared with ChatGPT, Shepherd earned more top ratings and also more wrong judgments.
- **Judge error.** In one worked example with the ground truth supplied, GPT-4 scored the one critique that found the error at 2, against 6 for SelFee and 4 for ChatGPT.

## Limits

The paper reports no agreement between raters, number of raters, intervals or tests of significance, although it uses the word "significantly". It also gives no correlation between GPT-4 and human judgements and does not swap answer positions in the pairwise prompt. Samples are small (50 per dataset). Checkpoints were chosen using the same GPT-4 comparison later applied for evaluation, on 20 held-out examples. Some of SelFee's training examples are also test items (33 of 50 in AlpacaFarm), an advantage for SelFee. The extraction's own arithmetic finds inconsistencies: Table 5's averages do not match the printed rows, and the printed ChatGPT-ahead human Likert result reverses on per-dataset numbers. Nothing tests whether critiques improve later outputs, no cost or latency is given, and no model release is stated (only data). Baselines and judge are 2023 versions.

## See Also
- [[LLM Judge Biases]] — related (pairwise versus pointwise scoring)
- [[LLM-as-Judge Evaluation]] — related
- [[Chain-of-Verification]] — related (another way a model's own errors get flagged)
