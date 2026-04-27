---
title: Chain of Thought
tags: [llm, concept, pattern]
summary: Inference-time technique where the LLM is prompted to show its reasoning before answering — improves accuracy on multi-step logic, arithmetic, and routing decisions with no training cost.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/self-learning-agents.md
---

# Chain of Thought

## What It Is

Chain of Thought (CoT) is an inference-time technique: the LLM is prompted to show its reasoning steps before giving an answer. The reasoning improves accuracy — especially for multi-step logic, arithmetic, and ambiguous queries. No training required, only prompt design.

## Zero-Shot CoT

Add "think step by step" to the prompt:

```python
SYSTEM_PROMPT = """
You are a billing assistant.

When answering questions that require calculation or multi-step reasoning:
1. Think through the steps explicitly before giving your answer
2. Show your reasoning for any numbers or decisions
3. Then give your final answer
"""
```

## Few-Shot CoT

Provide examples in the prompt that demonstrate the reasoning chain:

```python
FEW_SHOT_EXAMPLES = """
Example:
User: Create an invoice for Acme for the consulting work we did
Thinking: I need the customer ID for Acme (not just the name), the amount, and
  what products/services to line-item. I'll look up the customer first, then ask
  about amount if missing.
Action: list_customers(name="Acme")
...
"""
```

## When CoT Pays Off

- **VAT calculations** — multi-step arithmetic
- **Routing decisions** with ambiguous intent
- **Multi-entity queries** ("which customer has the highest outstanding balance?")
- **Error diagnosis** ("why did this invoice fail to send?")

## When CoT Is Not Worth It

- Simple single-turn lookups — adds latency for no benefit
- API-only models already do internal reasoning — zero-shot prompting is often sufficient
- You need sub-200ms response time — reasoning tokens add latency before tool calls

## Self-Critique (Related Pattern)

After generating a response, the agent critiques its own output and revises if needed — a lightweight inference-time quality check:

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
```

**Cost:** doubles the token count for the response step. Use selectively — on high-stakes outputs (invoice creation confirmations, financial summaries) not every turn.

## Key Distinction from Reflection

| | CoT / Self-critique | Reflection |
|--|-------------------|-----------:|
| Scope | Single turn | Future turns |
| Effect | Better response now | Updated procedural memory |
| Cost | Token cost | Token cost + storage write |

See [[Agent Memory Types]] for the reflection implementation.

## See Also
- [[ReAct Pattern]]
- [[Self-Learning Agents]]
- [[Agent Memory Types]]
