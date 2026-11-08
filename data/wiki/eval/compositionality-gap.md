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

Two papers measure the distance between answering parts and answering the whole. Both are
self-reported results on one dataset family each.

## The 2-hop definition (Press et al., 2023)

Press et al. define the compositionality gap as the fraction of compositional questions answered
incorrectly out of all those for which the model answers the sub-questions correctly. Their
hypothesis is that scaling improves memorised fact recall faster than compositional reasoning. They built
**Compositional Celebrities (CC)**, 8.6k 2-hop questions, and **Bamboogle**, 125 hand-written 2-hop
questions. The gap can only be measured on CC, since the other datasets lack sub-questions.

- The gap stays roughly constant at about 40% across GPT-3 sizes (Ada to Davinci and InstructGPT
  001/002/003, 2-shot direct prompt, CC).
- Davinci-002 answers 45.4% of CC 2-hop questions with direct 2-shot prompting. Across all CC categories
  it gets 33.4% of 2-hop questions wrong when both sub-questions are right and 41.8% right. In the hardest
  category (Birth Year / Literature Nobel Winner) it gets 1.2% of 2-hop right though it answers 80% of the
  sub-questions.
- Compositional accuracy rises from 42.6% to 81.1% as the perplexity of the worse sub-answer falls
  (Davinci-002, CC, questions where both sub-questions are right).
- Estimated gaps: ChatGPT 42.9% and GPT-4 23.0%, with a caveat that CC was released before GPT-4 launched
  and may be in its training data.
- [[Self-Ask Prompting]] narrows and sometimes closes the gap on CC.

## Chained GSM8K pairs (Hosseini et al., 2024)

Hosseini et al. chain two GSM8K test questions so the first answer becomes a variable in the second. If
a model solves the two independently with accuracies S1 and S2, they expect S1 x S2 on the chain; the
**reasoning gap** is S_comp minus S1 x S2. Setup throughout: 1,200 GSM8K test pairs, 8-shot,
temperature 0, pass@1, about 23 open and closed models.

- Cheaper models score comparably on GSM8K but show a 2-12x worse gap on the chained set. GPT-4o mini has a
  much larger gap than GPT-4o despite near-equal GSM8K accuracy, and GPT-4o mini and Gemini 1.5 Flash exceed
  90% on GSM while priced 25-35x below their larger siblings.
- Math-specialised models show gaps like same-size general models: Numina-7B 12.1, Mathstral-7B 14,
  Qwen2.5-7B 21.9, Qwen2.5-72B 2.6; Qwen2.5-Math-7B-IT solves under 60% of chained problems while scoring
  above 80% on MATH.
- Instruction tuning helps small models more on GSM8K than on the chained set (LLAMA3-8B +25.1 vs +12.6;
  Mistral-7B +14.1 vs +4.3; Gemma2-9B +22.8 vs +4.8), while for LLAMA3-70B the pattern reverses (+8.6 vs +19.0).
- Finetuning Gemma2 27B PT on GSM8K: chained accuracy rises up to 100 steps then drops at 400 while GSM8K
  keeps improving; self-generated (rejection-sampled) data beat human data.
- Writing Python rather than natural-language chain of thought helps small models more on the chained set
  (relative gains: Mistral 7B +149%, Mixtral +71%; LLAMA3 8B +69%, 70B +2%; Gemma2 9B +74%, 27B +27%).
- The authors read the near-original accuracy on the modified second questions as showing leakage is not the
  main cause, and report that several models solve the first question less often in the chained format and fail
  on the second even after a correct first answer. They call it a case study, not a benchmark to be solved.
- The extraction's lineage note marks this paper as contradicting Press et al. on one point: Press et al. found
  the gap did not shrink with GPT-3 size, while frontier models here show smaller gaps.

## Limits

- Press et al.: only GPT-3 models up to 175B and English 2-hop QA; no decoding settings reported, one run, no
  significance tests; Bamboogle is judged by hand and has 125 questions; GPT-4 and ChatGPT estimates are
  indicative because of possible contamination; Table 2 uses a later davinci-002 deployment than Table 1.
- Hosseini et al.: single run at temperature 0, no confidence intervals, 1,200 items; about 25% of modified
  questions needed manual edits; the leakage conclusion is indirect, resting on Q1 versus modified-Q2 accuracy
  being similar; fine-tuning hyperparameters are not given and gaps and deltas are read from figures; the
  models are from mid-2024; the S1 x S2 definition assumes the two hops are independent.
- The two "gaps" are defined differently (a fraction of failures given correct parts, against a deficit from a
  product of accuracies), so the numbers are not comparable.

## See Also
- [[Self-Ask Prompting]] — extends (the prompting method proposed to narrow the gap)
- [[GSM-Symbolic]] — alternative-to (another GSM8K perturbation that tests reasoning depth)
- [[Functional Benchmarks and the Reasoning Gap]] — alternative-to (a differently defined "reasoning gap": relative drop under regenerated inputs)
- [[Eval Contamination Defenses]] — related (the leakage question both papers touch)
