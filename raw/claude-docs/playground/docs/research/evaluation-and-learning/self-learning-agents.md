# Self-Learning Agents

**Sources:** langgraph_Yan.pptx (reflection, memory taxonomy), langgraph_extended.pptx (corrective RAG subgraph), librarian wiki (copilot-learning-loop.md, plan-and-execute-pattern.md), fresh synthesis of ReAct / CoT / DPO literature

---

## The Four Levels of Agent Self-Improvement

From fastest/cheapest to slowest/most powerful:

| Level | Technique | When it helps | Cost |
|-------|-----------|--------------|------|
| **Inference-time** | ReAct, CoT, Self-critique | Single turn quality | Token cost only |
| **Session-time** | Reflection, procedural memory update | Improves within session | Latency + tokens |
| **Operational** | Copilot learning loop, HITL annotation | Improves across deployments | Human time |
| **Training-time** | DPO, RLHF | Bakes in preferences permanently | GPU + data cost |

Most production agents need all four layers. Start with inference-time, add session-time, then operational. Training-time is a later-stage investment.

---

## ReAct (Reasoning + Acting)

The foundational single-agent loop. The agent alternates between reasoning (Thought) and acting (Action) until it has enough information to answer.

```
Thought: I need to find the invoice for customer X
Action: search_invoices(customer="X")
Observation: Found 3 invoices — #1042, #1043, #1044
Thought: The user asked for the latest, so #1044
Action: get_invoice(invoice_id="1044")
Observation: Invoice #1044, 500 EUR, due 2026-05-01
Thought: I have all the info. Ready to answer.
Answer: Invoice #1044 for 500 EUR is due May 1, 2026.
```

**Where ReAct lives in LangGraph:** a single agent node that loops via conditional edges until the stop condition is met (no more tool calls pending).

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[get_invoice, list_invoices, create_invoice],
    checkpointer=checkpointer,
)
```

**ReAct is sufficient for:** 1-3 tool calls, well-defined tasks, low-stakes queries.

**ReAct breaks down when:** task requires 5+ tool calls in sequence, ordering matters, partial failure mid-sequence causes inconsistent state. Use Plan-and-Execute (see orchestration-patterns.md) for those cases.

---

## Chain of Thought (CoT)

An inference-time technique: the LLM is prompted to show its reasoning before giving an answer. The reasoning steps improve accuracy — especially for multi-step logic, arithmetic, and ambiguous queries.

### Zero-Shot CoT

Add "Let's think step by step" to the prompt:

```python
SYSTEM_PROMPT = """
You are a billing assistant.

When answering questions that require calculation or multi-step reasoning:
1. Think through the steps explicitly before giving your answer
2. Show your reasoning for any numbers or decisions
3. Then give your final answer

Example:
User: What's the total revenue from invoices this month?
Thinking: I need to: 1) list all invoices for this month, 2) filter to paid ones, 3) sum amounts
Action: [tool calls...]
Answer: Total revenue this month is X EUR (Y paid invoices)
"""
```

### Few-Shot CoT

Provide examples in the prompt that demonstrate the reasoning chain:

```python
FEW_SHOT_EXAMPLES = """
Example 1:
User: Create an invoice for Acme for the consulting work we did
Thinking: I need the customer ID for Acme (not just the name), the amount, and what products/services to line-item. I'll look up the customer first, then ask about amount if missing.
Action: list_customers(name="Acme")
...
"""
```

**When CoT pays off:**
- VAT calculations (multi-step arithmetic)
- Routing decisions with ambiguous intent
- Multi-customer queries ("which of my customers has the highest outstanding balance?")
- Error diagnosis ("why did this invoice fail to send?")

**CoT adds latency** — the reasoning tokens must be generated before tool calls. Keep examples short and targeted to your domain.

---

## Self-Critique (Inference-Time Quality Check)

After generating a response, the agent critiques its own output and revises if needed. A lightweight alternative to DPO for improving response quality at inference time.

```python
CRITIQUE_PROMPT = """
Review this response for accuracy and completeness:

User question: {question}
Your response: {response}

Check:
1. Are all numbers correct?
2. Is any required information missing?
3. Is the tone appropriate for a billing assistant?
4. Would this confuse the user?

If the response has issues, rewrite it. If it's correct, output it unchanged.
"""

async def self_critique_node(state: AgentState, llm) -> dict:
    response = state["draft_response"]
    critique_result = await llm.ainvoke(
        CRITIQUE_PROMPT.format(
            question=state["messages"][-1].content,
            response=response
        )
    )
    return {"final_response": critique_result.content}
```

**Cost:** doubles the token count for the response step. Use selectively — on high-stakes outputs (invoice creation confirmations, financial summaries) not every turn.

---

## Corrective RAG as a Self-Correcting Subgraph

From langgraph_extended.pptx. Standard RAG retrieves once and uses what it gets. Corrective RAG grades the retrieved chunks and re-queries if they're not relevant — a self-correcting loop.

```
Query
  │
  ▼
[Retrieve]  →  chunks
  │
  ▼
[Grade Relevance]
  │
  ├── relevant (score ≥ threshold) → [Generate Answer]
  │
  └── not relevant → [Re-query with rewritten question] → [Retrieve] (loop)
                      (max 2 retries before fallback)
```

```python
# Encapsulated as a standalone subgraph — reusable in any parent graph
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

**Why subgraph vs node:** self-contained, tested independently, reusable across multiple parent agents (support agent, reporting agent, etc.).

---

## Reflection (Session-Time Self-Improvement)

The agent evaluates its own performance mid-session and updates its procedural memory. See [memory-architecture.md](memory-architecture.md) for full implementation.

**Key distinction from self-critique:**
- Self-critique: "is this response correct?" — single turn, affects only this response
- Reflection: "what should I do differently going forward?" — updates procedural memory, affects future turns

**Reflection signals:**
1. User explicitly corrects the agent
2. User ignores agent suggestion and does something different
3. Task execution failed (tool error, API rejection)
4. Confidence score below threshold

**Hot-path vs background reflection** — see memory-architecture.md for the trade-off.

---

## DPO (Direct Preference Optimization)

A **training-time** technique. You collect preference data (human preferences over pairs of agent responses) and fine-tune the model to prefer the chosen responses.

### How It Works

1. **Collect pairs:** for the same prompt, collect response A and response B, where a human or judge marks which is preferred
2. **Train:** fine-tune the model using the DPO loss — maximise the probability of preferred responses, minimise the probability of rejected ones
3. **No reward model needed:** DPO directly optimises on preference pairs (unlike PPO/RLHF which requires a separate reward model)

```python
# Simplified DPO loss concept
# loss = -log(σ(β * (log π_θ(y_w|x) - log π_ref(y_w|x)) - β * (log π_θ(y_l|x) - log π_ref(y_l|x))))
# where y_w = preferred (won), y_l = rejected (lost), β = temperature
```

### When to Use DPO for VA Agents

**Good fit:**
- You have 1000+ labeled preference pairs from real user interactions
- Specific undesirable behaviours that prompt engineering can't fix (always recommending the wrong VAT rate, wrong tone in Danish vs English, etc.)
- You have a fine-tunable base model (not API-only models like Claude/GPT-4)

**Bad fit:**
- You're using API-only models (Claude, GPT-4) — you can't fine-tune these
- You have < 500 preference pairs — not enough signal
- The problem can be solved with better prompting — DPO is expensive overkill

**For API-based agents (current architecture):** DPO is not applicable. Use inference-time techniques (CoT, self-critique) + session-time reflection + operational learning loop instead.

### RLHF vs DPO

| | RLHF (PPO) | DPO |
|--|-----------|-----|
| Requires reward model | Yes (train separately) | No |
| Stability | Harder to tune | More stable |
| Compute cost | Higher | Lower |
| Data format | Scalar rewards | Preference pairs |
| Use case | Complex reward shaping | Preference alignment |

DPO has largely replaced PPO for preference alignment in 2024-2025. If you're fine-tuning, use DPO.

---

## Operational Learning Loop (The Wrapper)

The layer above all inference-time and session-time techniques. Drives systematic improvement across deployments.

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
    │
    ▼
[Monitor for regression]
```

See librarian wiki: `Copilot Learning Loop` for the full operational process.

---

## Recommended Stack by Agent Maturity

| Stage | What to implement |
|-------|------------------|
| **MVP** | ReAct loop, CoT in system prompt |
| **Beta** | Self-critique on high-stakes outputs, corrective RAG subgraph |
| **Production** | Reflection + procedural memory, operational learning loop, eval harness with regression gate |
| **Scaled** | DPO fine-tuning (if fine-tunable model), advanced episodic few-shot injection |

---

## See Also
- [memory-architecture.md](memory-architecture.md) — three-tier memory, reflection implementation
- [eval-harness.md](eval-harness.md) — eval harness that captures signals for the learning loop
- [hitl-and-interrupts.md](hitl-and-interrupts.md) — HITL annotation triggers reflection
- librarian wiki: `Copilot Learning Loop`, `Plan and Execute Pattern`, `Corrective RAG Pipeline`
