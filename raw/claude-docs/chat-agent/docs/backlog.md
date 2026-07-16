# Production Readiness Backlog

Gaps identified for making the Agentic RAG chatbot GCP production-ready.
These are **not yet tracked** as Linear issues (unless noted).

---

## 1. ~~Vertex AI Migration (drop API keys)~~ ✅ Done

All `genai.Client()` calls now use Application Default Credentials (ADC). No API keys in production.

---

## 2. API Authentication

**Current state:** `cloudbuild.yaml` deploys with `--allow-unauthenticated`. No auth middleware in FastAPI.

**Required:** Add authentication to the API layer — either Cloud Run IAM (for internal services) or token-based auth (JWT / API key) for external consumers.

**Why it matters:** Banking industry — unauthenticated endpoints are a non-starter.

---

## 3. CORS Lockdown

**Current state:** `api/main.py` has `allow_origins=["*"]`.

**Required:** Restrict to the actual frontend domain(s) in production. Keep `*` only for local dev.

**Why it matters:** Open CORS allows any website to make requests to the API on behalf of a user.

---

## 4. Structured Logging

**Current state:** All logging is `print()` statements across `vector_store.py`, `cli.py`, `agent.py`.

**Required:** Replace with `structlog` or Python `logging` emitting JSON. Cloud Logging auto-parses structured JSON from stdout.

**Why it matters:** Debugging, alerting, audit trail. `print()` gives no severity levels, no correlation IDs, no queryable fields.

---

## 5. Automated Tests

**Current state:** Zero test files. No `pytest` in dependencies.

**Required:**
- Unit tests for tools (`classify_query`, `grade_relevance`, `vector_search`)
- Integration tests for the FastAPI endpoints
- Add `pytest` to dev dependencies in `pyproject.toml`

**Why it matters:** No CI gate — regressions go undetected, refactors are risky.

---

## 6. CI Test Stage

**Current state:** `cloudbuild.yaml` builds the Docker image and deploys. No test or lint step.

**Required:** Add a step before `build` that runs `uv run pytest` and `ruff check`. Fail the build on errors.

**Why it matters:** Broken code can ship to production on every push to `main`.

---

## 7. Staging / Environment Separation

**Current state:** Single Cloud Run service, one set of secrets, no staging vs. prod distinction.

**Required:** At minimum, a staging Cloud Run service with its own Cloud SQL instance and secrets. Ideally driven by branch (`main` → staging, tags → prod).

**Why it matters:** Cannot safely test changes before they hit production.

---

## 8. Health & Readiness Probes for Cloud Run ✅ `AIF-49`

**Current state:** `/api/health` returns `{"status": "ok"}` without checking DB or vector store.

**Required:**
- Liveness probe (`/api/health`): lightweight, confirms process is alive.
- Readiness probe (`/api/ready`): checks PostgreSQL connection, vector store loaded, credentials configured. Returns `503` when not ready.
- Configure Cloud Run probes in `cloudbuild.yaml`.

**Tracked:** [AIF-49](https://linear.app/client-a-co/issue/AIF-49/health-and-readiness-probes-for-cloud-run)

---

## 9. Error Handling & Retries

**Current state:** No retry logic for Gemini API calls in `tools.py`. A single transient failure → `500` to the user.

**Required:** Add retry with exponential backoff for Gemini/embedding API calls. Consider circuit breaker for sustained outages. Return user-friendly error messages instead of raw exceptions.

**Why it matters:** Gemini API has transient errors and rate limits. Without retries, users see failures that would self-resolve.

---

## 10. Database Migrations

**Current state:** Schema is created inline in `vector_store.py` with `CREATE TABLE IF NOT EXISTS`. No migration tool.

**Required:** Introduce Alembic (or similar) for versioned schema migrations. Track migration files in the repo.

**Why it matters:** Schema changes in production (adding columns, indexes) become dangerous without a migration framework. No rollback path today.
