---
title: Self-Learning Agents
tags: [langgraph, adk, memory, eval, concept]
summary: Four-level improvement stack for production agents — inference-time (ReAct, CoT, self-critique), session-time (reflection, procedural memory), operational (learning loop, HITL), and training-time (DPO). Most agents need the first three; DPO is a late-stage investment.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/self-learning-agents.md
---

# Self-Learning Agents

## The Four Levels of Self-Improvement

From fastest/cheapest to slowest/most powerful:

| Level | Technique | When it helps | Cost |
|-------|-----------|--------------|------|
| **Inference-time** | [[ReAct Pattern]], [[Chain of Thought]], self-critique | Single turn quality | Token cost only |
| **Session-time** | Reflection, procedural memory update | Improves within session | Latency + tokens |
| **Operational** | [[Copilot Learning Loop]], HITL annotation | Improves across deployments | Human time |
| **Training-time** | [[Direct Preference Optimization]], RLHF | Bakes in preferences permanently | GPU + data cost |

Most production agents need all four layers. Start with inference-time, add session-time, then operational. Training-time is a later-stage investment.

## Corrective RAG as a Self-Correcting Subgraph

Standard RAG retrieves once and uses what it gets. Corrective RAG (from LangGraph pptx) grades retrieved chunks and re-queries if they're not relevant:

```
Query → [Retrieve] → chunks
                        │
                   [Grade Relevance]
                        │
           ┌────────────┴────────────┐
      relevant                 not relevant
           │                        │
    [Generate Answer]    [Rewrite query] → [Retrieve] (max 2 retries)
```

```python
crag_builder = StateGraph(CRAGState)
crag_builder.add_node("retrieve", retrieve_node)
crag_builder.add_node("grade", grade_relevance_node)
crag_builder.add_node("rewrite_query", rewrite_query_node)
crag_builder.add_node("generate", generate_answer_node)

crag_builder.add_conditional_edges(
    "grade",
    lambda s: "generate" if s["relevance_score"] >= 0.7 else "rewrite_query",
)
crag_builder.add_edge("rewrite_query", "retrieve")
crag_graph = crag_builder.compile()

# Wire into parent as a node
parent_builder.add_node("knowledge_retrieval", crag_graph)
```

**Why subgraph vs node:** self-contained, tested independently, reusable across multiple parent agents.

See also [[LangGraph CRAG Pipeline]] for the full implementation.

## Reflection (Session-Time Self-Improvement)

The agent evaluates its own performance and updates its procedural memory. See [[Agent Memory Types]] for the full implementation.

**Key distinction from self-critique:**
- Self-critique: "is this response correct?" — single turn, affects only this response
- Reflection: "what should I do differently going forward?" — updates procedural memory, affects future turns

**Reflection trigger signals:**
1. User explicitly corrects the agent
2. User ignores agent suggestion
3. Task execution failed (tool error, API rejection)
4. Confidence score below threshold

**Hot-path vs background:** see [[Agent Memory Types]] for the latency trade-off.

## Operational Learning Loop

The layer above all inference-time and session-time techniques — drives systematic improvement across deployments:

```
Production signals (corrections, overrides, low-confidence turns)
    │
    ▼
[HITL Annotation] — attribute failure to root cause
    │
    ├── Wrong routing → update evalset routing cases
    ├── Wrong tool args → update tool descriptions
    ├── Tone/quality issue → update system prompt (procedural memory)
    └── Missing knowledge → update KB (semantic memory)
    │
    ▼
[Automated Eval] — measure improvement on golden set
    │
    ▼
[Deploy if eval floor maintained]
```

See [[Copilot Learning Loop]] for the full operational process.

## Recommended Stack by Agent Maturity

| Stage | What to implement |
|-------|------------------|
| **MVP** | [[ReAct Pattern]] loop, [[Chain of Thought]] in system prompt |
| **Beta** | Self-critique on high-stakes outputs, corrective RAG subgraph |
| **Production** | Reflection + procedural memory, operational learning loop, [[VA Eval Harness]] with regression gate |
| **Scaled** | [[Direct Preference Optimization]] fine-tuning (if fine-tunable model), advanced episodic few-shot injection |

## See Also
- [[ReAct Pattern]]
- [[Chain of Thought]]
- [[Direct Preference Optimization]]
- [[Agent Memory Types]]
- [[LangGraph CRAG Pipeline]]
- [[Copilot Learning Loop]]
- [[VA Eval Harness]]
