---
title: MM-Vet
tags: [multimodal, concept]
summary: "MM-Vet is a 218-question open-ended benchmark that tags each question with the capabilities it needs (recognition, OCR, knowledge, generation, spatial, math) and scores answers 0 to 1 with a few-shot GPT-4 judge; GPT-4V scores highest (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yu-2023-mm-vet.md
---

# MM-Vet

Yu et al. (ICML 2024) study the evaluation of large multimodal models on demanding tasks that call on several core vision-language skills at once, proposing a metric that copes with open-ended answers in any style. The benchmark holds 200 images (187 collected, 10 from VCR, 3 from ChestX-ray14) and 218 questions. Each question is tagged with the capabilities it requires, out of six core capabilities, and these combine into 16 integrations.

## The judge

GPT-4 (0613) receives the question, the ground truth and the prediction with a 7-example few-shot prompt and returns a soft score between 0 and 1; scores are averaged to a percentage. Because the judge's output varies even at temperature 0, evaluation is run five times.

## Results (self-reported)

- The judge check used 138 objective questions answered by MM-ReAct-GPT-4, with human scores as gold. A few-shot GPT-4 judge tracks humans much more closely than keyword matching does, with Claude 3 Opus next. LLaMA-2-70B as judge does worse than keyword matching; the authors suggest large open models follow the prompt less strictly. Pooling several judges brings no gain, while few-shot examples reduce judge error.
- GPT-4V has the top overall score. MM-ReAct-GPT-4 is the strongest system other than GPT-4V, ahead on OCR through an Azure OCR tool and on math through a PAL tool. LLaVA-13B (LLaMA-2) is the best open model trained end to end. On a 168-sample subset with face images removed, MM-ReAct-GPT-4 gets 48.1 and Bard is in front.

## Limits

- Judge validation covered a single system's outputs and just 138 objective questions, leaving long open-ended answers and other systems unchecked.
- The judge is not given the image, only GPT-4 matched human grades well, and that brings usage fees; judge output varies even at temperature 0.
- Inputs are image-text and outputs text only. The keyword-matching gap is not broken down by question type.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[LLM-as-Judge Evaluation]] — prerequisite-for
- [[MME Benchmark]] — alternative-to (concurrent LMM benchmark)
- [[MMBench]] — alternative-to
- [[Visual Commonsense Reasoning and Adversarial Matching]] — related (supplies 10 of the images)
