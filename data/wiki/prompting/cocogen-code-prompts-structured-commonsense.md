---
title: CoCoGen Code Prompts for Structured Commonsense
tags: [prompting, pattern]
summary: "CoCoGen rewrites each target graph as a Python class, gives a few as a few-shot prompt to Codex and parses the completed code back into a graph; on ExplaGraphs with 30 examples it beat T5 fine-tuned on 1,500 (structural accuracy 45.20 against 38.19) (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-madaan-2022-language-models-code-few-shot.md
---

# CoCoGen Code Prompts for Structured Commonsense

Madaan and colleagues (EMNLP 2022) ask whether a language model of code, prompted with the output graph written as Python, generates structured commonsense graphs better than a natural-language model prompted with a serialised text graph. Their hypothesis is that code-formatted graphs resemble the model's pretraining data.

## Mechanism

- Each (text input, graph) pair is rewritten as Python code. Nodes become objects and edges become attributes or add_edge calls (the ProScript prompt uses a `Tree` class holding a goal string).
- Several of these classes form the few-shot prompt for the code model Codex (version code-davinci-002), which receives an unfinished class for the test input, completes it, and the output is parsed into a graph.
- Baselines: text-davinci-002 and text-curie-001 shown the same examples flattened to text (a **serialized graph**: a flat node-pair list or a DOT string), and fine-tuned T5.
- **KST (knowledge similarity tuning)**, adapted from Synchromesh's target-similarity tuning, fine-tunes a retriever so that how close two inputs are in embedding space tracks how close their output graphs are; it then chooses prompt examples dynamically.

Tasks: ProScript (script generation, edge prediction), ProPara and ExplaGraphs.

## Results (self-reported)

- ProScript script generation: 15 prompt examples beat T5 fine-tuned on all 3,500 samples on BLEU. Edge prediction: F1 56.24 for CoCoGen against 48.92 for text-davinci-002; T5 fine-tuned on 1k scores higher (60.15).
- ProPara, 3 shots: F1 63.0, 5.0 above text-davinci-002 and 74% above text-curie-001; the authors claim the best few-shot result, within 10 F1 of the overall best.
- ExplaGraphs, 30 shots, validation split: structural accuracy 45.20 against 38.19 for T5 on 1,500 examples.
- A 2 by 2 on ExplaGraphs structural accuracy: text-davinci-002 with text prompt 33.16, with code prompt 33.00; Codex with text prompt 38.02; Codex with code prompt (CoCoGen) 45.20. The code model and the code prompt each help, and combined they help more than either alone.
- KST retrieval raises ProScript edge-prediction F1 (56.52 to 65.71), leaves script generation almost flat (BLEU 25.24, then 25.4), and hurts ExplaGraphs (45.2 to 37.47), which the authors attribute to near-duplicate neighbours cutting prompt diversity.
- The best Python format is task-dependent: on ExplaGraphs the Literal format scores 45.2 against Tree 39.24 and Relation 42.82. Code-davinci-001 swings from F1 15.9 to 29.7 across formats on edge prediction, code-davinci-002 only from 52.0 to 56.5.
- In a blind pairwise check on 20 ExplaGraphs samples, graphs from CoCoGen were preferred for correctness 38.3% against 18.3% for text-davinci-002. Across three seeds (prompt example order) ProScript script-generation BLEU is 25.3 +/- 0.1 against 23.1 +/- 2.7.

## Limits

- Codex, text-davinci-002 and text-curie-001 are closed, with undocumented size and data, so size comparisons are estimates; Codex has since been deprecated (not stated in the paper).
- English only. Because the ExplaGraphs test split was unavailable, its results come from the validation split.
- Each task needs its own hand-designed Python format; none is best everywhere.
- Human evaluation rests on 20 examples rated by three of the authors.
- The paper omits temperature and max-token settings, and text-curie-001's ProPara result suffers format failures.
- Internal inconsistencies: one caption claims a win over T5 (1k) on edge prediction that Table 2 does not show, and another caption (Table 14) conflicts with its own numbers.

## See Also
- [[Program-Aided Language Models (PAL)]] — related (code as the intermediate representation)
- [[Code Generation Prompting]] — related
- [[Few-Shot Prompting]] — prerequisite-for
- [[Structured Output]] — related
