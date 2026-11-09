---
title: SciBench
tags: [eval, benchmark]
summary: "SciBench has 869 college textbook science and math problems (177 multimodal) plus a closed set of exam problems, scored by numeric answers, with an LLM verifier assigning each error to one of ten missing skills; GPT-4 with few-shot Python tools was best, and no prompting strategy won on all skills (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2023-scibench.md
---

# SciBench

Wang and colleagues (ICML 2024) argue that current benchmarks are too easy, being limited to high-school content, basic arithmetic and text, and instead test college-level science and maths problem solving. The textbook set has 869 free-response problems from ten textbooks in physics, chemistry and maths, each with a single numeric answer, transcribed to LaTeX by hand; the closed exam set (103 problems, seven exams from computer science and maths courses, instructor-authorised) is typed manually to limit leakage.

## Method

Seven text-only and several multimodal models ran at temperature 0 under zero-shot, chain-of-thought, few-shot and Python or Wolfram tool prompts. Answers pass within 5% relative tolerance. A GPT-3.5 **verifier** puts each wrong answer under one of ten missing skills; those ten skills were condensed from 112 error annotations that humans made on GPT-3.5 outputs.

## Results (self-reported)

Setup: textbook set, accuracy weighted by problem count, unless noted.

- Best overall is GPT-4 with few-shot Python as an external tool (43.22 for GPT-4 few-shot Python); tools add about 12.9 points over few-shot chain of thought. GPT-4-Turbo is best zero-shot but underperforms GPT-4 with Python tools. In the zero-shot setting LLaMA-2-7B scores close to zero.
- Error profiles (GPT-3.5): zero-shot chain of thought cuts calculation errors but raises causal and logical-decomposition errors; tools cut calculation errors by half yet add trouble when converting a solution to code. No strategy wins on all skills.
- The verifier agreed with two annotators on 123 of 151 checked classifications (81.45%).
- GPT-4 trails the average student on the Data Mining midterm and final (the instructor gives student averages of 80.18% and 72.71%). The best multimodal run used captions and text recognised from images; the best open multimodal model scored 7.4%.

## Limits

- No contamination test beyond hand transcription and the closed exam set; textbook solutions may be online.
- Numeric final answers only; 5% tolerance can pass near misses. The error labels are produced by a GPT-3.5 verifier, and the main text shows profiles for GPT-3.5 only.
- The exam set is small, and the paper's exam score figures are inconsistent (51.57% against 57.54%).
- Each result is a single run at temperature 0 with no seeds or intervals; models are 2023-era. Multimodal evaluation goes through captions and OCR, not native vision.

## See Also
- [[Math Word Problem Benchmarks]] — related
- [[LILA Math Reasoning Benchmark]] — related
- [[AGIEval]] — related
- [[Chain-of-Thought Prompting]] — prerequisite-for
