---
title: Production Readiness Backlog
tags: [infra, rag, reference]
summary: The pre-launch gap checklist for a RAG service going to managed cloud hosting — auth, CORS, structured logging, tests, CI gate, staging separation, probes, retries, migrations — each stated as current-state vs required.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/chat-agent/docs/backlog.md
---

# Production Readiness Backlog

A checklist of the gaps that separate a working agentic RAG prototype from a
service that can be deployed to a managed cloud runtime (Cloud Run + Cloud SQL).

This is a **different axis** from [[Production Hardening Patterns]]. That page
catalogues code-level defects found in review — blocking event loops, SQL
injection, missing warmup. This page catalogues *infrastructure and process*
gaps: things that are absent entirely rather than implemented wrongly. A
codebase can pass every hardening item and still fail every item here.

## The checklist

Each item is written as **current state → required**, which is the format that
makes a backlog actionable: it names the specific artifact that must change,
not just the goal.

| # | Gap | Current state | Required |
|---|---|---|---|
| 1 | Credential model | API keys in config | Application Default Credentials (ADC) — no keys in prod |
| 2 | API authentication | `--allow-unauthenticated`, no middleware | Cloud Run IAM (internal) or JWT/API-key (external) |
| 3 | CORS | `allow_origins=["*"]` | Explicit frontend domain allowlist; `*` for local dev only |
| 4 | Logging | `print()` throughout | `structlog`/`logging` emitting JSON to stdout |
| 5 | Tests | Zero test files, no `pytest` dep | Unit tests for tools, integration tests for endpoints |
| 6 | CI gate | Build + deploy only | `pytest` + `ruff check` step before build, failing the build |
| 7 | Environments | Single service, one secret set | Staging service with its own DB and secrets |
| 8 | Probes | `/api/health` returns static `ok` | Liveness + readiness split; readiness returns `503` |
| 9 | Retries | None on model/embedding calls | Exponential backoff; circuit breaker for sustained outages |
| 10 | Schema | `CREATE TABLE IF NOT EXISTS` inline | Alembic versioned migrations tracked in-repo |

## The two items with non-obvious mechanics

Most of the list is well-known hygiene. Two items have real design content.

### Liveness vs readiness are different questions

A single `/api/health` that returns `{"status": "ok"}` conflates them, and the
conflation is what makes it useless:

- **Liveness** — "is this process alive?" Must be cheap and must NOT check
  dependencies. If it checks the database, a database blip causes the
  orchestrator to *kill and restart healthy containers*, converting a
  recoverable outage into a crash loop.
- **Readiness** — "should traffic be routed here?" Checks the Postgres
  connection, that the vector store is loaded, and that credentials resolve.
  Returns `503` when not ready, so the load balancer withholds traffic without
  killing the process.

The failure mode of getting this backwards is worse than having no probes at
all. See [[Cloud Run + Cloud SQL Pattern]] for the deployment-side config.

### `CREATE TABLE IF NOT EXISTS` has no rollback path

Inline schema creation looks like it works because it is idempotent on a fresh
database. It silently stops working the moment the schema needs to *change* —
`IF NOT EXISTS` will not add a column to an existing table, so the statement
succeeds while doing nothing, and the mismatch surfaces later as a query error.
There is no version record and therefore no rollback. Introducing Alembic before
the first production schema change is much cheaper than reconstructing history
after it.

## Why "not yet tracked" is worth recording

The source backlog explicitly notes which items are and are not tracked as
issues. That distinction is the useful part: a known gap that exists only in a
markdown file has no owner and no cadence, and is functionally invisible during
planning. Promoting checklist items into tracked issues is the step that makes
the backlog real — see [[Agile Workflow Definitions]] for the DoR gate that
tracked items pass through.

## See Also
- [[Production Hardening Patterns]] — alternative-to
- [[Cloud Run + Cloud SQL Pattern]] — prerequisite-for
- [[PGVector Migration Pattern]]
- [[Agile Workflow Definitions]]
