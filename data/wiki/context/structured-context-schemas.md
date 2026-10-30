---
title: Structured Context and Schemas
tags: [context, llm, concept]
summary: "Structure compresses meaning rather than tokens — tags for boundaries, markdown for prose, JSON for anything code reads back; schemas belong in three places (input, state carried across turns, output), and state should be small, structured, versioned, validated and overwritten rather than appended."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--07-structured-context.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--06-memory.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--13-putting-it-together.md
---

# Structured Context and Schemas

When the shape of content is consistent, the model spends less attention working out
what each part *is*. Structure belongs to the **Write** lever of [[Context Engineering]].

## Why Structure Helps

- **Separates instructions from data.** Tagged sections make retrieved text harder to read
  as a command — a partial injection mitigation, not a guarantee ([[Prompt Injection]]).
- **Addressability.** "Use the `<constraints>` block" resolves; "the constraints above"
  may not.
- **Consistency across calls** — your code can parse, diff and validate it.

Mechanistic background: an ICML 2025 result identifies a three-stage
abstraction → induction → retrieval circuit in LLMs; slot-shaped content fits it. This is
a plausible explanation, not a proven design rule.

## Choosing a Format

| Format | Best for | Watch out for |
|---|---|---|
| XML-style tags | Wrapping documents, sections, nesting | Verbosity; keep names meaningful |
| Markdown | Instructions, human-readable prompts | Weak boundaries — a retrieved doc's `##` collides with yours |
| JSON | Machine state, tool I/O | Token-heavy; escaping |
| YAML | Config-like nested state | Whitespace; ambiguous types |
| Tables | Comparable records | Wide tables lose alignment |

**Rule of thumb: tags for boundaries, markdown for prose, JSON for anything a program reads
back.** See [[XML Prompt Structuring]].

## Three Places Schemas Go

1. **Input schemas** — a fixed task skeleton (Task / Context: background, constraints,
   examples / Data / Output Format). The value is the fixed order and *visible empty
   slots*: a missing Constraints section shows at a glance. See
   [[Prompt Templates and Variables]].
2. **State schemas** — what carries across turns: **small, structured, overwritten, not
   appended** (`goal`, `decisions`, `open_questions`, `files_touched`, `next_step`).
   This is the compaction target and the memory format. The MEM1 result (RL-trained agents
   that keep one internal state overwritten every turn match or beat larger models on long
   multi-hop QA at near-constant memory) generalises without training: **a fixed-size,
   rewritten state block beats an ever-growing log.**
3. **Output schemas** — provider structured-output mode when code consumes the answer;
   otherwise schema-in-prompt plus one filled example, validated on receipt. See
   [[Structured Output]].

## Relational Evidence as Structure

Passing relational facts as prose forces the model to rebuild the graph. Triples or
adjacency lists (`(svc-a) -[calls]-> (svc-b)`) turn multi-hop questions into lookups.
See [[Index-Time Distillation]] for graph-shaped indexes.

## Schema Design Principles

| Principle | Test |
|---|---|
| Clarity | Could a new engineer fill it in without asking? |
| Consistency | Do two prompts disagree on a field name? |
| Flexibility | Is there a `notes`/`other` escape hatch, or does an odd case break the schema? |
| Efficiency | Ablate the field — does anything change? |

Two habits matter more than the principles:

- **Version schemas.** A schema change invalidates eval baselines just as a prompt change
  does; put a `schema_version` in state blocks.
- **Validate at the boundary.** Parse model-written state before writing it back. A
  malformed state block that is re-injected compounds every turn — context poisoning
  ([[Context Failure Modes]]).

A **user schema** (goals, expertise, preferences, history) kept outside the window and
selectively injected is the same pattern as structured memory ([[Memory as Context]]).

## See Also
- [[Context Engineering]] — extends
- [[Structured Output]] — extends (the output-schema case)
- [[XML Prompt Structuring]] — prerequisite-for
- [[Context Compaction]] — prerequisite-for (state schemas are the compaction target)
- [[Agent Status Bar]] — instance-of
- [[Protocol Shells]] — extends (an input schema with the process made explicit)
