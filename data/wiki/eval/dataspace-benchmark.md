---
title: DataSpace
tags: [eval, reference]
summary: "A benchmark of 410 data-analytics tasks over mixed-format workspaces, scored by a model-free table comparison; with one backbone held fixed the agent harness moved accuracy by 15.36 points, and most failures of the audited model were wrong output shape rather than wrong analysis (self-reported, one run per configuration)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-dataspace.md
---

# DataSpace

DataSpace (Li et al., arXiv 2608.03451, 2026) tests data agents on analytics questions whose evidence is spread across files of different kinds. The authors say existing data-agent benchmarks rarely combine three properties: a heterogeneous workspace, a requirement to return a complete table, and deterministic scoring. The KDD Cup 2026 data-agents competition adopted it as its official benchmark.

## Construction

The 410 tasks share 7,439 artifacts totalling 15.01 GB; the files are tabular, database, document, PDF and video formats. The items come from two Text-to-SQL sets, 363 from BULL and 47 from EHRSQL, and 11 experts checked them. Gold answers come from executing the SQL. The agent receives only a question and a workspace and must return a full CSV table.

## Scoring without a judge

A model-free evaluator compares the returned table with the gold one. Column alignment ignores header names, values are normalised by type and precision, and row order is checked only for tasks that require an order. The metric is binary exact-match Task Accuracy over all 410 tasks. Because the gold column types and precision are frozen per task, this is an example of grading the final state mechanically rather than asking a judge ([[LLM-as-Judge Evaluation]] covers the alternative).

## Results (self-reported)

Setup for the backbone comparison: a fixed ReAct-style agent with bash, image-viewing and answer-submission tools, per-task caps of 60 turns, 50 tool actions and half an hour (1,800 s), with 4 CPUs, 16 GiB, no network, provider-default reasoning effort, models accessed July 2026.

- Six backbones scored from 66.34% (272/410, Grok 4.5) and 64.63% (GPT-5.6 Sol) down to 32.93% (Claude Sonnet 5) and 28.54% (MiniMax M3) (self-reported). 56 tasks were solved by all six backbones and 76 by none; pooling the six covers 334 tasks (81.46%).
- GPT-5.6 Sol trailed Grok 4.5 by 1.71 points yet spent 74.2% fewer tokens, took 50.3% fewer actions and ran 39.2% faster (self-reported). Per-task cost was $0.011 (MiMo-V2.5), $0.169 (Grok) and $0.200 (GPT). On five backbones, failed tasks consumed between 1.2 and 3.2 times the average tokens of solved ones.

Setup for the harness comparison: backbone fixed at MiMo-V2.5, each harness using its own native loop with the same 1,800 s limit and no shared action cap.

- Accuracy ran from 46.34% (Grok Build) through 44.63% (Claude Code), 39.27% (the DataSpace agent) and 34.88% (Codex) to 30.98% (Smolagents), a spread of 15.36 points (self-reported).

Setup for the stratified results: all 410 tasks, every backbone. The 134 multimodal tasks scored below the 276 single-modal ones for every backbone, with gaps of 1.8 to 14.0 points, and the 113 join tasks lowered scores by 9.7 to 19.8 points (self-reported).

Setup for the failure audit: the 136 failures of Grok 4.5. Answer materialisation accounted for 71 (52.2%) and intent for 31 (22.8%); adding or omitting columns (60) plus misstating output or row grain (17) made 77 (56.6%), and only 3 failures were the wrong evidence source (self-reported). The authors' reading is that a harness must produce the exact requested output, not just find and compute the right values.

## Limits

- Each configuration appears to be one run, with no seeds, variance or confidence intervals, so the extraction notes the 7-task gap between the top two backbones has no noise estimate.
- The harness comparison uses one cheap open-weight backbone, and each harness brings its own action budget and context handling, so the loops are not isolated; the ranking may not hold for stronger backbones.
- The authors call the stratified results descriptive, not causal, and the strata overlap.
- Tasks are synthetic renderings of Text-to-SQL items by LLMs, in finance, macro and healthcare only. Only 60 of 410 references are public.
- The failure audit covers one model; GPT-5.6 Sol proposed root causes and a human checked them, with no inter-annotator agreement. The extraction notes that the dominance of format failures partly reflects the strict schema contract.
- Several specialised data-agent systems were excluded as not runnable. Model names are as printed and were not verified by the extractor.

## See Also
- [[Terminal-Bench]] — related (another benchmark where the scaffold changed the same model's score)
- [[Trajectory Over Outcome]] — related (symptom versus root cause in trace audits)
- [[Eval Error Bars and Sample Size]] — related (single-run gaps with no noise estimate)
- [[AutoLab]] — related (harness changes moved scores there too)
