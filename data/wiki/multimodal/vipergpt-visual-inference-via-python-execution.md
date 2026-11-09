---
title: ViperGPT Visual Inference via Python Execution
tags: [multimodal, pattern]
summary: "ViperGPT has a code model write a Python program per visual query against an API of pretrained vision modules, then runs it with the interpreter; no training, and zero-shot results on grounding, image QA and video QA that stay well below supervised models."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-suris-2023-vipergpt.md
---

# ViperGPT Visual Inference via Python Execution

Surís, Menon and Vondrick (arXiv 2303.08128) ask whether a code-generating LLM can compose pretrained vision and language modules into a per-query Python program that answers visual questions with no task-specific training. Their stated hypothesis is that explicit programs run by an interpreter give interpretable, logical reasoning.

## Mechanism

Codex (code-davinci-002) is prompted with an API specification (function signatures, docstrings and example query-code pairs) followed by the query, and it writes a Python function `execute_command`. The interpreter runs it. Its calls reach pretrained models: GLIP for detection, X-VLM for text-image similarity, MiDaS for depth, BLIP-2 for simple queries and GPT-3 for language queries or answer selection. In the paper's example, the program finds muffin and kid patches and returns the integer ratio of their counts.

## Results (self-reported, zero-shot)

- It beats all listed zero-shot methods on RefCOCO REC testA; the extraction lists ReCLIP 58.6, GLIP 55.0 and OWL-ViT 30.3 as comparison points.
- On GQA test-dev it has the top zero-shot score, 3.4 points above BLIP-2; BLIP-2 Flan-T5 XXL is added as a `simple_query` module.
- On OK-VQA it beats all zero-shot methods and the best prior model using public resources by 6%.
- On the NExT-QA hard temporal and causal splits it is above supervised HiTeA, though on the full set it is below HiTeA's 63.1.
- An intervention study makes modules uninformative on RefCOCO; the extraction reads the bar chart as showing perception modules and Python operations matter about equally (no numbers in the text).

## Limits

- Sampling temperature, token limits, number of programs per query and number of prompt examples are not stated, so exact reproduction is not possible from the text. Dataset sizes and splits are mostly unstated and the appendix lists only model versions.
- Zero-shot remains far below supervised: RefCOCO 72.0 against 94.0 for OFA, and GQA 48.1 against 72.1 for CRF.
- Its results depend on two models, code-davinci-002 and text-davinci-003, that have since been deprecated. Its prompt examples are written per benchmark, so "zero-shot" here means no training yet hand-tailored API examples.
- The programs displayed were stripped of comments and error handling, and the in-the-wild results are only qualitative.

## See Also
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
- [[Program-Aided Language Models (PAL)]] — prerequisite-for
- [[Chain of Code]] — related
- [[Toolformer Self-Supervised Tool Use]] — related
