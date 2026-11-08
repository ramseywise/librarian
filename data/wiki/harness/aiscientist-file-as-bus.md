---
title: AiScientist File-as-Bus
tags: [harness, pattern]
summary: "AiScientist coordinates a long-horizon ML research agent through durable, schema-governed files rather than conversation, keeping orchestration thin; removing the file bus costs far more on later-round refinement than on producing a first runnable result."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-toward-autonomous-long-horizon-engineering.md
---

# AiScientist File-as-Bus

AiScientist (Chen et al., an April 2026 preprint, revised May) is a hierarchical system for ML research tasks that run for 24 hours. Its design choice is thin control over thick state: a light orchestrator hands work to specialists, and the specialists share state through a workspace of files with a defined schema (the paper calls this File-as-Bus) instead of passing summaries in messages.

## Findings (self-reported)

- PaperBench (20 tasks, one GPU, 24 hours, single run): 30.52 against 20.60 for the matched iterative baseline with Gemini-3-Flash, and 33.73 against 22.37 with GLM-5. Cost per task was $15.67 against $27.44 and $12.20 against $54.90.
- MLE-Bench Lite (22 tasks, three seeds): 81.82 Any Medal under both backbones, 4.55 and 16.67 points above the strongest matched baseline. A Codex (GPT-5.5 xhigh) reference, not matched to the other runs, scored 29.45 on PaperBench and 68.18 on MLE-Bench Lite.
- Ablation: dropping File-as-Bus cost 6.41 points on PaperBench and, on MLE-Bench Lite, 31.82 points of Any Medal rate. Valid submissions and bronze medals mostly held; above-median, silver and gold results fell. The authors read this as durable state mattering for later rounds of diagnosis and improvement, and not for producing a first runnable result.

## Limits

- The ablation is given as a figure, not a table, and there are no error bars on PaperBench.
- The Codex reference is not matched on model.
- A full PaperBench evaluation costs about $832 to grade.
- The paper has no limitations section and no failure analysis, per the extraction; the figure axes were garbled in extraction.

## See Also
- [[Long-Horizon Execution]] — prerequisite-for
- [[PaperBench]] — prerequisite-for
- [[MLE-bench]] — prerequisite-for
- [[Loop State File]] — prerequisite-for
- [[Paper-Replication Completion Gate]] — related
