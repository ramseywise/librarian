---
title: TheoremQA
tags: [eval, reference]
summary: An 800-question university-level benchmark built around 354 theorems in math, physics, EE&CS and finance with short exact-match answers; GPT-4 with Program-of-Thoughts led at 52.4% (self-reported) and open instruction-tuned models stayed under 15%.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-chen-2023-theoremqa.md
---

# TheoremQA

Chen and colleagues (2023) argue that grade-school math sets no longer separate strong models (the extraction cites GPT-4 and PaLM-2 at 92% on GSM8K) and build a theorem-driven set instead. Experts collected 800 questions over 354 theorems, rewriting each so that the answer takes one of five forms, integer, float, list, bool or option (47% float, 27% integer, 15% bool, 9% list, 2% option). Question counts per domain are 442 for Math, 146 for CS&EE, 131 for Physics and 81 for Finance. Answers were extracted by ChatGPT and normalised with WolframAlpha, then matched exactly. Sixteen models were prompted with chain-of-thought (CoT) and Program-of-Thoughts (PoT).

## Results (self-reported; TheoremQA, 800 questions)

- GPT-4 with PoT reached 52.4% overall, the highest of any model; with CoT 43.8%. The abstract's headline says 51%.
- ChatGPT: 35.6% with PoT and 30.2% with CoT.
- Open instruction-tuned models (Alpaca, Vicuna, OpenAssistant, MOSS, StarChat and InstructCodeT5+, at 12B to 16B parameters) all scored below 15% under CoT and PoT; the random baseline is 10.0% overall in the text (10.5 in the Table 2 All column).
- PoT beat CoT by 5 to 8 points on GPT-family models, while Claude-v1 and StarChat gained almost nothing. In PoT mode GPT-4's outputs ran as Python 92% of the time; StarChat and CodeT5+ managed about 40% or less.
- Putting a theorem description written by GPT-4 into the prompt added less than a point (ChatGPT with CoT: 30.2 to 30.8).
- On the roughly 50 image questions, captioned by BLIP, every model stayed under 10%: GPT-4 got 7.5% and ChatGPT 9.3%.
- In a manual look at 200 wrong answers, half of GPT-4's errors were minor calculation slips and 90% of Alpaca's were not rectifiable (the theorem was unknown).
- Four undergraduates, with 24 hours and internet, scored 12, 15, 18 and 19 out of 20 on 20 random questions.

## Limits

- Answer extraction is imperfect, so accuracy is an approximate lower bound (authors). Formula, figure and matrix answers were avoided, which biases coverage.
- Experts were told to modify web-sourced questions, but no contamination test was run, and GPT-4 helped draft the theorem list.
- Per the extraction, the paper disagrees with itself: the random baseline is 10.0% in the text against 10.5 in Table 2, and the theorem count is 354 in the body, 350 in the abstract and roughly 400 in the introduction.
- Decoding settings, shots and seeds are not reported; per-field counts are small and there are no confidence intervals.
- Printed inconsistencies: 51% (abstract) against 52.4% (Table 2); 350 against 354 theorems; 50 against 51 image questions; GPT-4's lead over ChatGPT is 13 or 16 points depending on prompt and text.

## See Also
- [[Program-Aided Language Models (PAL)]] — related (program-based reasoning, as in PoT)
- [[MINT Multi-Turn Benchmark]] — related (repurposes TheoremQA questions)
- [[Functional Benchmarks and the Reasoning Gap]] — related
