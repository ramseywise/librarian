---
title: JAZ Invoke Loop
tags: [harness, pattern]
summary: A minimal agent loop in which the model writes code, subagents are recursive calls, and all inputs and history are REPL variables, so long recall is code-searching the raw history instead of using a memory tool.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2026-harness-as-language.md
---

# JAZ Invoke Loop

JAZ (Li et al., mostly MIT CSAIL, a September 2026 preprint) is a framework built around a minimal "invoke" loop in which the LLM writes code and subagents are recursive calls, and every input plus the REPL history is a variable in the REPL. When context fills, the agent hands off to a subagent, passing the full history by reference (the paper calls this tail-recursive delegation), and the successor searches the raw history using code. There is no memory store or memory tool, and the paper claims prompting alone is enough.

## Results (self-reported)

Mean with standard error; solver GPT-5.4 nano unless noted.

- On the far-recall subset of StuLife (207 of 939 graded tasks, taken from an ordered sequence of 1,284, high reasoning, 3 runs), JAZ invoke scored 69.9 pass at $18.3 a run, Letta (MemGPT) v0.16.8 scored 61.8 at $42.1, CodeAct plus subagents 32.0; per-task CodeAct without memory 24.8.
- All 939 graded StuLife tasks: JAZ 72.6, Letta 70.9, CodeAct plus subagents 60.0.
- AppWorld test-challenge (417 tasks, 6 runs for self-improving methods, 3 for others; meta-agent GPT-5.4): task goal completion 74.2 for JAZ, 71.1 for CodeAct plus subagents, 69.9 for ACE, 67.5 for per-task CodeAct; cost $20.9 against $30.6 for ACE. Margins are one to two standard errors.
- One case: the needed lecture came from a task 497 tasks earlier; JAZ got it right in all 3 runs, Letta in one, CodeAct plus subagents never. In Letta, its only search tool did not support exact substring matching.

## Limits

- Two benchmarks and one small solver model. Memory across separate sessions is not tested: history is raw and lossless, with no distillation, staleness or contradiction handling, and recall is exact-match search over a full, unabridged history. Cost and latency could rise as history grows; one run reached 70 delegations.
- Letta caveats: in the SQL search backend most results came back empty, so hybrid search replaced it; Letta needed tasks delivered as user messages; and most Letta prompts looped, so one prompt is reported. The comparison may favour JAZ. To save cost, ACE only learned from the first 42 tasks.
- The claim about prompts alone is valid only within restrictions the authors set themselves, and the paper has no dedicated limitations section.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Prime Agent State Hierarchy]] — related (also a REPL with recursive subagents)
- [[Long-Horizon Execution]] — related
