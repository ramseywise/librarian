---
title: Workflow Graph Static vs Dynamic Taxonomy
tags: [graph, reference]
summary: "Survey taxonomy of LLM-agent workflow optimisation: structure is static if it is a reusable template fixed after training or search, dynamic if any of it is selected, generated or edited at inference; the survey reports no experiments, only design guidance and a corpus of 77 works."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yue-2026-static-templates-dynamic-runtime-graphs.md
---

# Workflow Graph Static vs Dynamic Taxonomy

Yue et al. (arXiv 2603.22386, March 2026, preprint survey). The survey inventories 77 works in scope (39 core, 7 adjacent, 31 background) and 27 evaluation assets, and reports no accuracy, cost or latency numbers of its own. Its "when to use what" statements are the authors' synthesis, offered as cross-paper patterns rather than laws.

## The taxonomy

- **Three objects.** The template is the reusable design; the realised graph is what one run actually used; the trace holds that run's states, actions, observations and costs. Every run has a realised graph, so a method is dynamic only if some of that graph is chosen or revised at inference time.
- **Static** means the deployed structure is a reusable template that is fixed after training or search; it can contain loops and conditionals already encoded in the scaffold. Optimisation targets are the node (prompts, models inside a fixed scaffold), the graph, or both jointly.
- **Dynamic** has three plasticity modes: select or prune on a fixed super-graph, generate a graph before execution, or edit it during execution. A generator trained offline that produces a fresh plan for each input counts as dynamic; a pre-authored retry branch is static. The survey tags AgentConductor as an in-execution editing method.
- Methods are also described along feedback evidence (metric, verifier, preference, trace) and update mechanism (search, generator, controller, reinforcement learning, repair or edit).

## Design guidance (the authors' synthesis)

- Use the least plasticity the task needs. Selection suits tasks that vary mainly in difficulty or communication budget; generation pays when tasks need different structures; editing suits environments where runtime observations change what should happen next. Pruning cannot add a verifier or tool the super-graph lacks.
- A static graph is enough where operators are few, the evaluator is trustworthy and the workload recurs; a well-searched template can then beat runtime generation on cost and debuggability.
- Prompt tuning does not supply a missing node or information path, so inspect traces first. Dynamic control needs caps on tokens, tool calls and time, plus stopping rules and loop avoidance, as part of the workflow policy.
- Verifiers pay off most when cheap and meaningful (unit tests, schema, executability) and placed before expensive steps; textual feedback proposes, metrics or verifiers decide.
- Reporting proposal: papers should report the workflow that ran, the extent of its variation and its cost, with edit counts and structural variance for dynamic methods.
- Counter-evidence relayed second-hand: one cited paper argues that a single strong simulator can reproduce some multi-agent gains when the roles share a backbone.

## Limits

- No new experiments or pooled comparisons. The inventory is a snapshot of a field that moves quickly and excludes planning-only and tool-use-only work. Named open problems: structural credit assignment, expressivity against verifiability, adaptation under tool drift, benchmark quality, and the lack of any theory saying when dynamic generation is needed.
- The extraction notes the survey says little about named patterns such as supervisor-worker or fan-out; topology is treated as optimised graph structure rather than a catalogue.

## See Also
- [[Graph Topology Primitives]] — prerequisite-for
- [[AgentConductor Topology Evolution]] — instance-of
- [[Codebook Agent Amortized Topology Design]] — instance-of
- [[Multi-Agent Topology Patterns]] — prerequisite-for
