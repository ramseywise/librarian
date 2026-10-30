---
title: Toggle Gates the Capability, Not the Runtime Default
tags: [infra, pattern]
summary: "A scaffold toggle for an optional backend should only decide whether the dependency and code path exist; flipping the runtime default too is safe for lazily-consumed components but breaks every import of an eagerly-consumed one (e.g. a checkpointer built at graph-compile time), so the default stays the in-memory option and opt-in is an explicit env var."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/multi-agent-tooling-expansion.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--multi-agent-tooling-expansion.md
---

# Toggle Gates the Capability, Not the Runtime Default

Adding a Postgres backend to a copier template introduced two toggles: `postgres` as a
`vector_backend` choice, and `enable_postgres_checkpointer` for LangGraph persistence.
The original design made the checkpointer toggle also flip the **runtime default** of
`LG_CHECKPOINTER` to `postgres`. Rendering was clean. `make test` failed 4 of 36 tests in
a fresh render with a raw `psycopg.OperationalError`.

## Why one backend tolerated it and the other did not

| Component | When it is consumed | Effect of a remote default with no DB |
|---|---|---|
| Vector index | **Lazily** — per call, via a factory | Only a code path that actually searches fails |
| Checkpointer | **Eagerly** — module-level `build_graph()` at import | Every test that merely imports `main.py` opens a connection |

The difference is not the backend; it is *when the default is read*. A default that is
read at import or compile time is effectively executed by every test, every CLI command,
and every tool that touches the module.

## The rule

- The toggle controls **whether the dependency and the working code path exist** in the
  render.
- The runtime default stays the safe local option (`memory`) unconditionally.
- Opting in is an explicit env var (`LG_CHECKPOINTER=postgres` + a DSN) set once a
  database is actually reachable — the same precedent every other optional backend in the
  template followed.
- Keep related toggles orthogonal: Postgres vectors with in-memory checkpointing (and
  vice versa) are both legitimate, so neither toggle implies the other.
- Unreachable-backend behaviour is verified by explicit opt-in against a dead DSN: it
  must fail fast with a clear connection error, not hang.

This was caught only by running the test suite in the toggled configuration — the
argument of [[Execute Every Toggle Configuration]].

## See Also
- [[Execute Every Toggle Configuration]] — instance-of (a bug that renders cleanly and fails only when run)
- [[Runtime Topology and Checkpointer Alignment]] — related (where the checkpointer must live once opted in)
- [[Test Derived Defaults Without Overrides]] — related (defaults as the untested surface)
- [[AI Project Template Scaffold]] — related (part of)
