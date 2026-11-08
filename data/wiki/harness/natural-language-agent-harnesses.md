---
title: Natural-Language Agent Harnesses
tags: [harness, concept]
summary: Write harness policy (stages, state, acceptance) as a natural-language document that a runtime executes, while code keeps exact mechanisms; compared with code and plain-prompt harnesses on three benchmarks, with module ablations.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pan-2026-natural-language-agent-harnesses.md
---

# Natural-Language Agent Harnesses

Pan et al. (a May 2026 preprint, Tsinghua and HIT Shenzhen) propose writing the harness as a natural-language document (an NLAH) executed by a shared runtime (IHR). The thesis is a split: natural language holds the policy of the harness, and code plus the runtime hold the exact mechanisms (tool execution, parsing, sandboxing, logging). The paper defines a harness as the external execution system around a model, covering eleven aspects: agent loop, tool design, context engineering, workspace and filesystem, memory and state, stopping and validation, sandboxing and safety, runtime defaults, observability, retry and recovery, and budget control.

The system has four layers: a base agent whose only tool is a terminal, a fixed runtime policy, the replaceable NLAH, and deterministic scripts. A harness with one agent still runs as a parent orchestrator plus a single executor child. The paper's writing rules favour clauses that define observable behaviour (for example, writing a state file before delegating) over phrases like "be careful".

## Results

All numbers are the authors' own measurements; every run used Codex CLI 0.123.0 with gpt-5.4-mini at xhigh reasoning effort, in Docker, with one attempt and no variance reported.

- Static policy size, counting files only: Live-SWE 60.1k tokens of code against 2.9k as an NLAH; MHTBA 10.5k against 0.8k; SeeAct 47.5k against 1.4k (self-reported).
- Task scores, code harness / plain prompt / NLAH under IHR: on SWE-bench Verified (Live-SWE-Agent) 67.0, 77.0 and 73.0; on Terminal-Bench 2.0 (MHTBA) the three were 36.0, then 57.3, then 53.9; on OSWorld 47.1, 47.9 and 46.3 (self-reported). Plain prompting of the same text beat IHR on SWE and Terminal-Bench, so the runtime is not shown to add task gain over prompting.
- The MHTBA code harness, tuned for Claude Opus 4.6, scored 36.0 here; 45 of 89 runs failed on a timeout. The paper traces it to a two-call stopping protocol that this model did not follow, and states that code harnesses can carry model-specific assumptions.
- Module ablations, each adding one module to a Basic condition (SWE 73.0, OSWorld 44.4): file-backed state 75.6 and 58.3; self-evolution 78.8 and 52.8; verifier 73.2 and 52.8; multi-candidate search 71.4 and 47.2; context compression 72.0 and 36.1; Markdown memory 70.2 and 50.0 (self-reported). On SWE, multi-candidate search took agent calls up from 1.1 to 5.7.
- Runtime audit: under parent-child execution, recall of handed-off information dropped to 0.32 on SWE and 0.55 on MHTBA, where the plain prompt had 1.00.
- Overhead: on Live-SWE the NLAH used 41.0 LLM calls against 23.3 for code and 2.2M prompt tokens against 283.6k; on Terminal-Bench the code harness used more.

The paper says production systems should keep safety, permissions, evaluation and key parsing in code.

## Limits

- One model and one runtime substrate, single attempt, no confidence intervals. A few ablation deltas are tiny (+0.2, -1.0 and -1.6), and the extraction reads these as noise-level.
- The code baselines are third-party artifacts not re-tuned for this model.
- The abstract claims only comparable outcomes, not better accuracy. Natural-language imprecision, prompt injection through harness text and a prototype runtime are conceded limits.
- Model and CLI versions are specific snapshots that will date.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Harness Anatomy]] — prerequisite-for
- [[Iterative Harness Simplification]] — related
- [[Verification Loops]] — related
