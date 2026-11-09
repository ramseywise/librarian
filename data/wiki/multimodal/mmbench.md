---
title: MMBench
tags: [multimodal, concept]
summary: "MMBench is a 3,217-question bilingual multiple-choice benchmark over 20 abilities that scores a model only if it answers every circular shift of the choices (CircularEval) and uses GPT-4 to extract the chosen option (all figures self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-liu-2024-mmbench.md
---

# MMBench

Liu et al. (arXiv 2307.06281, v5 of 20 Aug 2024) ask how large vision-language models can be evaluated objectively and at fine grain even though many follow instructions poorly. Their answer pairs a systematically built benchmark with a stricter scoring rule.

## Construction and scoring

- 3,217 questions over 20 level-3 abilities in a three-level taxonomy, in English and Chinese; over 80% were collected from the Internet, with a dev:test split of 4:6.
- Quality filtering uses text-only LLM majority voting and a check for questions every VLM gets wrong.
- **CircularEval** feeds each question to the model N times, where N is the number of choices, shifting the choices circularly each pass; the model succeeds only if it is right on all passes.
- A GPT-4 extractor maps free-text outputs to a choice. On about 420 outputs that heuristic matching could not parse, it agrees with a human in 91.5% of cases (self-reported).

## Results (self-reported)

- On MMBench-dev (zero-shot, with the gpt-4-0125 extractor), OpenFlamingo v2 drops from 36.7% under single-pass scoring to 2.6% under CircularEval.
- On dev, the 13B LLaVA-v1.5 is ahead of its 7B sibling by 2.1 points single-pass and by 4.7 under CircularEval.
- VisualGLM-6B scores 19.4 on dev with exact matching and 36.1 with the GPT-4 extractor; its heuristic match rate is only 64.8%. Changing which LLM does the extraction moves its dev results by at most about 1.4%, and the top proprietary models by 0.3%.
- Refusals affect GPT-4v in 1.8% of its CircularEval passes, Gemini-Pro-V on 1.6% and Qwen-VL-Max on 0.1%; celebrity recognition accounts for 74% of the GPT-4v refusals. The authors bound the cost to MMBench-test accuracy at 2.4% or less (for GPT-4v, 74.3 rising to an upper bound of 76.2).
- On MMBench-test, moving Vicuna from 7B to 13B adds 8.3 (MiniGPT), 1.5 (InstructBLIP) and 3.5 (LLaVA v1.5) points.
- After quality control, GPT-4-Turbo given text alone lands near chance.
- Looking at the best model's CircularEval accuracy, the weakest abilities are image quality (61.3%) and structuralized image-text (61.5%), followed by physical relation at 64.0% and spatial relationship at 68.0%.

## Limits

- Multiple-choice only. CircularEval gives much lower accuracy than a single pass, so scores from the two protocols are not comparable.
- Content moderation in proprietary models depresses their scores.
- The numbers are from the v5 revision (MMBench v1.1); earlier versions differ. No seeds or variance are reported, and temperature and token limits are not stated.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[SEED-Bench]] — alternative-to (a competing MLLM benchmark)
- [[VLM Benchmark Shortcuts]] — prerequisite-for
- [[LLaVA Visual Instruction Tuning]] — related (LLaVA-1.5 is one of the models it evaluates)
- [[Visual Question Answering Benchmarks]] — related
- [[MME Benchmark]] — alternative-to
- [[MMMU]] — related
