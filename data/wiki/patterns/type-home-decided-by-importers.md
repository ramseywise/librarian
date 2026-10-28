---
title: Type Home Decided by Importers
tags: [infra, pattern]
summary: "Where a type lives is decided by who imports it, not by what it describes. Shapes that cross the API wire go in the shared types layer, shapes read by one module stay with it, and a shape that has a runtime schema is inferred from it and never hand-written next to it."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/CLAUDE.md
---

# Type Home Decided by Importers

From the nonprofit-success-ai repo, a TypeScript SPA plus serverless `/api` handlers. Its
code is split into layers (UI, agents, shared). Without a rule, a "shared types" folder
fills up with everything that sounds domain-shaped. Then it imports agent code and
causes cycles, or it duplicates schemas and drifts from them.

## The rule

**The test is who imports it, not what it describes.**

- **It crosses the `/api` wire → shared `types/`.** If a handler and a browser caller must
  agree on the shape, it is a shared contract (routing input/result, plan request, draft
  inputs).
- **Only one module's internals read it → it stays with that module.** A scoring
  intermediate with no importer in `api/` or `lib/` does not move to `types/`, even
  though it describes a domain concept.

## One definition per shape

- If a wire shape has a runtime schema (zod), its type is **inferred**
  (`type X = z.infer<typeof xSchema>`). It is never hand-written beside the schema. A
  type-only import keeps the schemas → types direction from becoming a runtime cycle.
- Shapes with no runtime validation (UI view models) stay hand-written interfaces.
  Database row types come from the generator, not from hand-written code.
- **Same subject, different concern, stays separate.** The eval harness's fixture
  schemas validate JSONL at runtime and never cross the wire. So they are not merged
  into `types/`, although they describe the same agents.
- Migrate **per agent as its wire schema lands**, not all at once.

## Surrounding constraints that make it hold

- The shared layers import nothing above them (no UI framework, no agent code). This is
  lint-enforced, together with the agent-side arrows, so the type layer cannot quietly
  start depending on what depends on it.
- Only the shared `types/` has a barrel. Agent directories deliberately have none, so
  their exports cannot drift from a re-export list.

## See Also
- [[Stated Seams Drift, Enforced Seams Hold]] — instance-of (the layer arrows are lint-enforced, not documented)
- [[Server-Derived Autonomy Tier]] — related (from the same repo's layering: guardrails live outside each agent's directory)
- [[Structured Output]] — related (the runtime schemas whose types are inferred)
