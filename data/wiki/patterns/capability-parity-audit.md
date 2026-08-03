---
title: Capability Parity Audit
tags: [llm, pattern]
summary: A method for deciding what a shared template should absorb next — classify every requested capability as have / partial / gap against the template's *verified* current state, then prioritize by how many consumers share the gap rather than by how loudly any one asked.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/multi-agent-tooling-parity.md
---

# Capability Parity Audit

When two or more downstream projects each arrive with a tool stack a shared template
doesn't fully cover, the tempting move is to design for each one separately. The audit is
the alternative: compare both stacks against the template at once, and let the overlap
decide the roadmap.

The framing sentence is the whole method: *"Rather than design one-off, this research
compares both stacks against the template's actual current state ... to find the overlap
worth prioritizing."*

## Three classifications, not two

The audit's discriminating move is refusing a binary. Every capability lands in one of
three buckets:

| Class | Meaning | What it costs |
|---|---|---|
| **Have** | A working, exercised implementation exists | Zero — point the project at it |
| **Partial** | An existing pattern generalizes to it | Extension, not invention |
| **Gap** | No pattern to build from | Net-new subsystem |

Collapsing `partial` into `gap` is what makes roadmaps wrong. In the source audit,
Supabase/pgvector looked like a large gap and was in fact the cheapest of the three shared
items, because two real extension points already existed — a `PostgresSaver` branch
stubbed with `NotImplementedError`, and a `get_vector_index()` factory whose exact shape
had already been proven out by adding OpenSearch. The conclusion follows directly:

> *"This isn't 'add a new subsystem,' it's 'finish two half-built extension points using a
> pattern the template already proved out.'"*

Collapsing `partial` into `have` is the opposite error and appears in the same matrix:
Pydantic-AI is marked partial because the *discipline* it enforces (Pydantic models at API
boundaries) is already a hard convention — but the agent framework itself is absent. The
classification records both facts instead of picking one.

## Verified state, not remembered state

The method is explicit that the baseline is read, not recalled: the audit was performed
*"verified by reading `copier.yaml`/`template/_scaffold/` directly, not from memory,"* by
grepping the scaffold, hooks, and skill trees for each capability.

This matters more for a template than for a normal codebase. A template's author is also
its heaviest user, so their mental model is the *rendered* project they last worked in, not
the parameterized source. Memory systematically over-reports `have`. Grepping for zero
references is the only claim that survives review — and it is the claim the matrix actually
makes, capability by capability. Same discipline as
[[Verified Runtime Capability Constraint]], applied to inventory rather than to runtime
behavior.

## Shared gaps outrank loud ones

Prioritization is by consumer count, not by requester enthusiasm or technical interest.
Three capabilities appeared in both projects' stacks and became the roadmap; everything
requested by exactly one project was explicitly deprioritized *for the template*, while
remaining real work for that project.

The reasoning is that a template's value is amortization. A gap one project has is that
project's problem to solve locally; a gap two projects share is the template's problem,
because solving it twice is the waste the template exists to prevent.

Within the shared set, ordering is by **cost given existing extension points**, which is
why the audit ran the `partial` classification at all — the cheapest shared gap was
sequenced first, the architecturally largest last, with its size estimated by analogy to a
comparable item already on the backlog rather than guessed.

## Collapsing the long tail

The single-consumer gaps were not enumerated as N separate work items. Several of them —
four SaaS APIs plus two web-research tools — were observed to reduce to one shape: *"plain
'call an external REST API with an API key' integrations that don't need template-level
toggles so much as one clearly-documented pattern + example."*

Recognizing that a long tail of named tools is one unnamed pattern is the audit's highest-
leverage output, because it converts a list that grows with every new project into a
document that doesn't. The precedent named is `include_mcp_server`, which *"ships one worked
example rather than a connector for every possible tool."* See
[[Integration Pattern Selection]] for the pattern that tail collapsed into.

## The "explicitly not recommended" section

An audit that only produces a roadmap is half-finished; the source ends with three
non-recommendations, each closing a plausible misreading of the matrix:

- **Don't scaffold the external service itself.** A hosted workflow tool is not something a
  project generator installs — see [[Callable-By Integration Contract]].
- **Don't unify two orchestration frameworks behind one abstraction.** *"That's the kind of
  premature multi-backend abstraction the project's own conventions warn against when
  nobody's asked for it"* — treat them as independently-selectable, the same shape as the
  existing framework-choice toggle. This is [[Complexity Floor]] reasoning applied to a
  gap the audit itself just identified.
- **Don't chase parity on the long tail** inside one pass.

Writing these down is what keeps the matrix from being read as a to-do list. A `gap` cell
records absence; it does not assert that the absence should be closed.

## See Also
- [[Integration Pattern Selection]] — extends (what the long tail collapses into)
- [[Callable-By Integration Contract]] — extends (the shape a shared gap resolved to)
- [[Verified Runtime Capability Constraint]] — complements (read the state, don't recall it)
- [[Complexity Floor]] — constrains (a gap is not automatically work)
- [[AI Project Template Scaffold]] — instance-of (the template audited)
- [[Copier Re-Entry as Capability Path]] — complements (how a closed gap reaches rendered projects)
- [[NYC-DSSG Project]] — instance-of (the two consuming projects)
- [[Asked vs Derived Scaffold Variables]] — extends (a new capability usually becomes a toggle)
- [[Six-Pillar Agent Engineering Assessment]] — alternative-to (a fixed rubric rather than a per-consumer request matrix)
- [[Template Floor Raising]] — complements (prioritize by portfolio weakness rather than consumer count)
- [[Capability Runtime-Coupling Tiers]] — alternative-to (runtime-coupling axis rather than have/partial/gap)
