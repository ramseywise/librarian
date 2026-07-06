# Production Deployment TODO — Jonas

## Status

- [x] Project restructured into `src/agentic_rag/` package
- [x] pgvector integrated (394 embeddings in local PostgreSQL)
- [x] Docker + Cloud Build config written
- [ ] GCP infrastructure provisioned
- [ ] Embeddings migrated to Cloud SQL
- [ ] CI/CD live

---

## Architecture

```
Browser
  └─→ Cloud Run (single container)
        ├─→ /api/*   → FastAPI (agentic_rag)
        ├─→ /assets/* → React static files
        └─→ /*        → index.html (SPA catch-all)
              │
              └─→ Cloud SQL (PostgreSQL 15 + pgvector)
                    └─ documents table (394 rows, 3072-dim embeddings)
```

**Why Cloud SQL and not Neon/Supabase:** Cloud Run → Cloud SQL uses a unix socket via the built-in Auth Proxy — no public IP, no SSL config, no extra firewall rules. Everything stays inside GCP.

---

## Step 1 — Enable GCP APIs

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

---

## Step 2 — Provision Cloud SQL (PostgreSQL + pgvector)

```bash
# Create instance (db-g1-small is enough for this workload)
gcloud sql instances create agentic-rag-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=$REGION \
  --no-assign-ip          # private IP only, no public access

# Create database and user
gcloud sql databases create agentic_rag --instance=agentic-rag-db

gcloud sql users create appuser \
  --instance=agentic-rag-db \
  --password=CHOOSE_A_STRONG_PASSWORD

# Enable pgvector extension (run once after instance is ready)
gcloud sql connect agentic-rag-db --user=postgres
# Inside psql:
# \c agentic_rag
# CREATE EXTENSION IF NOT EXISTS vector;
# \q
```

Note the **connection name** — you'll need it for Cloud Run:
```bash
gcloud sql instances describe agentic-rag-db --format='value(connectionName)'
# → PROJECT_ID:us-central1:agentic-rag-db
```

---

## Step 3 — Migrate Embeddings to Cloud SQL (no token cost)

The 394 document embeddings already exist in local PostgreSQL. Dump and restore — no re-embedding needed.

### 3a — Export from local

```bash
pg_dump -h localhost -U postgres -d agentic_rag \
  --table=documents \
  -F c -f documents_export.dump
```

### 3b — Restore via Cloud SQL Auth Proxy

```bash
# Start the proxy locally
cloud-sql-proxy PROJECT_ID:us-central1:agentic-rag-db &

# Restore into Cloud SQL
pg_restore -h 127.0.0.1 -p 5432 \
  -U appuser -d agentic_rag \
  --table=documents documents_export.dump

# Verify
psql -h 127.0.0.1 -U appuser -d agentic_rag \
  -c "SELECT COUNT(*) FROM documents;"
# → 394
```

---

## Step 4 — Store Secrets in Secret Manager

```bash
# API keys
echo -n "YOUR_GEMINI_KEY"   | gcloud secrets create GEMINI_API_KEY   --data-file=-
echo -n "YOUR_INTERCOM_KEY" | gcloud secrets create INTERCOM_API_KEY --data-file=-

# DATABASE_URL using Cloud SQL unix socket format (used by Cloud Run at runtime)
echo -n "postgresql://appuser:PASSWORD@/agentic_rag?host=/cloudsql/PROJECT_ID:us-central1:agentic-rag-db" \
  | gcloud secrets create DATABASE_URL --data-file=-
```

---

## Step 5 — IAM Permissions

```bash
# Cloud Run service account needs: secrets + Cloud SQL client
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET in GEMINI_API_KEY INTERCOM_API_KEY DATABASE_URL; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$SA" \
    --role="roles/secretmanager.secretAccessor"
done

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/cloudsql.client"

# Cloud Build service account needs: deploy to Cloud Run + push to Artifact Registry
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
for ROLE in roles/run.admin roles/iam.serviceAccountUser roles/artifactregistry.writer; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CB_SA" \
    --role=$ROLE
done
```

---

## Step 6 — Artifact Registry

```bash
gcloud artifacts repositories create agentic-rag \
  --repository-format=docker \
  --location=$REGION
```

---

## Step 7 — Update cloudbuild.yaml

Set the Cloud SQL instance name in the substitution:

```yaml
# In cloudbuild.yaml, set:
_CLOUDSQL_INSTANCE: "PROJECT_ID:us-central1:agentic-rag-db"

# And uncomment this line in the deploy step:
- --add-cloudsql-instances=${_CLOUDSQL_INSTANCE}
```

---

## Step 8 — First Deploy (manual)

```bash
gcloud auth configure-docker ${REGION}-docker.pkg.dev

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/agentic-rag/agentic-rag:v1"
docker build -t $IMAGE .
docker push $IMAGE

gcloud run deploy agentic-rag \
  --image=$IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=2 \
  --min-instances=1 \
  --max-instances=3 \
  --concurrency=10 \
  --timeout=300 \
  --port=8080 \
  --add-cloudsql-instances=PROJECT_ID:us-central1:agentic-rag-db \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest,INTERCOM_API_KEY=INTERCOM_API_KEY:latest,DATABASE_URL=DATABASE_URL:latest

# Verify
gcloud run services describe agentic-rag --region=$REGION --format='value(status.url)'
# → curl https://YOUR_URL/api/health  →  {"status":"ok"}
```

---

## Step 9 — Wire CI/CD (Cloud Build trigger)

```bash
gcloud builds triggers create github \
  --name="deploy-on-push-main" \
  --repo-name="Agentic-RAG" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"
```

After this, every push to `main` → Cloud Build → new image → rolling Cloud Run deploy.

---

## Knowledge Base Update Workflow

When Intercom articles change, re-index against Cloud SQL directly:

```bash
# 1. Start Cloud SQL Auth Proxy pointing at prod
cloud-sql-proxy PROJECT_ID:us-central1:agentic-rag-db &

# 2. Set DATABASE_URL to point at proxy
export DATABASE_URL="postgresql://appuser:PASSWORD@127.0.0.1:5432/agentic_rag"

# 3. Fetch latest articles from Intercom and re-embed into Cloud SQL
uv run python scripts/intercom_loader.py --rebuild

# No image rebuild needed — the DB update is live immediately.
```

---

## Cloud Run Sizing Rationale

| Parameter | Value | Reason |
|---|---|---|
| Memory | 1Gi | google-adk + psycopg + concurrent response buffers |
| CPU | 2 | Prevents event loop throttling during concurrent Gemini API calls |
| Min instances | 1 | Cold start is 10-20s (ADK init + DB connect) — keep 1 warm |
| Max instances | 3 | Caps Gemini API spend; 3×10 = 30 concurrent users max |
| Concurrency | 10 | FastAPI is fully async; safe ceiling given in-memory trace buffers |
| Timeout | 300s | Full agentic loop can take 60-120s under correction |

---

## Production Hardening (before go-live)

- [ ] `pydantic-settings` in `config.py` — fails loudly on missing env vars at startup
- [ ] Replace `print()` with `logging` / `structlog`
- [ ] `psycopg_pool` in `vector_store.py` — current code holds a single persistent connection
- [ ] Auth + rate limiting on FastAPI endpoints
