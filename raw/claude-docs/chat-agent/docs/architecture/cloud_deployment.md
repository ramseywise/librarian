# GCP Deployment — Agentic RAG

## Architecture

```
Browser
  └─→ Cloud Run (single container — FastAPI + React)
        ├─→ /api/*    → FastAPI (agentic_rag package)
        ├─→ /assets/* → React static files (baked into image)
        └─→ /*         → index.html (SPA catch-all)
              │
              └─→ Cloud SQL for PostgreSQL 15
                    └─ documents table
                         ├─ text (article chunks)
                         ├─ metadata (JSONB)
                         └─ embedding (vector(3072) — pgvector)
```

Cloud Run connects to Cloud SQL via the **built-in Auth Proxy** (unix socket). No public IP, no SSL configuration, no firewall rules needed.

---

## GCP Services

| Service | Purpose |
|---|---|
| **Cloud Run** | Runs the container; serverless, scales to zero |
| **Cloud SQL (PostgreSQL 15)** | pgvector embeddings — 394 documents, 3072-dim |
| **Artifact Registry** | Docker image storage |
| **Secret Manager** | `INTERCOM_API_KEY`, `DATABASE_URL` |
| **GitHub Actions** | CI/CD — builds and deploys on every push to `main` |

---

## Image Contents

The Docker image (see `Dockerfile`) contains:

```
/app
├── src/agentic_rag/     ← Python package
├── api/main.py          ← FastAPI app
├── AGENTS.md            ← Google ADK config (required at root)
└── frontend/dist/       ← Built React app (baked in during Stage 1)
```

**Not in the image:** `data/`, `scripts/`, embeddings. Embeddings live in Cloud SQL.

---

## Key Design Decisions

**Single Cloud Run service** — FastAPI serves both the API and the React SPA. The `StaticFiles` mount in `api/main.py` serves `/assets/*` and the catch-all route returns `index.html` for all other paths. This avoids CORS and removes the need for a CDN or separate frontend hosting.

**Cloud SQL Auth Proxy** — Cloud Run has native Cloud SQL support via `--add-cloudsql-instances`. The proxy runs as a sidecar automatically. `DATABASE_URL` uses a unix socket path:
```
postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE
```

**`--workers 1`** — The session dict (`_agents`) and pgvector connection are process-level globals. Multiple workers would create independent session state per worker, breaking conversation continuity.

**`--min-instances 1`** — Cold start (ADK init + Cloud SQL connection) is 10-20s. One warm instance prevents the first user from waiting.

---

## Knowledge Base Update

Intercom articles change → run locally with Cloud SQL Auth Proxy:

```bash
cloud-sql-proxy PROJECT_ID:REGION:INSTANCE &
DATABASE_URL="postgresql://user:pass@127.0.0.1:5432/agentic_rag" \
  uv run python scripts/intercom_loader.py --rebuild
```

No image rebuild needed. The DB update is live immediately on the running Cloud Run instance.

---

## Full setup steps → see `docs/TODO_production.md`
