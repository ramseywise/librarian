---
title: Visual Question Answering Benchmarks
tags: [multimodal, comparison]
summary: "A comparison of VQA datasets and the multimodal-LLM evaluations that followed, grouped by what each isolates (language priors, compositional reasoning, outside knowledge, reading text, commonsense, expert knowledge), with the models and grounding datasets they build on."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-goyal-2017-making-v-vqa-matter.md
  - data/raw/papers/2026-11-07-gurari-2018-vizwiz-grand-challenge.md
  - data/raw/papers/2026-11-07-singh-2019-towards-vqa-models-that-can.md
  - data/raw/papers/2026-11-08-hudson-2019-gqa.md
  - data/raw/papers/2026-11-08-marino-2019-ok-vqa.md
  - data/raw/papers/2026-11-08-mathew-2021-docvqa.md
  - data/raw/papers/2026-11-08-masry-2022-chartqa.md
  - data/raw/papers/2026-11-08-mishra-2019-ocr-vqa.md
  - data/raw/papers/2026-11-08-zellers-2019-recognition-cognition.md
  - data/raw/papers/2026-11-07-krishna-2017-visual-genome.md
  - data/raw/papers/2026-11-08-plummer-2015-flickr30k-entities.md
  - data/raw/papers/2026-11-08-fu-2025-mme.md
  - data/raw/papers/2026-11-08-xiang-2024-mmmu.md
  - data/raw/papers/2026-11-08-yu-2023-mm-vet.md
  - data/raw/papers/2026-11-07-lu-2022-learn-explain.md
  - data/raw/papers/2026-11-08-tan-2019-lxmert.md
  - data/raw/papers/2026-11-07-yang-2022-empirical-study-gpt-3-few.md
  - data/raw/papers/2026-11-08-yasunaga-2022-retrieval-augmented-multimodal-language-modeling.md
  - data/raw/papers/2026-11-07-karpathy-2015-deep-visual-semantic-alignments-generating.md
  - data/raw/papers/2026-11-07-ren-2016-faster-r-cnn.md
  - data/raw/papers/2026-11-07-russakovsky-2015-imagenet-large-scale-visual-recognition.md
---

# Visual Question Answering Benchmarks

Each VQA benchmark in the wiki was built to remove one shortcut or to test one skill that earlier sets let models skip. This page lines them up by that purpose. All figures come from the benchmark papers and are self-reported; scores from different papers use different splits and metrics, so they are not ranked against each other here.

## What each benchmark isolates

| Isolates | Benchmark | Defining design (self-reported) |
|---|---|---|
| Language priors | [[VQA v2 Balanced Dataset]] | Each question has two similar COCO images with different answers |
| Compositional reasoning | [[GQA Benchmark]] | 1.7M balanced questions from scene graphs, plus consistency, validity, plausibility and grounding metrics; best 2019 model 54.06% against 89.3% for humans |
| Outside knowledge | [[OK-VQA]] | 14,055 COCO questions needing external facts; 2019 models score 25 to 28 |
| Real-world access | [[VizWiz Grand Challenge]] | 31,173 questions from blind users' own photos; about 28.63% unanswerable |
| Reading scene text | [[TextVQA and LoRRA]], [[OCR-VQA]] | Questions on Open Images photos (LoRRA 27.63%) and on book covers (207,572 images, 48.3% for the baseline) |
| Reading documents and charts | [[DocVQA]], [[ChartQA and VisionTaPas]] | 50,000 questions on 12,767 page images scored by ANLS; charts at best 51.84% via an extracted data table |
| Commonsense | [[Visual Commonsense Reasoning and Adversarial Matching]] | Four-way answers and rationales; R2C 44.0% against 85.0% for humans |
| Broad MLLM ability | [[MME Benchmark]], [[MM-Vet]] | Yes/no pairs over 14 subtasks; open-ended answers scored 0 to 1 by a GPT-4 judge |
| Expert knowledge | [[MMMU]], [[ScienceQA]] | College-level questions (GPT-4V 55.7% on test); K-12 science with lectures and explanations |

## How they relate

- Balance is the thread from the first set to the second: VQA v2 balances by image pairs, and GQA balances by answer distribution over generated questions.
- Reading benchmarks split by input: natural photos with incidental text (TextVQA, VizWiz), template questions on covers (OCR-VQA), and structured documents and charts (DocVQA, ChartQA). The DocVQA paper finds that models fall short on questions needing layout and figures.
- The later MLLM evaluations drop the fixed answer vocabulary. MME poses yes/no questions in a fixed format, which its authors adopt to avoid data leakage and prompt-engineering effects, MM-Vet pays for a judge to accept open answers, and MMMU returns to multiple choice at college level.

## Models and grounding data

- Grounding datasets: [[Visual Genome]] supplies scene graphs and QA that GQA builds on, and [[Flickr30k Entities]] adds phrase-to-box links.
- Models: [[LXMERT]] pretrains on VQA and GQA data and is evaluated on both; [[PICa GPT-3 Knowledge VQA]] prompts GPT-3 with captions for OK-VQA; [[RA-CM3 Retrieval-Augmented Multimodal Modeling]] adds retrieval to a generator; [[Deep Visual-Semantic Alignments]] is an early region-word alignment and captioning model.

## Limits

- This is a synthesis of the benchmark papers, not a re-run; no single protocol puts the models side by side. Scores shift with the answer metric (soft accuracy, ANLS, cgF1-style gating, judge scores) and are tied to the 2015 to 2024 models each paper tested.
- Several extractions had figures stripped (DocVQA, MM-Vet, PICa, the captioning paper), so those entries carry design facts only.

## See Also
- [[VQA v2 Balanced Dataset]] — instance-of
- [[GQA Benchmark]] — instance-of
- [[OK-VQA]] — instance-of
- [[VizWiz Grand Challenge]] — instance-of
- [[TextVQA and LoRRA]] — instance-of
- [[OCR-VQA]] — instance-of
- [[DocVQA]] — instance-of
- [[ChartQA and VisionTaPas]] — instance-of
- [[Visual Commonsense Reasoning and Adversarial Matching]] — instance-of
- [[Visual Genome]] — related
- [[Flickr30k Entities]] — related
- [[MME Benchmark]] — instance-of
- [[MMMU]] — instance-of
- [[MM-Vet]] — instance-of
- [[ScienceQA]] — instance-of
- [[LXMERT]] — related
- [[PICa GPT-3 Knowledge VQA]] — related
- [[RA-CM3 Retrieval-Augmented Multimodal Modeling]] — related
- [[Deep Visual-Semantic Alignments]] — related
- [[Faster R-CNN]] — related (the detector behind object-feature VQA models)
- [[ILSVRC ImageNet Challenge]] — related
- [[MMBench]] — alternative-to
- [[VLM Benchmark Shortcuts]] — related
