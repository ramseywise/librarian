---
title: Cloud Run + Cloud SQL Pattern
tags: [infra, pattern]
summary: Single-container Cloud Run service (FastAPI + SPA) connected to Cloud SQL via the built-in Auth Proxy unix socket — no public IP, no SSL config, private GCP-internal networking by default.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/architecture/cloud_deployment.md
  - raw/claude-docs/chat-agent/docs/TODO_production.md
---

# Cloud Run + Cloud SQL Pattern

A repeatable GCP deployment pattern for Python agentic API services that need a persistent vector or relational database.

---

## Architecture

```
Browser
  └─→ Cloud Run (single container)
        ├─→ /api/*    → FastAPI (Python package)
        ├─→ /assets/* → React static files (baked into image)
        └─→ /*        → index.html (SPA catch-all)
              │
              └─→ Cloud SQL (PostgreSQL 15 + pgvector)
                    └─ documents table (vector(3072) embeddings)
```

The Docker image bakes the frontend `dist/` directory into the container at build time. FastAPI's `StaticFiles` mount serves `/assets/*` and the SPA catch-all route returns `index.html` for all other paths. This avoids CORS and removes the need for a CDN or separate frontend hosting.

---

## Cloud SQL Auth Proxy

Cloud Run has native Cloud SQL support via `--add-cloudsql-instances`. The proxy runs as a **sidecar automatically** — no separate process to manage.

The database connection string uses a **unix socket path**:

```
postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE
```

This means:
- No public IP on the Cloud SQL instance
- No SSL certificate configuration
- No firewall rules needed
- Everything stays inside GCP's private network

For local development or KB index updates, run the proxy locally:

```bash
cloud-sql-proxy PROJECT_ID:REGION:INSTANCE &
DATABASE_URL="postgresql://user:pass@127.0.0.1:5432/dbname" \
  uv run python scripts/rebuild_index.py
```

No image rebuild needed for KB updates — the DB change is live on the running Cloud Run instance immediately.

---

## Worker Count

```bash
uvicorn api.main:app --workers 1
```

**Why `--workers 1`:** Session dicts and database connections are process-level globals. Multiple workers create independent session state per worker, breaking conversation continuity. A single async worker handles concurrency via the event loop.

---

## Cloud Run Sizing Rationale

| Parameter | Value | Reason |
|---|---|---|
| Memory | 1Gi | Python ML deps (ADK, psycopg) + concurrent response buffers |
| CPU | 2 | Prevents event loop throttling during concurrent LLM API calls |
| Min instances | 1 | Cold start is 10–20s (ADK init + DB connect) — keep 1 warm |
| Max instances | 3 | Caps LLM API spend; 3 × 10 = 30 concurrent users max |
| Concurrency | 10 | FastAPI is fully async; safe ceiling given in-memory state |
| Timeout | 300s | Full agentic loop (with CRAG retry) can take 60–120s |

---

## GCP Services Used

| Service | Purpose |
|---|---|
| Cloud Run | Container runtime; serverless, scales to zero |
| Cloud SQL (PostgreSQL 15) | pgvector embeddings + conversation history |
| Artifact Registry | Docker image storage |
| Secret Manager | API keys, DATABASE_URL |
| Cloud Build | CI/CD — build + deploy on push to `main` |

---

## Secret Injection

Secrets are stored in Secret Manager and injected at deploy time:

```bash
gcloud run deploy my-service \
  --add-cloudsql-instances=PROJECT:REGION:INSTANCE \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest,DATABASE_URL=DATABASE_URL:latest
```

The `DATABASE_URL` secret uses the unix socket format so the value works identically in local proxy mode and in Cloud Run.

---

## CI/CD Flow

Cloud Build trigger on `main` branch:

1. Build Docker image (Stage 1: compile React frontend; Stage 2: Python layer)
2. Push to Artifact Registry
3. Rolling deploy to Cloud Run with `--add-cloudsql-instances`

---

## Production Hardening Checklist

- [ ] `pydantic-settings` in config — fails loudly on missing env vars at startup
- [ ] Replace `print()` with `structlog` JSON logging (Cloud Logging parses it automatically)
- [ ] Connection pooling (`psycopg_pool`) — single persistent connection does not handle concurrency
- [ ] Auth + rate limiting on FastAPI endpoints (`--allow-unauthenticated` is only for dev)
- [ ] CORS lockdown — restrict `allow_origins` from `["*"]` to actual frontend domain
- [ ] Liveness + readiness probes — `/api/health` (process alive) and `/api/ready` (DB connected, model loaded)
- [ ] Retry + exponential backoff for LLM API calls
- [ ] Staging environment with separate Cloud SQL instance

---

## See Also
- [[Production Hardening Patterns]]
- [[PGVector Migration Pattern]]
- [[Langfuse ADK Tracing Patterns]]
- [[ADK Deployment Patterns]]
