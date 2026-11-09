---
title: Compositionality Gap
tags: [eval, concept]
summary: "The share of 2-hop questions a model gets wrong although it answers both sub-questions right: about 40% across GPT-3 sizes on Compositional Celebrities (self-reported), and a related gap for chained GSM8K pairs, measured against the product of the two separate accuracies, was 2-12x worse for cheaper models at similar GSM8K scores (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-press-2023-measuring-narrowing-compositionality-gap-language.md
  - data/raw/papers/2026-11-08-hosseini-2024-not-all-llm-reasoners-created.md
---

# Compositionality Gap

Two papers measure the distance between answering parts and answering the whole. Each reports its own
figures (self-reported), and each rests on a single dataset family.

## The 2-hop definition (Press et al., 2023)

Press et al. define the compositionality gap as the share of compositional questions a model gets wrong,
counted among the questions where it gets both sub-questions right. They hypothesise that scale
improves recall of memorised facts more quickly than it improves compositional reasoning. They built
**Compositional Celebrities (CC)**, with 8.6k 2-hop questions, and **Bamboogle**, with 125 hand-written
2-hop questions. Only CC supports measuring the gap, because the other datasets have no sub-questions.

- Across GPT-3 sizes (Ada up to Davinci, plus InstructGPT 001/002/003, 2-shot direct prompting, CC), the
  gap holds at about 40%.
- Davinci-002 with direct 2-shot prompting gets 45.4% of CC 2-hop questions right. Over all CC
  categories, 2-hop questions whose sub-questions it answers correctly are wrong 33.4% of the time and
  right 41.8%. In the hardest category (Birth Year / Literature Nobel Winner) it solves only 1.2% of the
  2-hop questions, even though it handles 80% of the sub-questions.
- As the perplexity of the weaker sub-answer drops, compositional accuracy goes from 42.6% up to 81.1%
  (Davinci-002, CC, restricted to questions with both sub-answers correct).
- Estimated gaps are 42.9% for ChatGPT and 23.0% for GPT-4, with the caveat that CC predates the GPT-4
  release and could appear in its training data.
- [[Self-Ask Prompting]] reduces the gap on CC, and in some cases removes it.

## Chained GSM8K pairs (Hosseini et al., 2024)

Hosseini et al. join two GSM8K test questions so that the first answer feeds a variable of the second.
If a model's accuracies on the two questions alone are S1 and S2, the chain should score S1 x S2; the
**reasoning gap** is S_comp minus S1 x S2. The main comparisons use 1,200 GSM8K test pairs, 8 shots,
temperature 0, pass@1, around 23 open and closed models; the finetuning and code-prompting runs have their
own setups, given beside them.

- Lower-cost models do about as well on plain GSM8K but have a gap 2 to 12 times worse on the chained
  set. GPT-4o mini's gap is far above GPT-4o's although their GSM8K accuracy is nearly the same. GPT-4o
  mini and also Gemini 1.5 Flash both pass 90% on GSM, at prices 25 to 35 times below the larger models in
  their families.
- Models specialised for maths show gaps similar to general models of the same size: Numina-7B at 12.1,
  Mathstral-7B at 14, Qwen2.5-7B at 21.9 and, for contrast, Qwen2.5-72B at 2.6. Qwen2.5-Math-7B-IT scores over 80% on MATH yet
  solves fewer than 60% of the chained problems.
- Instruction tuning gives small models a bigger lift on GSM8K than on the chained set (LLAMA3-8B +25.1
  against +12.6; Mistral-7B +14.1 against +4.3; Gemma2-9B +22.8 against +4.8). LLAMA3-70B shows the
  opposite pattern (+8.6 against +19.0).
- When Gemma2 27B PT is finetuned on GSM8K (human-written against self-generated solutions; hyperparameters
  not given), chained accuracy climbs for the first 100 steps and is lower
  at 400, while plain GSM8K accuracy keeps improving. Data the model generated itself (rejection sampled)
  did better than human-written data.
- Having the model write Python in place of natural-language chain of thought benefits small models more
  on the chained set (8-shot code prompt; relative gains: Mistral 7B comes to +149% and Mixtral +71%; LLAMA3 at 8B: +69%, at 70B: +2%;
  Gemma2 at 9B: +74%, at 27B: +27%).
- The authors take the near-original accuracy on the modified second questions as a sign that leakage
  is not the main explanation. They also report that several models answer the first question correctly
  less often in the chained format, and miss the second even when the first answer was right. They describe
  the work as a case study, not a benchmark to be solved.
- The extraction's lineage note lists this paper as contradicting Press et al. on one point: Press et al.
  saw no shrinking of the gap as GPT-3 grew, whereas frontier models here have smaller gaps.

## Limits

- Press et al.: GPT-3 models of at most 175B parameters and English 2-hop QA only; decoding settings are
  not reported, there is a single run and no significance testing; Bamboogle was graded by hand and
  contains 125 questions; the GPT-4 and ChatGPT estimates are only indicative given possible contamination;
  the davinci-002 model in Table 2 is a later deployment than the one in Table 1.
- Hosseini et al.: one run at temperature 0 with no confidence intervals, and 1,200 items; roughly a
  quarter of the modified questions needed manual edits; the leakage conclusion is indirect, since it rests
  on Q1 and modified-Q2 accuracy being alike; fine-tuning hyperparameters are not listed and gaps and
  deltas are read off figures; the models date from mid-2024; the S1 x S2 definition presumes the two hops
  are independent.
- The two "gaps" are defined differently (a share of failures among correct parts, versus a shortfall
  relative to a product of accuracies).

## See Also
- [[Self-Ask Prompting]] — extends (the prompting method proposed to narrow the gap)
- [[GSM-Symbolic]] — alternative-to (another GSM8K perturbation that tests reasoning depth)
- [[Functional Benchmarks and the Reasoning Gap]] — alternative-to (a differently defined "reasoning gap": relative drop under regenerated inputs)
- [[Eval Contamination Defenses]] — related (the leakage question both papers touch)
- [[Selection-Inference]] — related (alternating select and infer calls)
- [[Iterated Decomposition]] — related
