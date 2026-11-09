---
title: Buffer of Thoughts
tags: [prompting, pattern]
summary: "Buffer of Thoughts distils each problem into key information and retrieves a stored thought-template from a growing meta-buffer, so one query instantiates a template instead of searching; it reports gains on 10 GPT-4 tasks at about 12% of multi-query cost, measured as time (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yang-2024-buffer-thoughts.md
---

# Buffer of Thoughts

Buffer of Thoughts (BoT, a NeurIPS 2024 paper) stores reusable high-level reasoning templates and retrieves one per problem. A problem distiller first extracts key information, restrictions and a distilled task from the question. The distilled task is matched, by comparing embeddings of each template's description with the distilled problem, against a meta-buffer of thought-templates in six categories. If nothing clears a similarity threshold (0.5-0.7 recommended) one of three coarse general templates is used. The retrieved template, for example Python code that enumerates number and operator combinations for Game of 24, is instantiated in a single query. A buffer manager distils a template from each solved problem and adds it only when its maximum similarity to existing templates is below the threshold.

## Results

All figures are self-reported; the base model is GPT-4 unless noted.

- Game of 24: 82.4 against Tree of Thoughts 74.0, Graph of Thoughts 73.2 and PAL 64.0. Checkmate-in-One: 86.4 against 57.2 for Meta Prompting.
- Cost: roughly 12% of what multi-query methods need, averaged; the comparison measures inference time, and covers only three tasks (Game of 24, MGSM, Checkmate-in-One), not tokens.
- Buffer manager ablation (50 random questions per round, four tasks): accuracy rises across four rounds from 56.8 to 88.5 with the manager and stays between 52.8 and 57.4 without it; time per problem falls from 297 s to 78.5 s with it.
- Removing the meta-buffer or the problem distiller hurts the harder tasks (Game of 24, Checkmate-in-One) more than easy ones; the extraction could only partly read these values from garbled charts.

## Limits

- The authors concede limited gains for problems needing human-like creativity, and weaker templates when a weaker model initialises the buffer.
- The extraction notes that the abstract's 11% margin on Game of 24 over the prior method disagrees with the 23% in the body.
- The extraction notes that benchmarks are narrow and static, buffer-manager rounds sample the same benchmarks (favourable to template reuse), efficiency is wall-clock time, and no seeds or error bars exist beyond a 10-run robustness test. Fig. 3-10 values come from garbled chart text.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Analogical Prompting]] — related (both reuse worked solution patterns)
- [[Self-Discover]] — alternative-to (composes a plan per task rather than retrieving a stored template)
- [[Tree of Thoughts]] — alternative-to
