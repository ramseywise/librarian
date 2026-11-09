---
title: OlympiadBench
tags: [eval, reference]
summary: "OlympiadBench is 8,476 bilingual, multimodal Olympiad-level math and physics problems with expert solutions; zero-shot, the best model (GPT-4V) scored 17.97% on the auto-scorable open-ended subset in the authors' own run (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-he-2024-olympiadbench.md
---

# OlympiadBench

He, Luo, Bai et al. (ACL 2024) built a benchmark to separate models that already saturate GSM8K and MATH. It holds 8,476 math and physics problems at Olympiad level, including Chinese college entrance exam problems, with expert step-by-step solutions.

## Construction and scoring

Problems from international and Chinese Olympiads and mock exams were converted to markdown with OCR, reviewed by hand, deduplicated with embedding cosine similarity and labelled by subfield and answer type. **Progressive problems** share a scenario and may depend on earlier answers, so they are compiled into a context field. Evaluation is zero-shot, with a single prompt template, on the open-ended subset that can be scored automatically; answers are taken from a boxed expression and judged by a SymPy-based pipeline (exact match, element-wise for intervals and tuples, numeric equality at tolerance 1e-8, equation and expression equivalence). The metric is micro-average accuracy.

## Results

All numbers are the paper's own (self-reported). Setup: open-ended auto-scorable problems, zero-shot, shared prompt template, micro-average accuracy.

- GPT-4V scores 17.97% overall, 21.70% on math and 10.74% on physics. On the text-only subset it scores 29.07% (31.01% math, 16.24% physics), and text-only GPT-4 scores 29.93%.
- DeepSeekMath-7B-RL scores 17.02% on text-only problems. With images, Yi-VL-34B scores 3.42%, LLaVA-NeXT-34B 3.65%, Qwen-VL-Max 10.09%, and Gemini-Pro-Vision only 4.22%.
- For comparison the paper cites other reports for GPT-4(V), which give it 52.9 on MATH and, separately, 49.9 on MathVista testmini.
- Manual error analysis of 164 failed GPT-4V problems (97 math, 67 physics): the most common math error is logical reasoning or conceptual confusion at 42%, then expression calculation at 27%.
- Long-context physics (157 problems): GPT-4V 18.47 against GPT-4 14.92; the 74 normal-length physics problems: 1.35 against 4.05.
- In a manual check of 81 theorem-proving questions, GPT-4V answered 6 correctly.

## Limits

- About a fifth of the data (21%) is theorem proving, which cannot be scored automatically and was sampled only for GPT-4V.
- The scorer sees only the two answers and cannot use problem constraints or judge equal forms such as a times root b against root of a squared b. Physics tolerance is chosen by hand where no official precision exists, so correct answers can be marked wrong (5615.88 against a reference 5614.43 at tolerance 10).
- One zero-shot prompt per model, no repeats or variance; error analysis covers GPT-4V only.
- Some closed-model responses are missing (under 1%, including 26 Qwen-VL-Max physics questions over the input limit) and were dropped. Model versions are dated; later reasoning models are not covered.

## See Also
- [[Math Word Problem Benchmarks]] — related (older, easier arithmetic datasets)
- [[IMO-Bench]] — related
- [[GPQA]] — related
