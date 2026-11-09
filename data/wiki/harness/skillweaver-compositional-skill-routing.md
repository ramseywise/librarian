---
title: SkillWeaver Compositional Skill Routing
tags: [harness, pattern]
summary: "SkillWeaver routes a multi-skill query by decomposing it, retrieving skills per sub-task and composing them; its SAD step re-decomposes with retrieved skill names as hints, lifting exact step-count accuracy from 51.0% to 67.7% on the authors' CompSkillBench (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gao-2026-compositional-skill-routing-llm-agents.md
---

# SkillWeaver Compositional Skill Routing

Gao (Alibaba Cloud, single author, preprint) argues that skill routing is usually framed as picking one skill, while real queries need several. SkillWeaver has three stages: an LLM decomposer splits the query into sub-tasks, a bi-encoder (all-MiniLM-L6-v2) with a FAISS index retrieves skills for each sub-task, and a composer arranges the chosen skills into a dependency graph. The paper identifies decomposition granularity, meaning how many sub-tasks the query is split into, as the bottleneck. Its remedy, which the paper calls **SAD**, retrieves skills for the first-pass sub-tasks and then asks the decomposer to try again with the retrieved skill names as hints.

## CompSkillBench

The benchmark has 300 synthetic template queries over 2,209 real skills (entries from an awesome-mcp-servers list) in 24 categories. The skills in this pool are descriptions of MCP servers rather than SKILL.md contents.

## Results (self-reported; decomposer Qwen2.5-7B-Instruct at temperature 0.1, one run)

- Decomposition accuracy (exact step count) went from 51.0% up to 67.7% under SAD (Wilcoxon p<1e-6, n=300); within one step, 71.3% to 84.3%. The extraction notes the headline "+32.7%" is relative; the absolute gain is 16.7 points.
- Category recall at 1 moved from 34.2% to 37.0%, not significant (p=0.17); recall at 10 stayed about 69 to 70%.
- A vanilla 7B told the true step count reached 99.3% decomposition accuracy, which suggests SAD mostly corrects granularity.
- Listing 100 skill names in the prompt (qwen-max, n=50, ground truth included) gave decomposition accuracy 0.90 but category recall at 1 of only 0.211.
- Context cost: listing every one of the 2,209 skills would cost about 884K tokens, using an assumed 400 tokens each that was not measured, whereas retrieving the top 10 costs about 4,000 tokens.
- Cross-model spot checks, n=50 each: Qwen2.5-14B decomposition accuracy 32% to 68%; qwen-max 66% to 92%.

## Limits

- Queries are synthetic and templated; just the skill pool is real, and the metric is category recall instead of exact-skill match or execution.
- The compose stage is never evaluated alone, and the execution pilot uses mock executors.
- The 7B decomposer dominates; neither GPT-4o nor Claude was tried.
- The 99% context saving rests on the assumed 400 tokens per skill.
- The extraction reports it found no results comparing body-aware encoding with metadata-only, so "metadata suffices" rests on recall at 10.
- Convergence of the re-decomposition loop is argued by pigeonhole, which the extraction calls weak.

## See Also
- [[Dynamic Tool Discovery]] — prerequisite-for
- [[Skill Discovery Failure Modes]] — related
- [[Skill Authoring Discipline]] — related (descriptions drive retrieval)
- [[AnyTool]] — alternative-to (hierarchical retrieval over a large API pool)
- [[Learned Skill and Action Libraries]] — related
