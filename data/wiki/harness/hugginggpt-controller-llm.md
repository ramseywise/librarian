---
title: HuggingGPT Controller LLM
tags: [harness, concept]
summary: Four-stage pipeline in which ChatGPT plans a JSON task graph, selects Hugging Face models, runs them and writes the response; the paper reports 63.08 end-to-end success on 130 requests with a GPT-3.5 controller (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-shen-2023-hugginggpt.md
---

# HuggingGPT Controller LLM

HuggingGPT (NeurIPS 2023) uses an LLM as a controller over expert models from Hugging Face. Four stages:

1. **Task planning:** the controller turns the request into a JSON task graph. Each task has a type, an id, a list of dependency task ids and arguments (text, image, audio or video).
2. **Model selection:** candidates are filtered by task type, the top K by downloads are kept, and the controller chooses using their model descriptions.
3. **Task execution:** independent tasks run in parallel, on a hybrid of local and cloud endpoints.
4. **Response generation:** the controller summarises the results into an answer.

## Results (self-reported)

- Human evaluation on 130 diverse requests, three experts averaged, GPT-3.5 controller: 63.08 end-to-end success, 91.22 task-planning passing rate and 93.89 model-selection passing rate.
- Human-annotated set of 46 complex requests (24 sequential, 22 graph), planning scored on task type only, temperature 0: GPT-4 plans 41.36 accuracy on sequential tasks against 18.18 for GPT-3.5, and 58.33 on graph tasks against 20.83.
- On GPT-4-annotated pseudo-labels, task type only (3,497 requests, split into 1,450 single, 1,917 sequence and 130 graph): GPT-3.5 reaches 52.62 single-task planning accuracy where Alpaca-7b gets 6.48 and Vicuna-7b 23.86. Its sequential edit distance is 0.54 against 0.83 and 0.80 respectively, and its graph GPT-4 Score is 50.48 against 13.14 and 19.17.
- Demonstrations: gains are limited beyond 4; raising demonstration variety from 2 to 10 task types lifts GPT-3.5 graph-task F1 from 43.42 to 64.24.

## Limits

- Planning depends on the controller LLM and plans may be infeasible or suboptimal; several LLM calls per request add latency; context length caps how many model descriptions fit; the LLM may not follow the output format.
- Planning is scored on task type only, with arguments ignored, and the GPT-4 Score is not always correct.
- The human-annotated set has just 46 examples; K, the default number of shots and the cost are not given; Sec 4.1 mentions text-davinci-003, yet no results for it are shown.

## See Also
- [[Task Decomposition Patterns]] — prerequisite-for
- [[Dynamic Tool Discovery]] — related
- [[Tool Design as Harness Surface]] — related
- [[ToolLLM ToolBench and DFSDT]] — related
