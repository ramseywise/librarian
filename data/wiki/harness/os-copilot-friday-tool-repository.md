---
title: OS-Copilot FRIDAY Tool Repository
tags: [harness, pattern]
summary: A generalist computer agent with four control methods behind one runtime, a tool repository the agent grows by writing Python tools gated by a critic score, and a DAG planner.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2024-os-copilot.md
---

# OS-Copilot FRIDAY Tool Repository

OS-Copilot (Wu et al., ICLR 2024) builds FRIDAY, an agent that treats a Python interpreter, bash, API calls and mouse and keyboard control as one runtime interface on Linux and macOS. The authors built and evaluated it.

## Mechanism

- **Tool repository:** seeded with 4 hand-made tools; the agent writes the rest as Python classes (subclassing BaseAction) or POST-invoked services. A short description doubles as the retrieval key, and tools are recalled by dense retrieval. The similarity threshold is not given.
- **Generation and gating:** if no stored tool is similar enough, a Tool Generator writes one. A critic scores it from 1 to 10 for reuse, and only tools above 8 are kept. Failed actions get at most 3 self-correction attempts.
- **Planner:** a DAG planner runs subtasks that do not depend on each other in parallel, giving each a sub-agent of its own, and is given a list of atomic tools so it plans at the right granularity.
- **Learned tools are small:** names such as sort_excel_by_column.

## Reported numbers (self-reported)

Setup: model GPT-4-turbo-1106; tools are 4 seeds and 9 more learned from the GAIA dev set; scored on the official server.

- GAIA level 1: FRIDAY 40.86, GPT-4 Plugins 30.30, FRIDAY without learning 36.56. Levels 2 and 3: FRIDAY 20.13 and 6.12; without learning 17.61 and 6.12.
- SheetCopilot-20 (20 of 221 tasks, Pass@1, GPT-4): FRIDAY goes from 0% to 60% after 10 self-set tasks and 8 accumulated tools. The SheetCopilot GPT-4 figure of 55% is quoted from its authors, not rerun.
- The authors credit the planner, critic and refiner for the gap over AutoGPT-4 but did not ablate them.

## Limits

- No ablation of retrieval and generation against a fixed tool set, and no test of description wording or tool-set bloat; one model and one budget-limited run, with no variance.
- The extraction notes internal inconsistencies: for AutoGPT-4 the text says 14.4% but Table 1 says 15.05, and for FRIDAY the text gives 105 s while Table 3 gives 118 s (the same table has AutoGPT-4 at 456 s, whereas the text says "more than 500").
- The critic is LLM-judged; the authors concede prompting dependence, no GUI input, read-only web browsing and untested safety.
- Dated to the 2024 GPT-4-turbo era.

## See Also
- [[Tool Design as Harness Surface]] — related
- [[Harness Orchestration]] — related
- [[CoAct-1 Coding Actions for Computer Use]] — related
