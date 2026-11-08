---
title: Open NLP Questions Large Language Models Do Not Solve
tags: [foundations, reference]
summary: "A 2023 position paper from one academic lab lists 14 research areas with 45 directions it says LLMs do not directly solve, chosen to be thesis-sized and independent of paid APIs; it runs no experiments and is best used as a framing citation."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ignat-2023-has-it-all-been-solved.md
---

# Open NLP Questions Large Language Models Do Not Solve

Ignat, Jin, Mihalcea and co-authors wrote a research-agenda paper (arXiv preprint; the extraction could not confirm a venue). It runs no experiments and has no benchmarks; its only figures count its own taxonomy, drawn from a brainstorm in one US academic NLP lab rather than a systematic survey.

## What it lists

It names 14 research areas spanning 45 directions that the authors say need new work beyond LLMs, grouped as fundamental, responsible and applied. They chose areas that fit three principles: thesis-sized, affordable in a university lab, and not dependent on paid APIs. The list covers 15 of the 21 areas of a 2018 conference track list, leaving out areas they consider within LLM reach.

Directions the extraction records, each resting on cited work and not on tests here:

- **Reasoning:** the next-word objective can favour invalid reasoning, and supervised training on correct demonstrations does not cure that. Evaluating multi-step reasoning is hard under data contamination and Goodhart effects.
- **Languages:** performance is uneven across languages, which the authors attribute to training-data proportions and annotator demographics, and general-purpose models trailed dedicated translation models in 2023.
- **Hallucination and fact-checking:** hallucination persists even with retrieval or tools, so LLMs alone are not enough for fact-checking; proposed mitigations are citing sources, external knowledge lookup and tools such as calculators.
- **Annotation:** prompted labelling often loses to supervised models trained on human annotations, and ChatGPT showed higher recall than precision in the cited study.
- **Data:** the authors say deduplication and curation methods are lacking for corpora over 700 billion tokens, a threshold stated without a source.
- **Sample efficiency:** models need much more data than children to learn language, so language-acquisition research may help.
- **Multimodality:** modalities can compete and many unimodal models beat multimodal ones, as of 2023.
- **Efficiency, distillation, interpretability:** attention efficiency, mixture-of-experts and parameter-efficient tuning; distillation moving from soft logits to LLM-generated examples; probing and mechanistic work.

## Limits

- The authors concede the list is not exhaustive and omits areas where LLMs lag (information extraction, question answering, summarisation) and all LLM-development research. It comes from a single lab and the directions are described briefly and not evaluated.
- It reflects early-2023 capabilities; the extraction judges claims such as multimodal models being limited to text, audio and vision as stale, and reasoning models post-date it. The claims that LLMs cannot do something rest on cited papers, none checked here.
- Internal inconsistencies: none found by the extraction.

## See Also
- [[ChatGPT Information Extraction Evaluation]] — related (a task the paper leaves out as already tested)
- [[Language Model Self-Knowledge]] — related
- [[Hidden-State Hallucination Probes]] — related
