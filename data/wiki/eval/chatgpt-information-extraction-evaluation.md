---
title: ChatGPT Information Extraction Evaluation
tags: [eval, concept]
summary: "A 2023 preprint scored ChatGPT zero-shot on seven information-extraction tasks across 14 datasets, finding it far below supervised models except on entity typing, and its verbalised confidence badly calibrated while its self-judged explanation quality sat near 100%."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2023-evaluating-chatgpt-s-information-extraction.md
---

# ChatGPT Information Extraction Evaluation

Li and colleagues evaluated a March-to-April 2023 ChatGPT through its API on seven information-extraction tasks (entity typing, named entity recognition, relation classification, relation extraction, event detection, event argument extraction, event extraction) over 14 datasets. The PDF names no venue and the model version is not stated. The prompt gave a task description, a label set, the input and an output-format instruction, with the conversation cleared after each response. The study rates four things: performance, explainability, calibration and faithfulness, using 15 keys, ten from ChatGPT's own JSON output and five by manual annotation of about 3,000 sampled items.

## Results

- **Performance (micro-F1, whole test sets, authors' own runs, self-reported):** ChatGPT beat supervised baselines only on entity typing (BBN 85.6 against 82.2). It trailed badly elsewhere, for example CoNLL named entity recognition 67.2 against 94.6, TACRED relation classification 20.3 against 75.6 and ACE05 event detection 17.1 against 75.8. Scores fall as the task gets more complex.
- **Why it differs from earlier positive reports:** the authors say those used small random subsets and prompts tuned to the domain, while this study scored whole test sets with one concise prompt. They concede prompt choice may explain the contrast, and no prompt-sensitivity test was run.
- **Without a label set:** on about 200 samples per dataset, three experts judged whether a prediction was "reasonable" by majority vote, rather than matching the gold label. Accepted rates were far above exact-match accuracy (CoNLL 93.3% against 69.0%; SemEval 84.3% against 43.3%), and the authors suspect hard-to-understand labels hurt. The two numbers measure different things.
- **Top-k as candidates:** asking for the top 3 and top 5 labels raised recall (SemEval 42.5 to 62.1 to 76.0), shown for two datasets only.
- **Calibration:** verbalised confidence (an integer rating the model writes) was overconfident. Expected calibration error was worse than BERT's except on entity typing (SemEval 0.460 against 0.023; ACE05 relation extraction 0.745 against 0.020). On event argument extraction, mean confidence was 0.956 for correct and 0.910 for incorrect predictions.
- **Explanations:** ChatGPT rated its own explanations reasonable about 100% of the time. Human checking found 99.2% on BBN but 74.1% on event argument extraction and 47.1% on event extraction. More than 95% of explanations were judged faithful to the input in nearly all datasets.

## Limits

- Zero-shot with one prompt, an early ChatGPT version, and no few-shot or chain-of-thought variants; current models would score differently.
- Human judgement used three experts with no reported agreement. The explanation and faithfulness subsets cover only correct predictions, so failures are excluded. Samples are small (about 200 per dataset, and only 66 for one relation set).
- Calibration compares verbalised confidence with softmax probabilities in the baselines, so the two confidence measures differ in kind. Answer, confidence and explanation share one output, whose influence on the answer is untested.
- The top-k table covers two of 14 datasets. There is no limitations section. Internal inconsistency: the authors describe a clear confidence gap between right and wrong answers, which the extraction notes holds for only some rows (the ACE05 relation row shows 0.760 against 0.764).

## See Also
- [[Language Model Self-Knowledge]] — related (stated confidence versus actual correctness)
- [[Logprobs as Confidence Signal]] — alternative-to (probabilities rather than a written confidence number)
- [[LLM-as-Judge Evaluation]] — related (self-judged quality inflated against human checking)
