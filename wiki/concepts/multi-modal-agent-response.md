---
title: Multi-Modal Agent Response
tags: [adk, mcp, pattern, concept]
summary: Agent response pattern where output can include text, data visualizations, interactive UI components, and full task surfaces — moving beyond chat to structured elicitation and guided execution.
updated: 2026-04-25
sources:
  - raw/notion/2026-04-09-copilot-why-what-how.md
  - raw/claude-docs/playground/docs/plans/va-agent-systems.md
---

# Multi-Modal Agent Response

In production agent systems, a response is not always a text message. Agents that operate within a UI can generate structured outputs that reduce ambiguity and shorten the path from intent to completion.

---

## Response Types

| Type | Description | Use Case |
|---|---|---|
| **Structured text** | Markdown with headers, bullets, steps | Explanations, step-by-step guidance |
| **Data visualizations** | Charts, tables, financial summaries | Insights, financial analysis |
| **Interactive UI components** | Buttons for confirmation, dropdowns, constrained choices | Disambiguation, approval flows |
| **Action prompts** | Suggestion/Automation cards | Proactive nudges, next-step shortcuts |
| **Full task surfaces** | Invoice forms, draft previews, structured workflows | Guided execution, creation flows |

---

## Structured Elicitation

The core idea: rather than asking users to describe everything in natural language, the agent generates UI elements that make it easier for users to provide precise input.

Examples:
- **Buttons for confirmation** — "Was this expense a meal with clients?" [Yes] [No] [Something else]
- **Dropdowns or constrained choices** — instead of "which VAT rate?", show available options
- **Pre-filled forms** — agent generates an invoice draft with available fields filled; user reviews and confirms
- **Editable fields** — surface the specific field that needs correction, not the full form

**Why it matters:** Natural language input is ambiguous. Structured elicitation removes ambiguity without requiring the user to know the right terminology.

---

## Interaction Level Mapping

Structured elicitation maps across the three-level interaction hierarchy (from [[Shine Copilot Architecture]]):

| Level | Response Pattern |
|---|---|
| Level 1 — Explicit AI | Open-ended text; reasoning visible; errors tolerated |
| Level 2 — Guided Intelligence | Constrained choices; pre-filled forms; AI visible but bounded |
| Level 3 — Invisible Automation | No UI, no AI branding; background processing |

---

## VA Agent Implementation

The [[VA Agent Project]] `AssistantResponse` schema demonstrates this pattern in production:

```python
class AssistantResponse(BaseModel):
    message: str                          # text — always present
    suggestions: list[str] = []          # follow-up chips
    nav_buttons: list[NavButton] = []    # deep-links into app
    table_type: str | None = None        # structured data table
    form: FormConfig | None = None       # inline creation form
    confirm: bool = False                # Confirm/Discard HITL pattern
    chart_data: ChartData | None = None  # financial chart
    metric_cards: list[MetricCard] = None # KPI tiles
    alert: Alert | None = None           # proactive warning
```

The `format` LangGraph node uses `llm.with_structured_output(AssistantResponse)` to populate this schema — the LLM decides which fields to populate based on the domain result.

---

## Design Principle: Match Response Type to Context

- **Always answering with text** misses opportunities for precision (forms, pre-fills, charts)
- **Always generating UI** adds friction to simple questions that need only a text answer
- **The agent should choose** response type based on: intent type, current user context, whether action is required

For action-oriented workflows (create invoice, correct categorization), lean toward forms and confirmations. For explanatory workflows (why is this expense in this account?), lean toward structured text with source references.

---

## See Also
- [[Shine Copilot Architecture]]
- [[VA Agent Project]]
- [[ACI (Agent-Computer Interface)]]
- [[Plan and Execute Pattern]]
- [[Agentic Workflow Patterns]]
