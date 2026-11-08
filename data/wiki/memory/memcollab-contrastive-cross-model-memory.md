---
title: MemCollab Contrastive Cross-Model Memory
tags: [memory, pattern]
summary: "MemCollab builds one memory bank shared by several models from the contrast between their trajectories on the same task; the paper finds that memory distilled from one model can lower another model's score, and that contrasting different models beats contrasting two samples from one model (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chang-2026-memcollab.md
---

# MemCollab Contrastive Cross-Model Memory

MemCollab (a 2026 preprint) asks how memory written by one model can be reused by another. Its starting observation is that plain transfer can hurt: in the paper's own setup, a Qwen2.5-7B-Instruct agent given memory distilled from 32B trajectories (Buffer-of-Thoughts style) scored 50.6 on MATH500 against 52.2 with no memory, and 34.1 on HumanEval against 42.7 (self-reported, that setup). Memory came from 1000 training items; each dataset's test split held 500 separate items (HumanEval has 164 tasks). Runs used temperature 0, a smolagents CodeAgent and seed 42.

## Mechanism

For each task, two trajectories from different models are paired, one preferred and one not. By default the stronger model's trajectory is preferred; if it fails while another succeeds, the successful one wins. That means build time needs a correctness signal, either a verifier or ground truth. A contrast prompt turns each pair into abstract entries of the "when X, enforce Y; avoid Z" form, tagged with the model labels of the pair. No raw trajectories, demonstrations or final solutions are stored.

Retrieval is two-step: filter to the task category, then keep only entries in which the target model appears as winner or loser, take the top 3 by TF-IDF, and use up to 3 constraints from each. The authors call the result a shared bank with model-aware retrieval, not a model-agnostic one.

## Results (MATH500, GSM8K, MBPP and HumanEval; single run unless noted)

- Average accuracy across the four benchmarks, listed as vanilla, own-model memory, MemCollab: Qwen-7B 57.1, 59.8, 71.6. Qwen-32B reads 70.8, 75.6, 79.6. And for Llama-3-8B the three values are 41.7, 45.6, 53.9 (self-reported).
- Contrasting two samples from the same model (self-contrast) averages 67.5 for Qwen-7B against 71.6 for MemCollab; for Llama-3-8B it is 45.0 against 53.9 (self-reported).
- An ablation on MBPP with Qwen2.5-7B varies how the preferred trajectory is picked. The default rule scores 57.6; random choice 50.2; reversed choice 52.9; and with no memory the score is 47.9 (self-reported).
- Average reasoning turns for Qwen-7B fall from 3.1 to 1.4 on MBPP and from 3.3 to 1.5 on HumanEval (self-reported).
- On AppWorld, task goal completion rises from 47.7 to 63.3 for GPT-5-mini and from 4.8 to 26.7 for GPT-5-nano (self-reported).

## Limits

- The authors' single stated limitation: safety filtering and access control for a shared memory are left to later work.
- The extraction notes that models are mostly Qwen2.5 and Llama-3 (4B to 72B) on math and code tasks with checkable answers. Because memory is built and evaluated within the same task families, the notes add that carry-over to new domains is not shown.
- Building memory means running several models over the training tasks and having a correctness signal. One test swapped that signal for model self-selection (ASQA) and still showed a gain (Qwen-7B 15.4 to 21.3, self-reported, ASQA test).
- Seed spread appears only for the main configuration; other tables are single runs. The no-memory 7B HumanEval run has a spread of 5.32, so small gaps are noisy.
- The mechanism explanation ("suppressing model-specific bias") is an interpretation, not tested by an experiment.
- Internal inconsistencies (the extraction notes): prose near Table 2 gives Llama-3-8B 74.4% on MATH500, yet the table row reads 42.4 (74.4 is its GSM8K number); Table 2 also shows Qwen-32B MemCollab at 70.6 on MATH500 where Table 1 has 73.8. GPT-5-mini serves as the memory-quality judge.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory Forms Taxonomy]] — prerequisite-for
- [[Memory Transfer Learning in Coding Agents]] — related (a second study of memory moving between models and domains)
- [[ArcMemo Concept-Level Memory]] — alternative-to (abstract memory entries instead of raw traces)
