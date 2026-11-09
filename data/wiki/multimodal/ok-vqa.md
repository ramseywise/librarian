---
title: OK-VQA
tags: [multimodal, concept]
summary: "OK-VQA is a 14,055-question VQA benchmark on COCO images whose questions need outside knowledge; 2019 models score 25-28 and Wikipedia retrieval adds little (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-marino-2019-ok-vqa.md
---

# OK-VQA

Marino et al. (CVPR 2019) build a VQA benchmark where the image alone is not enough to answer, and test whether knowledge retrieved from unstructured text helps. MTurk workers wrote questions needing outside knowledge about COCO images, and five other workers answered each. Manual filtering reduced 86,700 collected questions to 34,921, and answer balancing together with agreement filtering left 14,055, of which 9,009 are train and 5,046 test (all self-reported).

## Baselines (self-reported, OK-VQA test)

- MUTAN gets 26.41 and BAN 25.17. According to the extraction, the paper's text quotes 72.41 as the best result of the 2018 VQA competition on VQA v2.
- ArticleNet, a Wikipedia-retrieval reader, alone scores 5.28. Feeding its retrieved sentences into a 2-hop memory network (20 sentences) lifts MUTAN to 27.84 but moves BAN only from 25.17 to 25.61.
- An oracle choosing the better of MUTAN and ArticleNet for each question reaches 28.47. That is an optimistic upper bound, which the authors take to mean the retrieved knowledge adds something complementary.
- A question-only MLP scores 14.93 and the MLP with the image 20.67, so the image matters. MUTAN with ResNet18, 50 and 152 features scores 23.64, 24.74 and 26.41: better visual features give marginal gains.
- Among a sample of 10,000 VQA v1 questions, over 78% could be answered by a child of 10 or under, which the authors use as a rough proxy for how little knowledge standard VQA demands.

The three biggest knowledge categories are Plants and Animals at 17%, Vehicles at 16%, and Cooking and Food at 15%. Science and Technology makes up just 2%.

## Limits

- The set is small, and answer balancing (dropping questions whose most common answer appears more than 5 times) makes it harder by design.
- The authors concede that most of the data needs knowledge beyond Wikipedia, such as commonsense or visual knowledge.
- Each result is a single run, with no seeds or significance tests, and nobody measured how many questions remain answerable from the image. The 25-28 scores belong to 2019 models, not to modern pretrained VLMs.

## See Also
- [[Visual Question Answering Benchmarks]] — related
- [[Microsoft COCO]] — prerequisite-for (image source)
- [[VQA v2 Balanced Dataset]] — related (VQA v2 and the answer-bias motivation)
- [[PICa GPT-3 Knowledge VQA]] — related (evaluates a frozen GPT-3 on this benchmark)
