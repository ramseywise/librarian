---
title: ADAS Meta Agent Search
tags: [harness, pattern]
summary: "ADAS defines an agent as code and has a meta agent program new agents from an archive of past discoveries; the discovered agents beat hand-designed ones, with small margins on knowledge-limited tasks."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hu-2024-automated-design-agentic-systems.md
---

# ADAS Meta Agent Search

ADAS (Hu, Lu and Clune, ICLR 2025) formulates automated agent design as search over code. In Meta Agent Search, a meta agent writes a new agent as a program, the program is evaluated, and it joins an archive that later proposals can build on.

## Setup

Search ran independently per domain for 30 iterations; the meta agent was GPT-4 (a gpt-4o checkpoint) and the discovered agents and baselines ran on gpt-3.5-turbo. Validation sets had 128 questions and test sets 800 (GPQA diamond: 32 and 166).

## Findings (self-reported)

- Test results against the best hand-designed agent: DROP F1 79.4 against 65.8; MGSM 53.4% against 39.0%; MMLU 69.6 against 65.9; GPQA 34.6 against 31.6. On MMLU and GPQA the margins sit inside the reported intervals, by the extraction's reading of Table 1.
- Code as the search space beat prompt-only optimisation in all four domains (DROP 79.4 against 69.1).
- ARC case study: stepping stones appeared at iterations 3, 5, 11 and 12, and the best agent combined three earlier ideas.
- Transfer within maths was strong (GSM8K 69.5 against 43.6). Transfer to reading comprehension was positive, to multi-task mixed (one agent below the best baseline), and to science at best a match. The authors hypothesise that models lack the knowledge for the science and multi-task questions, so better structure helps less; this is untested.
- Agents found on ARC with the weaker model kept their lead on stronger models, though the best agent on one model was not best on the others.

## Limits

- The text says the search used GPT-4 while the model name in the appendix is a gpt-4o checkpoint.
- The authors' claim of outperforming on multi-task transfer is generous given one agent scored 62.4 against a 65.9 baseline.
- Small test sets and intervals around 3 points on MMLU and GPQA.
- Searching from an empty archive still beat baselines, but seeding with human baselines helped in three of four domains.

## See Also
- [[Harness Engineering]] — prerequisite-for
- [[Harness Updating vs Harness Benefit]] — related (the meta agent here is a stronger model than the agents it designs)
- [[AutoHarness Synthesized Code Harness]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
