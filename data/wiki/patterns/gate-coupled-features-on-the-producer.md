---
title: Gate Coupled Features on the Producer, Not the Label
tags: [infra, pattern]
summary: "When a scaffold feature only makes sense if some other component exists (graders need a conversational agent, a retrieval service needs a caller), gate it on a predicate over the component that *produces* its input — not on a project-type label that usually correlates — and gate the per-item toggles too, so the coupling holds against an explicit override."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-genesis-dryrun.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-genesis-dryrun.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-17-template-core-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-17-template-core-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/multi-agent-tooling-expansion.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--multi-agent-tooling-expansion.md
  - data/raw/claude-docs/ai-project-template/docs/plans/AIT-32-plan.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--AIT-32-plan.md
---

# Gate Coupled Features on the Producer, Not the Label

Scaffold templates accumulate convenience predicates over the project *label* —
`is_agent_shaped`, `scaffold_full_project` — and then reuse them to gate features whose
real precondition is something else. The label and the real precondition agree in the
common case and diverge at the edges, and every divergence ships dead or broken code.

## The instance

In the ai-project-template, interaction-eval metrics (escalation, friction, intent
graders + LLM judges + a metrics registry) were gated on `is_agent_shaped` /
`scaffold_full_project`. What actually produces a gradeable conversational turn is
`primary_chat_agent`. Rendering an agent-shaped project with `primary_chat_agent=none`
produced a full interaction-eval harness — heuristics, judges, registry, sampling and
calibration pipelines, two `targets.yaml` keys — grading an agent the project did not
contain.

Fix: a new derived predicate `has_gradeable_interactions` keyed on the producer, with
`and is_agent_shaped` kept as a conjunct because `primary_chat_agent` defaults to a real
agent for a non-agent prototype shape — dropping it would have *added* evals to the half
that was already correct. Measure both halves before changing either.

## Gate the toggles, not just the seed

Changing only the multiselect's default would leave `-d eval_metrics=[intent]` free to
scaffold an intent grader on a project with no chat agent. Gating each per-metric toggle
on the predicate makes the coupling hold against an explicit override:

> *Which* metrics is a user choice; whether any interaction metric is coherent for the
> project is not.

## The same mistake elsewhere in the template

- **A service justified by a consumer that was switched off.** The retrieval service
  shipped "as shared infra backing the MCP tool" — in a render with the MCP server off.
  Its rationale had collapsed but its gate had not, dragging ~2 GB of embedding deps and
  a corpus pipeline into a project whose design put retrieval in a different service.
- **Integrations rendered with no caller.** Calendar and meeting-intelligence modules
  were mounted only through an n8n webhook router that the config had not scaffolded; a
  `try/except ImportError` swallowed the miss, so the app was healthy while the project's
  headline feature had zero HTTP surface. Gate a module on its mount point existing, and
  never let an ImportError guard turn an absent caller into silence.
  The guard was originally a deliberate design choice: mounting the optional router via
  `try/except ImportError` let every agent's `main.py` stay plain Python with no Jinja
  conditionals, and the type checker's resulting missing-import warnings were accepted as
  the same tradeoff as other optional backends. The convenience held until a second
  toggle depended on the router existing.
- **A corpus package gated on the wrong agent.** Gating the corpus pipeline on
  `include_rag_agent` alone would have broken the default chat agent's BM25 retrieval and
  the always-shipped retrieval eval. The shipped predicate was *any retrieving agent*.

## Dependencies follow the consumer too (AIT-32)

A later refactor applied the same rule to the dependency list. The scaffold's
`pyproject.toml` declared the corpus demo's heavy dependencies (`duckdb`,
`sentence-transformers`, `wandb`, and the pgvector/OpenSearch clients) unconditionally, so
even a minimal agent installed all of them. The fix:

- **Make the demo an additive layer over a minimal agent** — a bare guardrail→generate
  graph is the base; the corpus/RAG pipeline layers on top of it rather than being the
  default shape.
- **Grep each heavy dependency for its actual consumers** and gate it on a predicate over
  those consumers (e.g. `duckdb` only when the corpus pipeline exists *or* the RAG agent
  uses the duckdb vector backend) — the producer rule applied to imports.
- **Prove the refactor with byte identity.** `diff -r` of a feature-on render against a
  render from `main` must be empty; only the feature-off render is allowed to change.

The same pass found that the big staging `mv` moved `_scaffold/README.md` into the project
unconditionally — clobbering the project's own README on every re-render and bypassing
`copier --skip` entirely, since the task, not Copier's file merge, wrote the file. README
got its own task that moves the staged copy only when no README exists.

## See Also
- [[Circular Core Justification]] — extends (when the producer itself is only there for another example)
- [[Derived-and-Hidden Design Decisions]] — extends (silent derivations that ship code nobody chose)
- [[Test Derived Defaults Without Overrides]] — related (verifying the predicate without supplying its value)
- [[Execute Every Toggle Configuration]] — prerequisite-for (the edge configs where label and producer diverge)
- [[Silence Reads as Clean]] — related (the swallowed ImportError)
- [[AI Project Template Scaffold]] — instance-of
