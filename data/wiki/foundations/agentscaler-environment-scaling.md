---
title: AgentScaler Environment Scaling
tags: [foundations, llm, pattern]
summary: "AgentScaler builds function-calling environments automatically by treating every tool call as a read or write on a generated database, filters trajectories by final database state, and SFTs in two stages; its 30B model scored 70.4 on tau-bench Retail (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fang-2025-towards-general-agentic-intelligence-environment.md
---

# AgentScaler Environment Scaling

AgentScaler (Tongyi Lab, a September 2025 preprint) treats a function call as a read or write over a domain database, so a whole environment can be generated from a set of APIs and verified by diffing database states.

## Pipeline

1. **Domains from a tool graph.** APIs (from ToolBench, an API-generation dataset and an internal repository) are linked when parameter embeddings are similar enough; community detection then splits the graph, giving over 1,000 domains out of 30,000-plus APIs. An LLM checks tool pairs within a domain.
2. **Materialise tools.** Each tool becomes Python code over a generated database schema. The authors report by manual inspection that schemas for tau-bench domains look consistent with the official ones.
3. **Tasks from walks.** Directed walks over the tool graph give tool sequences; a simulated user, agent and environment then produce trajectories.
4. **Three-stage filter.** Validity control (well-formed turns, n-gram repetition removal); state alignment (final database equals the gold state); an exact function-call comparison for sequences that only read, since a database diff cannot tell those apart. Trajectories containing tool errors are kept when they still reach the goal.
5. **Masked SFT.** Loss applies to tool-call and assistant tokens only; user and tool turns stay in context but are masked.
6. **Two stages.** General tool use across domains first, then vertical-domain specialisation.

## Results (self-reported)

Base Qwen3-Thinking-30B-A3B, pass^1 on tau-bench and tau2-Bench, accuracy on ACEBench-en: Retail 70.4, Airline 54.0 (tau-bench); 70.2, 60.0, 55.3 (tau2 Retail, Airline, Telecom); ACEBench-en overall 75.7. Kimi-K2 is ahead on tau-bench Retail (73.9) and tau2 Telecom (65.8), and GPT-5-think reaches 96.7 on Telecom. The 4B model gains over its base (ACEBench-en overall 65.9 against 49.5) but its agent subset is only 30.8. On ACEBench-zh, all three sizes beat their bases overall.

Consistency drops as trials are required to all pass: on tau2-Bench the 30B model's weighted score falls from 62.5 at k=1 to 30.6 at k=4, and accuracy falls as tool calls per task rise.

## Limits

- The extraction notes that Table 2 and the pass^k figure values are interleaved, so series pairing is inferred; the text also uses "Qwen3-4B" loosely for the thinking variant and duplicates one reference.
- No ablation of the filter funnel and none varying the number of environments, so "scaling" is untested. SFT only, up to 30B; no training-set size is given, no seeds, and the user-simulator model is not named in the extraction. The authors concede closed models still lead and long-horizon use stays open.
- Baselines date from mid-2025.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[APIGen]] — prerequisite-for (execution-verified function-calling data; AgentScaler adds generated environments)
- [[Salesforce Koa]] — related
- [[AutoGym Blueprint-First Verifiable Gyms]] — alternative-to
