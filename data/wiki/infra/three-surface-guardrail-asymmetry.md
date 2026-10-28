---
title: Three-Surface Guardrail Asymmetry
tags: [infra, pattern]
summary: "Guardrails on an agent's three text surfaces should react differently — block the untrusted user turn, neutralize a poisoned span in retrieved/tool content, scrub leaked values from model output before both caller and tracer — with a deliberate fail-open-when-disabled / fail-closed-when-crashing asymmetry and a result whose text field is safe by construction."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
---

# Three-Surface Guardrail Asymmetry

The ai-project-template's security step scaffolded three guard layers. The design point
is that one hit-action for all three surfaces is wrong.

| Layer | Runs on | On a hit |
|---|---|---|
| `check_input` | untrusted user turn, before the model call | **blocks** — returns a refusal message |
| `filter_content` | tool/retrieval output, before it enters the prompt | **neutralizes** — replaces the span, keeps the rest |
| `check_output` | model output, before the caller *and* before the tracer | **scrubs** — replaces values, still delivers |

- `filter_content` is the **indirect-injection seam**: a poisoned document is not a user
  turn, so the input check never sees it.
- Layers 2 and 3 deliberately **do not block**. Dropping a whole retrieved passage
  degrades answers in ways that look like retrieval bugs; blocking a response over one
  leaked token turns a scrub into an outage.

## Fail-open vs fail-closed, on purpose

A layer switched **off** in settings fails open — that is an operator decision. A layer
that **raises** fails closed (refusal, or empty content for layer 2) — a crashing guard
must not become an availability hole *or* a bypass. Both directions were verified by
execution, not assumed.

## Safe by construction

`GuardResult.text` is always the safe value, so a call site that ignores `blocked` and
just uses `text` still behaves safely. Blocked verdicts return the refusal message, never
the rule ids — ids go to logs, traces and evals; surfacing them teaches a probing caller
what tripped.

## Redact before trace

`check_output()` runs **before** the tracing module's `redact()`, so a value the model
leaked never lands in observability tooling even in redacted form. The two are
complementary, not redundant: `redact()` matches **field names** in span attributes;
`check_output()` matches **value shapes** in free prose, where there is no key to match.

## See Also
- [[Input Guardrails Pipeline]] — extends (the input-surface stages in detail)
- [[Safeguards Architecture — Five Protection Layers]] — related
- [[Streaming Output Scrubbing]] — related (the output surface under streaming)
- [[Presidio PII Redaction for Langfuse]] — related (field-level redaction at the tracer)
- [[Prompt Injection]] — prerequisite-for
- [[AI Project Template Scaffold]] — instance-of
