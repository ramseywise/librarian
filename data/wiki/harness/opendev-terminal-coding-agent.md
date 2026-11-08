---
title: OpenDev Terminal Coding Agent
tags: [harness, reference]
summary: "A single-author engineering report on a terminal coding agent: scaffolding versus harness, staged context compaction, tool-output offloading, lazy MCP discovery, system reminders, doom-loop detection and schema-level safety; design constants with no benchmark."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bui-2026-building-effective-ai-coding-agents.md
---

# OpenDev Terminal Coding Agent

Bui's report (March 2026, single author, a preprint) describes OpenDev, a Rust CLI coding agent. It splits scaffolding (assembling the system prompt, tool schemas and subagent registry before the first prompt) from the harness (runtime orchestration of tool dispatch, context, safety and persistence). The author states the paper "lacks systematic quantitative evaluation": every figure below is a design constant or the author's own unreported-setup measurement (self-reported).

## Design choices

- **Schema-level safety:** a Planner subagent gets a read-only schema, so write tools are absent rather than blocked at call time. The design stacks five layers: guardrails in the prompt, restrictions in the schema, approval at runtime, validation of tools, and lifecycle hooks. A PreToolUse hook with exit code 2 hard-blocks a call, and default danger rules at priority 100 cannot be overridden by user configuration. There are ten hook events.
- **Staged compaction:** tool outputs take 70 to 80% of context in typical sessions. Compaction escalates through warning, observation masking, pruning, aggressive masking and full LLM compaction at thresholds up to 99%; masked observations shrink to about 15 tokens and full history is archived to a file. The author says this cut peak observation context by about 54% (no setup given). Token counts use the API's prompt_tokens rather than local estimates.
- **Offloading:** tool outputs over 8,000 characters go to a scratch file with a 500-character preview and path. A test-suite output fell from 30,000 tokens to under 100; sessions ran 30 to 40 turns before overflow instead of 15 to 20 (the author's development history, no controlled test).
- **Lazy MCP discovery:** loading every schema at the start took as much as 40% of context, and a discovery tool searching by keyword cut this to below 5%. Skills load only their frontmatter at startup.
- **System reminders:** short single-purpose reminders injected as user-role messages before the decision point counter instruction fade-out seen after about 15 tool calls; each has a cap (todo nudges 2, error nudges 3). The author reports higher compliance than system-role injection, with no figure.
- **Doom-loop detection:** an MD5 fingerprint of tool name and arguments over a window of 20, with a threshold of 3 repeats, triggers a warning and then a human approval pause.
- **Prompt cache split:** 19 of 21 prompt sections are stable; the author works out roughly an 88% saving in input cost for the cached portion from pricing, not from a test.
- **Thinking separate from action:** a tool-free thinking call, on the author's claim that absent tool schemas change behaviour; no ablation.
- **Subagents** run in isolated context with filtered tools and return a summary; todo tools are withheld from them.
- **Edit tool:** a chain of 9 progressively looser matchers, a stale-read check, and LSP diagnostics appended after edits.

## Limits

- No benchmark, ablation, baseline, repeat runs or confidence intervals; the 54%, the 40% and 5%, and the 88% figures come with no named model or task set, and the 88% is an estimate from pricing. Thresholds are globally fixed.
- Internal inconsistencies in the paper: compaction stages (four in the appendix table, five in the text), number of thinking-depth levels (4 or 6), the subagent iteration cap (15 or none), and the count of built-in tools (about 40 or 35).
- Related-work figures the paper quotes from others are second-hand.

## See Also

- [[Harness Engineering]] — prerequisite-for
- [[Harness Anatomy]] — prerequisite-for
- [[Loop Detection and the Two-Retry Rule]] — related
- [[Dynamic Tool Discovery]] — related
- [[Coding-Agent Search and Edit Schemes]] — related
