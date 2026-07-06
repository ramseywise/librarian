# Galactus Tooling Overview

This is the entry map for humans and agents. It points to the canonical
runbooks and code entry points without duplicating their full instructions.

## Primary Runbooks

| Area | Canonical runbook | Use it for |
|---|---|---|
| Eval experiments | [`evals/README.md`](../evals/README.md) | Stats, quality grading, live agent calls, LangFuse experiments, report rendering |
| Data ingestion and preprocessing | [`core/README.md`](../core/README.md) | Article ingestion, conversation preprocessing, BKH/GT preparation |
| Data layout | [`data/README.md`](../data/README.md) | Dataset locations, generated artifacts, golden-set pointers |
| Support-agent architecture | [`docs/support-agents/invocation-flow.md`](support-agents/invocation-flow.md) | Request flow, schemas, safeguards, source handling |
| RAG/corpus architecture | [`docs/rag/hc-rag-pipeline.md`](rag/hc-rag-pipeline.md) | Local corpus, DuckDB vector store, chunking, ingestion |
| Grader interface | [`evals/graders/README.md`](../evals/graders/README.md) | Adding or modifying graders and tiers |
| Reports | [`evals/reports/README.md`](../evals/reports/README.md) | Rendering and report-data contracts |

## Common Goals

| I want to... | Read first | Command | Code entry point | Output |
|---|---|---|---|---|
| Run heuristic stats on JSONL | `evals/README.md` | `uv run python -m evals.pipelines.run stats --dir data/datasets/bkh/eval_sets/` | `evals/pipelines/eval_stats.py` | `data/datasets/*/stats/`, `evals/reports/*/` |
| Run LLM quality graders | `evals/README.md` | `uv run python -m evals.pipelines.run quality --dataset <responses.jsonl> --tier calibrated --limit 20` | `evals/pipelines/eval_quality.py` | Quality JSON + HTML report |
| Call a local agent and grade it | `evals/README.md` | `uv run python -m evals.pipelines.run live --run-name smoke --jsonl <dataset.jsonl> --endpoint http://localhost:8011/chat --tier heuristic` | `evals/pipelines/evaluation.py` | `evals/reports/output/<run>.json` |
| Run a LangFuse experiment | `docs/frameworks/langfuse.md` | `uv run python -m evals.pipelines.run langfuse --run-name hc-adk --dataset hc-support-agents-golden-597 --endpoint http://localhost:8011/chat` | `evals/pipelines/langfuse_utils/evaluation.py` | LangFuse experiment scores |
| Re-render a report | `evals/reports/README.md` | `uv run python -m evals.pipelines.run render <report-data.json>` | `evals/reports/renderer.py` | HTML report |
| Start support agents | `src/README.md` | `make sa-up` | `src/support_agents/hc_*/main.py` | Local ports `8011`, `8012`, `8013` |
| Refresh Intercom articles | `core/README.md` | `make articles-fetch` | `core/ingestion/intercom/articles/`, `core/preprocessing/articles/intercom.py` | `data/articles/billy/intercom/help_articles.jsonl` |
| Re-ingest local RAG corpus | `docs/rag/hc-rag-pipeline.md` | `make corpus-ingest` | `src/support_agents/hc_rag/rag/ingestion/` | `data/corpus/datastores/knowledge.duckdb` |
| Add a grader | `evals/graders/README.md` | Add class + registry entry + tests | `evals/graders/` | Registry tier + unit tests |
| Investigate agent parity | `docs/frameworks/agent-feature-parity.md` | No command; compare code and update doc | `src/support_agents/`, `src/multi_agents/` | Updated parity matrix |

## Durable Knowledge Areas

| Directory | Contains | Rule of thumb |
|---|---|---|
| `docs/evals/` | Eval architecture, calibration, methodology | Decisions and invariants, not command catalogs |
| `docs/rag/` | Retrieval architecture, corpus design, KB tradeoffs | RAG decisions and experiment conclusions |
| `docs/support-agents/` | Invocation flow, safeguards, observability | Runtime behavior and response schema context |
| `docs/frameworks/` | LangFuse, LangGraph, ADK, LangSmith, parity | Framework-specific integration notes |
| `docs/stakeholders/` | Notion-ready summaries | Narrative context; use current runbooks for commands |
| `.claude/docs/` | Ticket-scoped research and plans | Promote conclusions to `docs/` once durable |

## Command Surface Policy

- Prefer `uv run python -m evals.pipelines.run ...` for eval workflows.
- Keep the Makefile thin: local services, corpus refresh, tests, and prompt admin.
- Do not add new top-level directories under `evals/`; use `graders/`, `metrics/`, `pipelines/`, or `reports/`.
- Generated report output belongs under `evals/reports/output/` or dataset-specific `data/datasets/*/stats/`.

## Freshness Notes

When updating docs, prefer links to canonical runbooks over copied command blocks.
If a stakeholder or historical doc contains old commands, add a pointer to this
overview or the relevant runbook instead of duplicating the command surface.
