---
title: SKILL.state
tags: [context, pattern]
summary: "SKILL.state replaces the growing transcript with a fixed spec, a JSON state the model updates by validated patch, and the latest observation; on the authors' synthetic Warehouse benchmark it held 0.94 accuracy at 100 steps on 65,408 tokens against 1,062,387 for a stateful baseline (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-badhe-2026-skill-state.md
---

# SKILL.state

Badhe, Tiwari and Chung (a single-lab preprint) propose a runtime for long-horizon agent loops. Each step the prompt holds three parts: a fixed specification, a structured JSON state, and the latest observation. The model reasons, then returns a state patch and an action; the reasoning is discarded after the step. The runtime validates the patch deterministically, merges it into the state (a dictionary merge where a null value deletes a key), then runs the action. A patch that fails validation is rolled back and the step is retried. The authors argue prompt size stays constant and cumulative cost grows linearly instead of quadratically; that claim is asymptotic reasoning and was not measured. The extraction notes that "skill" here covers any procedure the agent runs, with nothing on skill files or discovery.

## Results (all self-reported)

- **Token cost.** The setup is the Warehouse task of SkillExecBench with 500 shelves, run on Gemini-3-Flash at temperature 0 over 5 seeds. At 100 steps SKILL.state scored 0.94 on 65,408 tokens; a LangGraph-style stateful baseline scored 0.91 on 1,062,387 tokens (16.2 times more). At 200 steps SKILL.state held 0.94 on about 122k tokens while ReAct scored 0.74, Memory 0.84 and Stateful 0.88.
- **Structure against compression at equal prompt size.** Same setup at 100 steps with a budget of about 1,800: truncated window 0.18, capped summary 0.52, ReAct with LLMLingua 0.22, SKILL.state 0.94.
- **Stale facts.** After a silent world change in hand-built scenarios, history-based baselines needed 5 to 8 recovery steps on Warehouse and 8 to 14 on a software-repository task; SKILL.state needed none.
- **Public benchmarks.** InterCode CTF (100 tasks, one static five-field schema, single run): the best baseline reached 46.4% pass@1 and SKILL.state 54.2%, with 60.4% fewer tokens than ReAct.
- **Small models.** Gemma-4-31B at 100 steps scored 0.42 (self-reported), tied with Stateful; 68% of its errors were premature overwrite or deletion of existing state keys.

## Limits

- The authors state the method assumes state is a sufficient summary of the past, and it breaks down if the schema cannot be known beforehand, when relevance is not recognised on first sight, or when the task concerns the history itself.
- Single-agent only; small models would need grammar-constrained decoding, left as future work.
- The extraction notes: headline results use one frontier model; the benchmark was built by the authors and suits key-value state; the Stateful baseline retains the transcript next to a state block; public-benchmark runs report no variance; the schema is hand-written per domain with no cost reported; no latency is measured.
- Internal inconsistencies: the budget is given in both tokens and characters; for Airline the text puts baseline prompt peaks above 11,000 tokens per step while Table 4 shows 4,700 to 5,400; the text claims an edge under injected noise that the table does not show because Memory and Stateful also score 0.98 to 1.00.
- On the repository task SKILL.state lost to Stateful at 25 steps (0.88 against 0.94).

## See Also
- [[Structured Context and Schemas]] — prerequisite-for
- [[Context Compaction]] — alternative-to
- [[Context Failure Modes]] — related (stale facts after a silent change)
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to
