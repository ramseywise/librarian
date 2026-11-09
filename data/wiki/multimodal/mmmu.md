---
title: MMMU
tags: [multimodal, concept]
summary: "MMMU is 11.5K college-level multimodal questions across 6 disciplines and 30 subjects; GPT-4V scores 55.7% on the test set and the best human expert 88.6% on validation (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-xiang-2024-mmmu.md
---

# MMMU

Yue et al. (arXiv v4, June 2024; CVPR 2024) argue that current multimodal benchmarks probe commonsense and basic perception, and instead build a college-level test of perception, knowledge and reasoning using interleaved text and images. Over 50 college students gathered 13K questions from textbooks, quizzes and exams. After deduplication and cleaning, 11,550 remain, split into dev (150), validation (900) and test (10,500), with 94.03% multiple choice. They span 6 disciplines, 30 subjects, 183 subfields and 30 image types. Roughly 10% of the gathered problems were discarded as very easy, and the authors' own difficulty labels divide the remainder into 28% easy, 45% medium and 27% hard. Evaluation is zero-shot, scored by micro-averaged accuracy after rule-based answer extraction.

## Results (self-reported)

- GPT-4V reaches 55.7% on test and 56.8% on validation. Random choice gets 22.1% (validation) and 23.9% (test).
- Humans: 90 college seniors (three per subject, 30 validation questions each, textbooks allowed) reach 88.6% for the best, 82.6 medium and 76.2 worst.
- Vendors supplied these figures; the authors did not run them. Validation scores are 69.1% for GPT-4o, 62.2% for Gemini 1.5 Pro, and 59.4% for Claude 3 Opus.
- The first open-source models, BLIP2-FLAN-T5-XXL and LLaVA-1.5, land near 34% on test. The later LLaVA-1.6-34B and InternVL-Chat-V1.2 get 44.7% and 46.2%, figures provided by their authors.
- Text-only GPT-4 scores 33.8%, and adding OCR text or captions to text-only LLMs adds little (FLAN-T5-XXL 31.2, 31.9 with either).
- Broken down by difficulty on test, GPT-4V scores 76.1 on easy, 55.6 on medium and 31.2 on hard questions, and on the hard ones the gap to open models disappears. Broken down by discipline, it scores 76.3 in Hum&Soc and 41.7 in Tech and Engineering.
- In 150 sampled GPT-4V errors, 35% were perceptual, 29% lack of knowledge and 26% reasoning errors.
- Open models gain nothing from few-shot prompting: OpenFlamingo moves from 0.263 to 0.264 and Otter drops from 0.291 to 0.258.

## Limits

- Many leaderboard entries are author-provided, and prompts differ per model. Human baseline is validation only; the error analysis covers GPT-4V only.
- Rule-based extraction gives a random guess on unparseable multiple-choice answers, which pushes low scores toward chance.
- English only. The authors concede manual curation may carry bias and that college subjects are not enough to test Expert AGI; no mapping from score to skilled-adult percentile is established. Later models have exceeded the top score at v4, which the paper does not cover.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[ScienceQA]] — prerequisite-for (the closest prior benchmark, at lower grade level)
- [[MMBench]] — related
- [[Multimodal Chain-of-Thought]] — related
