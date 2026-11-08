---
title: Agent S Hierarchical GUI Agent
tags: [harness, agents, pattern]
summary: "Agent S drives a desktop through a Manager that plans and a Worker that executes, with web knowledge plus two retrieved experience stores and a bounded action interface; with GPT-4o it roughly doubled the best prior OSWorld result (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-agashe-2024-agent-s.md
---

# Agent S Hierarchical GUI Agent

Agent S (an October 2024 preprint from Simular Research) is a computer-use agent whose learning happens entirely by retrieval; no weights change.

## Mechanism

- **Manager and Worker.** The Manager turns a task into subtasks, using web search plus retrieved experience fused into one guideline. A Worker handles each subtask step by step; a trajectory reflector gives it advice to avoid repeating actions.
- **Two memories.** Narrative memory (Manager side) holds abstracted summaries of entire task attempts (successes and failures) with the concrete actions stripped out, keyed by the task query. Episodic memory (Worker side) holds successful subtask plans with grounded actions, keyed by task, subtask and context. Retrieval is by embedding similarity. A self-evaluator writes both without human feedback or ground truth.
- **Bootstrapping.** Memory is first built by self-supervised exploration over generated tasks (the top 50 common tasks per application), then updated after every inference task.
- **Agent-computer interface.** One discrete primitive per step (11 in all, such as click, type, scroll, hotkey, drag, wait); elements are referenced by integer tags from the accessibility tree, augmented with OCR text blocks.

## Results (self-reported)

- OSWorld, 369 Ubuntu tasks, GPT-4o, screenshot plus accessibility tree: 20.58% against 11.21% for the best baseline. On WindowsAgentArena (154 tasks, GPT-4o): 18.2% against 13.3%, without adaptation, though the baseline's best agent used an inaccessible internal model.
- Ablations use a 65-task subset with GPT-4o: full 26.15; no web knowledge 16.80; no narrative memory 21.41; no episodic memory 18.46; none of the three 13.85. Without the self-evaluator (raw trajectories stored) 18.46; without exploration 15.38. Retrieval alone on the baseline barely helped (10.77 to 12.31) but helped a lot once the interface and hierarchy were present (12.31 to 20.00).
- On failed tasks, execution errors were the most common category (79.59%), then grounding (53.06%), with one task possibly carrying several.

## Limits

- The extraction notes internal inconsistencies: the continual-update ablation is 23.18 in the figure and 23.08 in the table; the overall for the no-web-knowledge ablation (16.80) disagrees with its column values; the text names a different Claude version from the table; the per-domain baseline row differs from Table 1.
- The authors concede they never measured step counts or elapsed time. Only GPT-4o and one Claude model were used. Ablations rest on 65 tasks, so single-point differences are noisy; the main comparison reports no seeds. The Windows result is weak in the Office category (0.0).

## See Also

- [[Computer Use Visual Grounding]] — related
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to (context paging, where Agent S retrieves task experience)
- [[Self-Learning Agents]] — related
- [[ComputerRL API-GUI Agent RL]] — alternative-to (trains weights where Agent S retrieves)
