---
title: Iterated Decomposition
tags: [prompting, pattern]
summary: "A human-in-the-loop loop for building select-then-generate LM pipelines: run on gold answers, inspect failing steps in a trace viewer, fix the worst one (usually paragraph selection) and repeat; reported gains on three science Q&A tasks with text-davinci-002 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-reppert-2023-iterated-decomposition.md
---

# Iterated Decomposition

Reppert, Rachbach, George et al. (preprint, 2023) propose a workflow for developing **compositional language model programs**: tasks split into inspectable subtasks that each call a model. **Iterated decomposition** improves a decomposition step by step through error diagnosis and amendment. **Process supervision**, as the paper uses it, means relying on human-understandable intermediate steps; here it is the developer checking steps against gold answers, not a claim for settings without ground truth. The authors also release ICE, an open-source visualizer for execution traces.

## The loop

1. Start with a minimal decomposition.
2. Run it on inputs with gold answers.
3. Evaluate.
4. Inspect failures in the ICE trace viewer.
5. Fix the failing subtask (decompose further, add chain of thought or retrieval, edit prompts), then repeat.

The case studies are select-then-generate pipelines, where the biggest gains came from choosing paragraphs better (a zero-shot perplexity cross-encoder: rank paragraphs by the inverse perplexity of the completion saying the answer is not mentioned) and few-shot demonstrations for generation.

## Results

All numbers are the paper's own (self-reported). Setup for all: held-out test sets, text-davinci-002, against Elicit's deployed monoT5 plus text-davinci-002 baseline, unless stated.

- Placebo extraction: description accuracy rises to 65% and classification from 71% to 98%, the latter through combining a trial-arm classifier with a per-paragraph one.
- Participant flow in trials, with perplexity selection plus automatic few-shot generation: adherence accuracy 53% to 70%, experiment extraction 40% to 70%, trial arm extraction 55% to 86%.
- Transfer: reusing the participant-flow decomposition unchanged on 100 sampled QASPER questions moves semantic-equivalence accuracy from 38% to 69% (F1 15 to 32).
- Diagnosis: every one of the 51 adherence false negatives in the baseline traced to selection; given perfect selection the baseline generator still manages just 77% adherence accuracy, so generation needs work too. Perplexity selection lifts adherence paragraph recall from 0.09 to 0.76.
- Controls: a regex and keyword decision tree gets 94% on placebo classification (98% for the decomposition) but only 10% on description. Filling a 4096-token window with as much of the paper as fits, plus step-by-step prompting, gets 69% classification and 30% description.
- In the pruning step, paragraph precision went from 0.14 to 0.29 while recall fell from 0.77 to 0.54, and answer accuracy edged from 0.55 up to 0.6.

## Limits

- Test sets are small (20 to 135 items; 100 QASPER questions) and the p-values treat answers as independent, which makes them look stronger than they are.
- Only text-davinci-002 and monoT5 were used; the authors expect simulation-style prompts to count for less on instruction-tuned models.
- Decontextualization was not systematically evaluated, the keyword regex nearly matches the decomposition on the easy placebo task, and the cost of many calls against end-to-end was not measured.
- Temperature, max tokens, seeds and the perplexity threshold are missing.

## See Also
- [[Prompt Chaining]] — prerequisite-for
- [[Decomposed Prompting (DecomP)]] — related
- [[Selection-Inference]] — related (alternating select and infer)
- [[Compositionality Gap]] — related (the gap the paper quotes at about 40%)
