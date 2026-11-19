---
title: MT-Bench and Chatbot Arena Judge Agreement
tags: [eval, judges, benchmark]
summary: "Zheng et al. build MT-Bench (80 two-turn questions) and use Chatbot Arena votes to test whether strong LLMs can stand in for human raters: GPT-4 pairwise reaches 85% agreement with expert humans on non-tie votes, with position, verbosity and self-enhancement biases measured (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-zheng-2023-judging-llm-as-judge-mt.md
---

# MT-Bench and Chatbot Arena Judge Agreement

The paper asks whether strong LLMs can judge open-ended, multi-turn chat assistants in a way that matches human preferences. The authors build human-preference datasets from two sources: **MT-Bench** (80 two-turn questions across 8 categories) and **Chatbot Arena** (anonymous head-to-head battles voted on by the crowd). The datasets together comprise 80 MT-Bench questions, 3K expert votes and 30K conversations with human preferences. They then measure how often judges built on GPT-4, GPT-3.5 or Claude-v1 agree with humans, in three modes: pairwise, single-answer grading, and reference-guided grading (the judge first answers on its own, then sees that answer as a reference).

## Agreement results (self-reported)

- Setup S2 (non-tie votes only), MT-Bench first turn, 6 models, 58 expert labelers, default zero-shot pairwise GPT-4 prompt: GPT-4 agrees with experts 85%, against 81% human-human agreement.
- Setup S1 (ties and inconsistent verdicts count as ties): GPT-4 66% versus 63% human-human, with a random baseline of 33%.
- Chatbot Arena, 3K single-turn votes from 2114 unique IPs: 87% on non-tie votes (64% under S1).
- The further apart the two compared models are in win rate, the more GPT-4 agrees with humans, from 70% up to nearly 100% (MT-Bench, per model pair).
- Single-answer GPT-4 grading matches pairwise GPT-4 and humans at 84-85% (S2, first turn), is more scalable, and gives more ties.
- Where humans disagreed with GPT-4 they judged its verdict reasonable in 75% of cases and changed their own choice in 34%.

## Biases measured (self-reported)

- **Position.** Only GPT-4 stayed consistent in over 60% of swapped cases; Claude-v1 was 23.8% consistent (two near-identical GPT-3.5 answers, default prompt). It is stronger when the two models are close and almost disappears when they are far apart (GPT-3.5 against LLaMA-13B: 98.8% consistent). By category it is worst on writing, STEM and humanities and mildest on math and coding (86.0% consistent).
- **Verbosity.** Prepending a rephrased "repetitive list" to 23 MT-Bench answers made Claude-v1 and GPT-3.5 prefer the padded answer in 91.3% of cases, against 8.7% for GPT-4.
- **Self-enhancement.** GPT-4 favoured itself with a 10% higher win rate and Claude-v1 25%; GPT-3.5 did not. The authors call this suggestive, not established.
- **Math grading.** Reference-guided judging cut GPT-4 failures from 14/20 to 3/20 (LLaMA-13B versus Vicuna-13B, 10 math questions, positions swapped).
- **Mitigations.** Giving the judge three few-shot examples lifted GPT-4's consistency from 65.0% to 77.5%, at four times the API cost. Fine-tuning Vicuna-13B on 20K Arena votes as a 3-way classifier lifted consistency from 16.2% to 65.0% with 85.5% non-tie agreement.

## Benchmark scores and a caution

Under GPT-4 single-answer grading (80 questions x 2 turns), Vicuna-13B scores 6.39 on MT-Bench against 7.94 for GPT-3.5 and 8.99 for GPT-4, and 52.1 on 5-shot MMLU against 70.0 and 86.4. A 3K-conversation SFT set taught a style GPT-4 prefers (Vicuna-7B scores 5.95 on MT-Bench) yet MMLU stayed at 37.3 against 35.2 for LLaMA-7B, so the authors conclude one benchmark cannot determine model quality.

## Limits

- The authors say safety (honesty, harmlessness) is largely neglected in favour of helpfulness, that several helpfulness dimensions are folded into one score, and that the data cannot show whether self-enhancement exists. Few-shot consistency does not necessarily mean accuracy.
- The case studies used gpt-4-0314 and may not reproduce on later GPT-4 versions; every judge is an early-2023 closed model.
- The bias probes are small (23 padded answers; 10 math questions with 20 trials), with no intervals or significance tests.
- Only GPT-4 reaches over 80% agreement; the other two judges are weaker, and the rate depends on how ties are handled (66% under S1, 85% under S2).
- MT-Bench holds just 80 questions; judge model versions and judging temperature are not stated.

## See Also
- [[LLM Judge Biases]] — prerequisite-for
- [[LLM-as-Judge Evaluation]] — prerequisite-for
- [[Arena-Hard-Auto and BenchBuilder]] — extends
- [[LMSYS-Chat-1M]] — related
