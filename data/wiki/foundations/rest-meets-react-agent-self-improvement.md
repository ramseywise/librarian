---
title: ReST Meets ReAct Agent Self-Improvement
tags: [foundations, concept]
summary: Recipe that runs a prompted multi-step search agent, ranks its trajectories with an LLM, and fine-tunes on them for two iterations using AI feedback only; reported to bring PaLM 2 XS and S close to the prompted L teacher (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-aksitov-2023-rest-meets-react.md
---

# ReST Meets ReAct Agent Self-Improvement

This preprint applies a ReST-style grow-and-improve loop to a ReAct-style agent with no human labels. The **Search Agent** is a five-step state machine (decide, search, summarise, answer, then self-checks for relevance and grounding), written as Python code in the prompt for PaLM 2-L. The paper presents it as a ReAct agent with Reflexion whose single tool is web search, used to write long-form answers that cite sources. Trajectories from 2,000 questions are cut into per-step examples, perplexity or an LLM ranker picks the best samples, and PaLM 2 XS, S and L are fully fine-tuned on them. A second generation repeats the process using the fine-tuned L, and the small models train on that same data too (self-distillation).

## Results (self-reported)

Automatic evaluation uses PaLM 2-L on Bamboogle (125 two-hop questions), as mean accuracy over 10 runs at T=0.5; the human evaluation is one run.

- After a second generation, the XS model comes close to the prompted PaLM 2-L teacher (70.3), S reaches 69.7, and the fine-tuned L outdoes its prompted teacher.
- Human evaluation on Bamboogle: pre-trained L 68.8, second-generation XS 67.2 and S 68.0. On the held-out BamTwoogle set (100 questions): XS and S 63.0 against 68.0 for prompted L.
- Pilot data (XS, 500 trajectories): filtering about 30% by hand lowered accuracy, 44.7 against 47.2 unfiltered.
- Mixing two trajectories per question beats one by 2.2% (65.6 against 63.4) and four adds little (65.9). From first to second generation at about equal data size (17,970 against 18,007 examples), XS rises from 54.4 to 63.4, which the paper reads as quality over quantity.
- The self-critique steps add about 0.5 to 1.0% for most models. The extraction's lineage notes this runs against the claim that LLMs cannot self-correct reasoning yet, in a process-based setup.
- Of the pre-trained models tried, only PaLM 2-L handled the code-as-prompt format consistently.

## Limits

- The authors list manually built prompts, small evaluations, a limited model set and a single tool.
- Only two iterations, so the saturation point is unknown; untested with several or unseen tools.
- No learning rate, optimiser, batch size, hardware or compute is reported, and PaLM 2 and the search API are not public.
- The small models learn from data produced by the prompted L, so it is open whether they can surpass it; the evaluator is itself PaLM 2-L.

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Reflexion]] — prerequisite-for
- [[Rejection Sampling Fine-Tuning]] — related
- [[Agent-FLAN Agent Tuning Data Design]] — related
