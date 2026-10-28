---
title: Settings Field Names Are a Shared Env Namespace
tags: [infra, pattern]
summary: "pydantic-settings binds every field to an environment variable named after it, so two independent Settings classes in one process that each declare `vectordb_path` both read `VECTORDB_PATH` — silently pointing two agents with incompatible schemas at one file; prefix or rename per component, and audit sibling Settings for collisions and drift."
updated: 2026-10-17
sources:
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--puffin-integration--plan.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--template-backlog--backlog.md
  - data/raw/repos/atlas/.claude--skills--akira--SKILL.md
---

# Settings Field Names Are a Shared Env Namespace

`pydantic-settings` maps each field of a `BaseSettings` class to an environment variable
with the field's name (case-insensitive) unless the class sets an `env_prefix`. Developers
treat each class as a private namespace. The environment, though, is one flat namespace
for the whole process. Every Settings class without a prefix is drawing names from it.

## The incident

While integrating a second example agent into the ai-project-template, the LangGraph agent
and a newly ported RAG agent each declared a `vectordb_path` field. Both read
`VECTORDB_PATH`. Setting it for one agent silently re-pointed the other at the same
vector-store file, and the two agents wrote incompatible schemas. Nothing errored at
import, at config load, or at render: the collision only shows when both agents run
against real data. The fix was a rename (`rag_vectordb_path`). It was caught by a real run,
not by the scripts used during the port. Those scripts never loaded both Settings classes
in the same process.

## The sibling failure: drift between parallel Settings

The same template hit the mirror-image bug more than once. Parallel Settings classes for
sibling agents are near-copies, and a field added to one was not added to its sibling. The
result was an `AttributeError` the first time an eval ran against the sibling in a
configuration where it was the only backend. A collision is "two classes share a name they
shouldn't". Drift is "two classes are missing a name they should share". Both come from
maintaining near-identical config classes by hand.

## Rules

- **Give each component's Settings an `env_prefix`** (`RAG_`, `LG_`), or name fields with
  a component prefix when the variable is genuinely component-specific.
- **Share a variable on purpose, through one base class.** A truly global setting (an API
  key) belongs in a shared base class, not in two independent declarations that happen to
  match.
- **Audit sibling Settings mechanically.** The bug class recurred enough that the template
  repo's codebase-quality agent runs a dedicated schema subagent. It diffs the
  `settings.py` / `schema.py` field names across the example agents for collisions and for
  drift.
- **Verify with every component loaded in one process,** under each toggle configuration
  that ships more than one of them (see [[Execute Every Toggle Configuration]]).

## See Also
- [[Execute Every Toggle Configuration]] — extends (the sibling-drift case appears there as a config-only bug)
- [[Silent Failure Catalogue]] — instance-of (wrong-but-plausible configuration, no error raised)
- [[AI Project Template Scaffold]] — instance-of
- [[Empty-String Env Override Defeats Nullish Coalescing]] — related (an env bypass that half works because of `??`)
