---
title: ADK Deployment Patterns
tags: [adk, infra, pattern]
summary: ADK deployment targets (Agent Engine vs Cloud Run vs GKE), CI/CD with WIF, service account architecture, event-driven triggers, and Terraform patterns.
updated: 2026-07-14
sources:
  - raw/claude-docs/project-g/.agents/skills/adk-deploy-guide/SKILL.md
  - raw/claude-docs/project-g/.agents/skills/adk-deploy-guide/references/agent-engine.md
  - raw/claude-docs/project-g/.agents/skills/adk-deploy-guide/references/cloud-run.md
  - raw/claude-docs/project-g/.agents/skills/adk-deploy-guide/references/event-driven.md
  - raw/claude-docs/project-g/.agents/skills/adk-deploy-guide/references/terraform-patterns.md
  - raw/agent-skills/adk-deploy-guide/SKILL.md
  - raw/agent-skills/adk-deploy-guide/references/agent-engine.md
  - raw/agent-skills/adk-deploy-guide/references/cloud-run.md
  - raw/agent-skills/adk-deploy-guide/references/event-driven.md
  - raw/agent-skills/adk-deploy-guide/references/terraform-patterns.md
---

# ADK Deployment Patterns

Covers the three deployment targets (Agent Engine, Cloud Run, GKE), CI/CD pipeline structure, Workload Identity Federation, service account architecture, event-driven invocations, and Terraform infrastructure patterns.

For observability configuration, see [[ADK Observability]]. For project scaffolding, see [[ADK Scaffold Patterns]].

---

## Deployment Target Decision Matrix

| Criteria | Agent Engine | Cloud Run | GKE |
|---|---|---|---|
| **Languages** | Python only | Python (custom containers) | Any language |
| **Scaling** | Managed auto-scaling | Fully configurable | Full Kubernetes (HPA, VPA) |
| **Networking** | VPC-SC + PSC | Full VPC, direct VPC egress, IAP | Full Kubernetes networking |
| **Session state** | Native `VertexAiSessionService` | In-memory, Cloud SQL, or Agent Engine | Any Kubernetes-compatible store |
| **Batch/event** | Not supported | `/invoke` endpoint for Pub/Sub, Eventarc, BQ | Custom (Jobs, Pub/Sub) |
| **Cost model** | vCPU-hours + memory-hours (not billed idle) | Per-instance-second + min instance costs | Node pool costs (always-on) |
| **Setup** | Lower (managed) | Medium (Dockerfile + Terraform) | Higher (Kubernetes expertise) |
| **Best for** | Minimal ops, managed infra | Custom infra, event-driven | Full control, GPU, open models |

---

## Quick Deploy (No Scaffold)

```bash
adk deploy cloud_run --project=PROJECT --region=REGION path/to/agent/
adk deploy agent_engine --project=PROJECT --region=REGION path/to/agent/
adk deploy gke --project=PROJECT --cluster_name=CLUSTER --region=REGION path/to/agent/
```

All commands support `--with_ui`. Cloud Run also accepts extra `gcloud` flags after `--`.

---

## Agent Engine

**Source-based deployment** — no Docker container. Code is packaged as a base64-encoded tarball.

```python
# Your agent extends AdkApp from vertexai.agent_engines.templates.adk
# Key methods: set_up(), register_operations(), async_stream_query()

import vertexai
with open("deployment_metadata.json") as f:
    engine_id = json.load(f)["remote_agent_engine_id"]

client = vertexai.Client(location="us-central1")
agent = client.agent_engines.get(name=engine_id)

async for event in agent.async_stream_query(message="Hello!", user_id="test"):
    print(event)
```

**No `gcloud` CLI.** Deploy via `deploy.py` or `adk deploy agent_engine`.

**Deployment flow:**
1. `uv export` → `.requirements.txt` from lockfile
2. `deploy.py` packages source, creates/updates the Agent Engine instance
3. Writes `deployment_metadata.json` with engine resource ID

**deployment_metadata.json:**
```json
{
  "remote_agent_engine_id": "projects/P/locations/L/reasoningEngines/ID",
  "deployment_target": "agent_engine",
  "is_a2a": false,
  "deployment_timestamp": "2025-02-25T10:30:00.000Z"
}
```

If `make deploy` times out but the engine was created, manually populate this file with the engine resource ID.

**Session services:** `InMemorySessionService` (default, stateless) or `VertexAiSessionService` (persistent managed). Artifacts: `GcsArtifactService` via `LOGS_BUCKET_NAME` env var.

**Terraform resource:** `google_vertex_ai_reasoning_engine` in `deployment/terraform/service.tf`. Critical: `lifecycle.ignore_changes` on `source_code_spec` — source code is updated by CI/CD, not Terraform.

**AdkApp key methods (full set):** `set_up()`, `register_operations()`, `register_feedback()` (collect and log user feedback), `async_stream_query()`.

**Playground & remote testing:** `expose_app.py` bridges a local WebSocket frontend to a deployed Agent Engine instance for ADK Live/streaming projects — `make playground` runs against the local agent instance, `make playground-remote` reads `deployment_metadata.json` for the engine ID and connects via `client.aio.live.agent_engines.connect()` with bidirectional streaming.

**CI/CD differences vs Cloud Run:**

| Aspect | Agent Engine | Cloud Run |
|---|---|---|
| Build | `uv export` → requirements file | Docker build → container image |
| Deploy command | `uv run -m app.app_utils.deploy` | `gcloud run deploy --image ...` |
| Artifact | Base64 source tarball | Container image in Artifact Registry |
| Python version | Fixed at 3.12 (Terraform) | Configurable in Dockerfile |
| Load testing | Via `expose_app.py --mode remote` bridge | Direct HTTP to Cloud Run URL |

---

## Cloud Run

**Container-based deployment.** Uses Dockerfile with `uv` for dependency management.

**Session types:**

| Type | Configuration | Use Case |
|---|---|---|
| In-memory | Default | Local dev only |
| Cloud SQL | `--session-type cloud_sql` | Production persistent sessions |
| Agent Engine | `session_service_uri = agentengine://...` | Agent Engine as session backend |

**Key Terraform settings:** `cpu_idle`, `min_instance_count` (cold start avoidance), `max_instance_request_concurrency`, `session_affinity`.

**Ingress:** default is `INGRESS_TRAFFIC_ALL` (public). Restrict to `INGRESS_TRAFFIC_INTERNAL_ONLY` or `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` in `service.tf`.

**IAP:** `make deploy IAP=true` adds Identity-Aware Proxy for Google identity authentication.

**VPC connectors are not configured by default** — add them in custom Terraform if the agent needs private resource access.

**Testing a deployed Cloud Run service:**
```bash
SERVICE_URL="https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app"
AUTH="Authorization: Bearer $(gcloud auth print-identity-token)"

# Create session first
curl -X POST "$SERVICE_URL/apps/app/users/test-user/sessions" \
  -H "Content-Type: application/json" -H "$AUTH" -d '{}'

# Then send message
curl -X POST "$SERVICE_URL/run_sse" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"app_name": "app", "user_id": "test-user", "session_id": "ID",
       "new_message": {"role": "user", "parts": [{"text": "Hello!"}]}}'
```

**Common mistake:** `{"message": "Hello!"}` returns `422 Field required`. Use the `new_message`/`parts` schema above.

---

## CI/CD Pipeline (GitHub Actions)

**Three stages:**

1. **CI (PR checks)** — unit + integration tests on pull request
2. **Staging CD** — triggered on merge to `main` under `app/**`. Builds container, deploys to staging, runs load tests
3. **Production CD** — triggered after successful staging deploy. Requires manual approval via GitHub Actions environment protection rules

**Setup:**
```bash
uvx agent-starter-pack setup-cicd \
  --staging-project YOUR_STAGING_PROJECT \
  --prod-project YOUR_PROD_PROJECT \
  --repository-name YOUR_REPO_NAME \
  --repository-owner YOUR_GITHUB_USERNAME \
  --auto-approve \
  --create-repository
```

**Important:** `setup-cicd` creates infrastructure but doesn't deploy automatically. Push code to trigger:
```bash
git add . && git commit -m "Initial agent implementation"
git push origin main
```

**Path filter caveat:** Staging CD uses `paths: ['app/**']`. First push after `setup-cicd` won't trigger staging CD unless files under `app/` changed.

---

## Workload Identity Federation (WIF)

Both GitHub Actions and Cloud Build use WIF — no long-lived service account keys needed.

GitHub/Cloud Build OIDC tokens are trusted by a GCP Workload Identity Pool, which grants `cicd_runner_sa` impersonation. Terraform in `setup-cicd` creates the pool, provider, and SA bindings automatically.

If auth fails, re-run `terraform apply` in the CI/CD Terraform directory.

---

## Service Account Architecture

| SA | Role |
|---|---|
| `app_sa` (per environment) | Runtime identity for the deployed agent |
| `cicd_runner_sa` (CI/CD project) | CI/CD pipeline identity; needs permissions in staging AND prod |

**Common 403 errors:**
- "Permission denied on Cloud Run" → `cicd_runner_sa` missing deployment role in target project
- "Cannot act as service account" → Missing `iam.serviceAccountUser` on `app_sa`
- "Secret access denied" → `app_sa` missing `secretmanager.secretAccessor`
- "Artifact Registry read denied" → Cloud Run service agent missing read access in CI/CD project

---

## Secret Manager

```bash
echo -n "YOUR_API_KEY" | gcloud secrets create MY_SECRET_NAME --data-file=-
echo -n "NEW_VALUE" | gcloud secrets versions add MY_SECRET_NAME --data-file=-
```

**Grant access:** Cloud Run → grant `secretmanager.secretAccessor` to `app_sa`. Agent Engine → grant to `service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`.

**Pass at deploy time (Agent Engine):**
```bash
make deploy SECRETS="API_KEY=my-api-key,DB_PASS=db-password:2"
```

---

## Event-Driven Invocations (Cloud Run)

Add custom endpoints to `fast_api_app.py`. The general pattern: decode trigger payload → run agent with ephemeral session → return correct response format.

**Setup (shared across all endpoints):**
```python
_trigger_session_service = InMemorySessionService()
_trigger_runner = Runner(agent=root_agent, app_name=APP_NAME,
                          session_service=_trigger_session_service)
app = get_fast_api_app(agents_dir=..., session_service_uri=...)

async def _run_agent(message_text: str, user_id: str = "trigger") -> list:
    session = await _trigger_session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=str(uuid.uuid4())
    )
    events = []
    async for event in _trigger_runner.run_async(
        user_id=user_id, session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message_text)]),
    ):
        events.append(event)
    return events
```

**Pub/Sub push:** decode base64 data, return 200 to ack, non-200 to retry.

**Eventarc:** binary mode uses `ce-*` headers + Pub/Sub body; structured mode has a `data` key.

**BigQuery Remote Function:** BQ sends `{"calls": [["row1"], ...]}`, expects `{"replies": [...]}` in same order. Register at `POST /` (BQ cannot use URL paths). Terraform: `google_bigquery_routine` with `routine_type = "SCALAR_FUNCTION"`, `remote_function_options.endpoint` pointing at the Cloud Run service root URL and `connection` referencing a `google_bigquery_connection`.

**Production hardening:** Add `asyncio.Semaphore` to cap concurrent invocations; retry with exponential backoff on 429/RESOURCE_EXHAUSTED.

**Pub/Sub push subscription Terraform:** `google_pubsub_subscription` with `push_config.push_endpoint` set to the `/trigger/pubsub` route and `push_config.oidc_token` (service account + audience = the Cloud Run URL) for push auth. Requires a `google_service_account_iam_member` granting `roles/iam.serviceAccountTokenCreator` to the Pub/Sub service agent (`service-{PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com`) on `app_sa` so Pub/Sub can mint the OIDC tokens.

---

## Terraform Patterns

**Critical rule:** all production infrastructure must be in Terraform — never create resources manually via `gcloud` in production.

**Where to put custom Terraform:**
- Dev-only: `deployment/terraform/dev/custom_resources.tf`
- CI/CD environments (staging/prod): `deployment/terraform/custom_resources.tf`

**Common resource patterns:**
- Cloud Storage + Eventarc trigger → point to `/invoke` endpoint, grant `eventarc.eventReceiver` to `app_sa`
- Pub/Sub topic + push subscription → point to `/invoke`, grant `iam.serviceAccountTokenCreator` for push auth
- BigQuery Remote Function → create BQ connection + grant Cloud Run invoke permission

**Terraform state:**
- Default (remote): `{cicd_project}-terraform-state` GCS bucket, prefix `{repository_name}/{env}`
- Local: use `--local-state` flag with `setup-cicd` (single-developer only)

**Importing existing resources:**
```bash
terraform import google_cloud_run_v2_service.app \
  projects/PROJECT_ID/locations/REGION/services/SERVICE_NAME

terraform import google_service_account.app_sa \
  projects/PROJECT_ID/serviceAccounts/SA_EMAIL

terraform import google_secret_manager_secret.my_secret \
  projects/PROJECT_ID/secrets/SECRET_NAME
```
After importing, run `terraform plan` to verify the imported state matches configuration before applying.

---

## Rollback

**Primary method:** git-based. Fix, commit, push to `main` — CI/CD deploys through staging → production.

**Cloud Run immediate rollback** (no new commit):
```bash
gcloud run revisions list --service=SERVICE_NAME --region=REGION
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION_NAME=100 --region=REGION
```

**Agent Engine:** no revision-based rollback — fix and redeploy.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Terraform state locked | `terraform force-unlock -force LOCK_ID` |
| GitHub Actions auth failed | Re-run `terraform apply` in CI/CD terraform dir |
| Agent Engine deploy timeout | Check if engine was created; manually populate `deployment_metadata.json` |
| 403 on deploy | Check `iam.tf` — `cicd_runner_sa` needs deployment + SA impersonation roles |
| 403 when testing Cloud Run | Default is `--no-allow-unauthenticated`; include Bearer token |
| Cold starts slow | Set `min_instance_count > 0` in Cloud Run Terraform config |
| 403 right after granting IAM role | IAM propagation is not instant — wait a couple minutes |
| Resource seems missing | Run `terraform state list` — BQ linked datasets via `null_resource` won't appear in `gcloud` |

---

## See Also

- [[System Design — Serverless Agent Backends]] — instance-of
- [[ADK Scaffold Patterns]]
- [[ADK Observability]]
- [[ADK Python API Reference]]
- [[Production Hardening Patterns]]
- [[Observability and Runtime Patterns]]
