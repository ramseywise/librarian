# Plan: VA Agents Infrastructure

> Status: Draft — 2026-04-21
> Scope: Containers + Terraform for va-google-adk, va-langgraph, Billy MCP, and frontend.
> Ignores: librarian stack entirely.
> Reference: va-agent-systems.md, va-agent-improvements.md, ts_google_adk (production reference on billy-staging/va-agents-service)

---

## 0. Architecture decision: sidecar FastAPI vs MCP

These are orthogonal questions:

| Layer | Decision | Rationale |
|---|---|---|
| **Gateway** | FastAPI sidecar **in-process** with agent runtime | Same pattern as ts_google_adk (Next.js IS the runtime). One image, one process, no network hop for streaming. |
| **Tools** | MCP server as **separate container** | Matches va-agent-improvements.md — MCP stub is permanent dev infra, not a temporary placeholder. Tool signatures stable; backend swappable. |

The "sidecar FastAPI wrapping the agent" = one Docker image contains FastAPI + ADK runner OR FastAPI + LangGraph runner. `VA_BACKEND=adk|langgraph` (or two separate images) selects which. The agent runtime is NOT a microservice — it's a library import inside the gateway process.

MCP is strictly the tool layer (Billy data). The gateway calls `http://billy-mcp:8765/sse` for tools, not for agent orchestration.

---

## 1. Target local dev stack

```
┌─────────────────────────────────────────────────────────────┐
│                    docker-compose (local)                    │
│                                                              │
│  frontend :3000          Next.js (ts_google_adk adapted)     │
│      │ SSE                                                   │
│  va-gateway-adk :8000    FastAPI + ADK runner                │
│  va-gateway-lg  :8001    FastAPI + LangGraph runner          │
│      │ MCP/SSE                                               │
│  billy-mcp :8765         FastMCP + SQLite billy.db           │
│  billy-api :8766         FastAPI REST stub (optional)        │
│  postgres  :5432         LangGraph checkpointer + BillyDB    │
└─────────────────────────────────────────────────────────────┘
```

Frontend env var `VA_BACKEND_URL` selects which gateway to target.
Both gateways share the same Billy MCP server and Postgres instance.

---

## 2. Container layout

```
infrastructure/
  containers/
    va-gateway/
      Dockerfile            # FastAPI + ADK + LangGraph deps; VA_BACKEND selects runtime
      entrypoint.sh         # uvicorn gateway.main:app --host 0.0.0.0 --port 8000
    billy-mcp/
      Dockerfile            # copies adk-agent-pocs/mcp_servers/billy/
    billy-api/
      Dockerfile            # Billy REST stub (adk-agent-pocs/mcp_servers/billy/main.py)
    frontend/
      Dockerfile            # Next.js build (from ts_google_adk or adapted)
    docker-compose.yml      # local dev: all services + postgres
```

### va-gateway/Dockerfile (sketch)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen
COPY va-google-adk/ ./va-google-adk/
COPY va-langgraph/ ./va-langgraph/
COPY infrastructure/containers/va-gateway/entrypoint.sh .
ENV VA_BACKEND=adk
EXPOSE 8000
CMD ["./entrypoint.sh"]
```

`entrypoint.sh` selects `va-google-adk/gateway/main.py` or `va-langgraph/gateway/main.py` based on `$VA_BACKEND`.

Single image, two runtimes — avoids maintaining separate build pipelines for dev. Separate images for production (smaller, no cross-contamination).

---

## 3. Streaming over ALB

SSE over HTTP/1.1 works through ALB with these settings:

```hcl
# ALB idle timeout — must exceed longest expected SSE session
resource "aws_lb" "va" {
  idle_timeout = 300   # 5 min; increase if turns can run longer
}

# Target group — no response buffering, sticky sessions for session affinity
resource "aws_lb_target_group" "va_gateway" {
  deregistration_delay = 30
  stickiness {
    type    = "lb_cookie"
    enabled = true
    duration = 86400
  }
}
```

ALB → ECS Fargate via HTTP/1.1. Fargate task runs uvicorn (supports SSE natively). No NLB needed — HTTP/1.1 keep-alive is sufficient for SSE.

WebSocket (for voice in adk-pocs) requires NLB or `upgrade` header support on ALB — out of scope for now.

---

## 4. Auth middleware

Thin FastAPI middleware on the gateway — not ALB Cognito (adds infra complexity for a POC):

```python
# gateway/auth.py
async def api_key_middleware(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    key = request.headers.get("X-API-Key")
    if key != settings.gateway_api_key:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)
```

`GATEWAY_API_KEY` from Secrets Manager → ECS task env var. Frontend sends it as a header. Rotate via Secrets Manager without redeploying.

Production upgrade path: swap middleware for JWT validation (Cognito or custom JWKS). Shape of the middleware doesn't change.

---

## 5. Terraform: `va_agents` stack

New stack, completely separate from `librarian_api` / `librarian_llm`.

```
infrastructure_as_code/
  va_agents/
    main.tf               # root module — wires everything
    variables.tf
    outputs.tf
    backend.tf            # S3 state, separate prefix from librarian
    environments/
      dev.tfvars
      prod.tfvars
    modules/
      ecs_va/             # ECS cluster + task defs + services (gateway, billy-mcp)
        main.tf
        variables.tf
        outputs.tf
      alb_va/             # ALB + target groups + listeners (reuses vpc from shared)
        main.tf
        variables.tf
        outputs.tf
      rds_va/             # RDS Postgres (LangGraph checkpointer + BillyDB prod)
        main.tf
        variables.tf
        outputs.tf
      secrets_va/         # Secrets Manager: GATEWAY_API_KEY, GEMINI_API_KEY, DB_URL
        main.tf
        variables.tf
        outputs.tf
  _shared/               # existing — cross-stack VPC outputs reused here
```

### What `va_agents` provisions

| Resource | Purpose |
|---|---|
| ECS Fargate cluster | `va-agents` |
| ECS task def: `va-gateway-adk` | FastAPI + ADK runner, 1 vCPU / 2GB |
| ECS task def: `va-gateway-lg` | FastAPI + LangGraph runner, 1 vCPU / 2GB |
| ECS task def: `billy-mcp` | Billy MCP + REST server, 256 CPU / 512MB |
| ECS service per task | desired_count from tfvars (1 dev, 2+ prod) |
| ALB | `va-agents-alb`; path-based routing: `/adk/*` → adk target, `/lg/*` → lg target |
| RDS Postgres (t3.micro dev, t3.small prod) | `va_billy` DB (BillyDB prod) + `va_checkpoints` DB (LangGraph) |
| ECR repos | `va-gateway-adk`, `va-gateway-lg`, `billy-mcp` |
| Secrets Manager | `GATEWAY_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `POSTGRES_URL` |
| CloudWatch log groups | one per ECS service |
| Security groups | ALB → gateway, gateway → billy-mcp, gateway → RDS |

### ALB routing

```
/adk/*  → va-gateway-adk target group :8000
/lg/*   → va-gateway-lg  target group :8001
/       → frontend target group :3000  (if deployed to Fargate)
```

Frontend can also stay as a separate static deploy (Vercel/Amplify) and call the ALB — not blocked.

---

## 6. Build order

### Phase 0 — Containers (no cloud)
- [ ] `infrastructure/containers/va-gateway/Dockerfile` + `entrypoint.sh`
- [ ] `infrastructure/containers/billy-mcp/Dockerfile`
- [ ] `infrastructure/containers/billy-api/Dockerfile`
- [ ] `infrastructure/containers/docker-compose.yml` with postgres, both gateways, both billy servers
- [ ] Smoke test: `docker compose up` → `curl localhost:8000/health` + `curl localhost:8001/health`

### Phase 1 — Auth + streaming hardening
- [ ] `gateway/auth.py` API key middleware (both va-google-adk and va-langgraph)
- [ ] ALB idle_timeout + sticky sessions in Terraform (even before deploying, get right)
- [ ] Verify SSE flushes correctly through uvicorn (add `X-Accel-Buffering: no` response header)

### Phase 2 — Terraform `va_agents` stack
- [ ] `modules/secrets_va` — Secrets Manager entries
- [ ] `modules/ecs_va` — cluster, task defs, services (no RDS yet; use SQLite/in-memory)
- [ ] `modules/alb_va` — ALB with path routing + target groups
- [ ] ECR repos + lifecycle policies
- [ ] `environments/dev.tfvars` — minimal sizing, 1 replica each
- [ ] Deploy to dev: `terraform apply -var-file=environments/dev.tfvars`
- [ ] Smoke test via ALB DNS

### Phase 3 — Postgres (RDS)
- [ ] `modules/rds_va` — t3.micro, `va_billy` + `va_checkpoints` databases
- [ ] Wire `POSTGRES_URL` secret → ECS task env
- [ ] va-langgraph: swap MemorySaver → AsyncPostgresSaver on startup
- [ ] Billy MCP: swap SQLite → Postgres for `BILLY_BACKEND=postgres`
- [ ] Migration script in `billy-mcp/` (`reset_db.py` → supports `--backend postgres`)

### Phase 4 — Frontend
- [x] `infrastructure/containers/frontend/Dockerfile` (web_client adapted for va_assistant)
- [x] `infrastructure/containers/frontend/server.py` (live_audio_patch removed, AGENTS_ROOT_DIR env var, /health, X-Accel-Buffering)
- [x] `infrastructure/containers/frontend/config.json`
- [x] `docker-compose.va.yml` — frontend service added (port 3000, depends on billy-mcp)
- [ ] Add `va-frontend` ECS task def
- [ ] ALB root path `/` → frontend target group

---

## 7. Open questions

| # | Question | Blocks |
|---|---|---|
| 1 | One `va-gateway` image with `VA_BACKEND` env var, or separate `va-gateway-adk` + `va-gateway-lg` images? | Phase 0 Dockerfile design |
| 2 | BillyDB on Postgres in prod, or keep SQLite since it's a stub? | Phase 3 |
| 3 | Frontend stays in ts_google_adk (TS/Next.js) or gets re-wrapped? | Phase 4 |
| 4 | ALB path routing (`/adk`, `/lg`) or hostname routing (`adk.va.internal`, `lg.va.internal`)? | Phase 2 ALB module |
| 5 | Is `_shared/` VPC reused by va_agents, or does va_agents get its own VPC? | Phase 2 — simplest is reuse |
