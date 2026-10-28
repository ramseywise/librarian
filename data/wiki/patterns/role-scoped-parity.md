---
title: Role-Scoped Parity
tags: [infra, pattern]
summary: When two backends in one template play different roles, "does the second tree have this?" is the wrong parity question — ask "does its role require this?"; that reclassified a missing eval suite as a deliberate asymmetry and left observability and security as the only real gaps.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/frameworks/va-langgraph-production-parity.md
  - data/raw/claude-docs/playground/docs/frameworks/agent-feature-parity.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold-decision-tree.md
  - data/raw/claude-docs/project-g/docs/frameworks/agent-feature-parity.md
  - data/raw/claude-docs/project-g/docs/frameworks/va-langgraph-production-parity.md
---

# Role-Scoped Parity

A structural diff of the ai-project-template's Python and TypeScript roots produced a
parity table with five apparent gaps. Reading each row against the *role* of the TS
backend reversed one of them and reframed the whole exercise.

## The reversal

The Python eval root grades **retrieval** (hit rate, MRR) against an in-process search
function. The TS agent is a tool-calling assistant with no retrieval step; grading it on
hit rate "would be meaningless". Its own `run.ts` instead hits the live chat endpoint
over HTTP and scores answer overlap, deliberately porting one heuristic so it carries no
Python dependency. The header comment of that file documented the reasoning; the parity
table had read the absence of a grader suite as a gap.

> The two eval suites grade different things because the two backends *are* different
> things. Porting the grader suite would produce metrics with no referent.

The correct action was to preserve the asymmetry and make the rationale visible somewhere
other than a source comment — not to add a work item.

## The frame

The Python root is a multi-capability research backend (ETL, ML, RAG, evals,
integrations). The TS root is a single-purpose serving agent (one `streamText()` call, a
tool registry, a step-count loop, three dependencies). So per row the question is not
"does TS have this?" but **"does the TS backend's role require this?"**:

| Tree | Verdict | Why |
|---|---|---|
| observability | gap | a serving agent makes LLM calls needing traces identically |
| security guards | gap | guards wrap an LLM turn regardless of language |
| evals | deliberate asymmetry | no retrieval step to grade |
| ETL, ML, notebooks | correct asymmetry | research-backend concerns |
| auth middleware | gap only under one topology | the frontend already carries its own |

Observability and security survived as real gaps because the grep for any synonym across
the whole TS tree returned zero files — the asymmetry was total, not a naming difference.
Even then, *intent* stayed at Medium confidence: no ADR said "TS backends are
intentionally thin", and the honest audit records that it found no evidence either way.

## A shared surface instead of a port

Where a cross-language eval is wanted, the finding points at the language-agnostic layer
already present — an HTTP-targeting eval config in the universal shell — rather than
porting one language's graders into the other.

## The grounding target follows the evidence source

A parent orchestrator that delegates support questions to a child RAG agent should not be
parity-checked against the child's internals. Its parity target is user-facing behaviour
and the tool contract: the response shape, preserved passages, trace metadata and the
failure fallback. Grounding is checked where the evidence came from. Support answers are
checked against citation URLs inside the delegated agent. **Non-support claims, such as
accounting records, are checked against the returned tool or fixture records, not against
URL-grounding datasets.** Running a URL-grounding eval on a tool-answering agent measures
nothing about whether its claims are true.

## See Also
- [[Capability Parity Audit]] — extends (have/partial/gap, with the extra question of whether the role needs it)
- [[Template Floor Raising]] — related (which gaps become template work)
- [[Eval vs Test Distinction]] — related (an eval grades the product the backend actually is)
- [[AI Project Template Scaffold]] — instance-of
- [[Capability Runtime-Coupling Tiers]] — extends
