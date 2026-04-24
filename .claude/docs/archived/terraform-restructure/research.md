# Research: Terraform Infrastructure Restructure

**Date**: 2026-04-14
**Status**: Complete
**Confidence**: High

## Context

Restructuring flat `infra/terraform/` layout to match enterprise IaC patterns with module extraction, environment separation, and workload isolation. Must support <2sec response latency for RAG API and future copilot routing agent.

## Current State

Flat layout: 10 `.tf` files at root under `infra/terraform/`. Provisions VPC, ALB, ECS/Fargate, ECR, S3 data lake, Lambda (opt-in), Secrets Manager, security groups. Local backend. Single environment parameterized via variables.

### Resources Provisioned
- **VPC**: `10.0.0.0/16`, 2 public subnets, IGW, no NAT (cost-minimal)
- **ECR**: `librarian-dev-api`, lifecycle policy (keep 10 images)
- **ECS/Fargate**: 512 CPU / 4096 MiB, port 8000, Container Insights, Secrets Manager injection
- **ALB**: public-facing, HTTP/HTTPS listeners, health check on `/health`
- **S3**: `librarian-dev-data-lake`, versioned, encrypted, event notification to Lambda on `raw/`
- **Lambda** (opt-in): API Lambda (Mangum) + ingestion Lambda (S3 trigger), both from same ECR image
- **Secrets Manager**: `ANTHROPIC_API_KEY`
- **Security Groups**: ALB (80/443 inbound) + ECS (container_port from ALB only)

## Key Findings

### 1. Latency Budget Requires Fargate

| Pipeline Step | Warm Latency | Lambda Cold Start |
|---|---|---|
| E5-large embedding (560M) | ~100-200ms | +3-8s model load |
| Cross-encoder reranking | ~100-300ms | +1-2s model load |
| Claude/Bedrock generation | 500ms-2s | — |
| **Total** | **~700ms-2.5s** | **+4-10s cold** |

Lambda cold starts with container images (embedding model baked in) make <2sec impossible without provisioned concurrency, which economically converges with Fargate. **Keep Fargate for serving.**

### 2. Runtime Stack Decision

- **LangGraph**: Stays as RAG orchestration (CRAG loop, hybrid scoring, conditional edges, state machine). Too much custom logic for Agent Core.
- **ADK**: Stays as tool interface layer (Bedrock KB, search, rerank tools). Clean abstraction boundary.
- **Bedrock Agent Core**: Skip for RAG. Consider for future copilot routing layer — the ADK tool abstractions provide a clean migration seam.

### 3. Two-Stack Terraform Architecture

Maps to enterprise pattern:

| Stack | Purpose | Resources |
|---|---|---|
| `librarian_api` ("model hosting") | RAG API serving | ECR, ECS/Fargate, ALB, VPC, security groups, CloudWatch, Secrets |
| `librarian_llm` ("LLM lambda") | Bedrock/generation + data | IAM (Bedrock), Lambda (ingestion), S3 data lake |

Separate state files enable independent deployment and different change velocity.

### 4. CI/CD Pipeline: Team Pattern vs This Project

Reference pipeline: `va-agents-service` (Node 22 + Pixi Python, awsonnet Jsonnet task defs, `ageras-com/github-actions` shared workflows). This project adapts the same structure for a pure Python 3.12 + uv stack.

#### Toolchain Comparison

| Concern | Team pattern (va-agents) | This project (librarian) | Trade-off |
|---|---|---|---|
| **Runtime** | Node 22 (Next.js frontend) | Python 3.12 (FastAPI) | Different ecosystems, same CI structure |
| **Package mgr** | `npm ci` + `pixi install` | `uv sync --frozen` | uv replaces both — single lockfile, faster installs, deterministic |
| **Lint** | `npm run lint` (ESLint) | `ruff check` + `ruff format --check` | ruff is 10-100x faster than flake8/black; single tool for lint+format |
| **Test** | `pixi run -e test pytest` | `uv run pytest` | pixi adds conda ecosystem; uv is lighter if PyPI-only deps suffice |
| **Task def** | Jsonnet (awsonnet/shinesonnet) | Terraform modules | See IaC comparison below |
| **Docker** | `ageras-com/github-actions` shared action | Standalone `docker build` + `aws ecr` | Can swap to shared action later — same inputs |
| **Deploy** | `awsonnet-ecs-deploy.yml@v11` reusable workflow | Standalone `terraform apply -target=module.ecs` | See IaC comparison below |

#### IaC Approach: Terraform Modules vs Jsonnet (awsonnet)

| Dimension | Terraform modules | Jsonnet (awsonnet) |
|---|---|---|
| **What it manages** | Full infra lifecycle (VPC, ALB, ECS, S3, IAM, Secrets) | ECS task definition only (container spec, env vars, secrets, health check) |
| **State** | Explicit state file (S3 + DynamoDB) — drift detection, plan/apply cycle | Stateless — generates JSON task def, ECS service handles the rest |
| **Scope** | Provisions + deploys | Deploy only — assumes infra exists |
| **Environment config** | `.tfvars` per environment | Jsonnet local variables per environment |
| **Shared patterns** | Module registry (or stack-local modules) | `shinesonnet` library (company standard) |
| **Learning curve** | HCL, state management, import/moved blocks | Jsonnet, library conventions |
| **Team compatibility** | Standard in industry; standalone | Requires `ageras-com/github-actions` shared workflows |

**Decision**: Use Terraform for infra provisioning (this project needs full lifecycle management — VPC, ALB, S3, etc.). The Jsonnet pattern only covers task definitions and assumes infra already exists via another mechanism. If integrating with the team's shared deploy workflows later, add a Jsonnet task def alongside Terraform — they're complementary, not competing.

#### CI Pipeline Structure (adapted)

```
PR:  lint (ruff) → test (pytest) → terraform plan (both stacks, posted as PR comment)
Main: lint → test → docker build/push (ECR) → deploy staging → deploy production
Manual: workflow_dispatch → choose environment → deploy
```

Matches the team's pattern: `lint → test → validate → build → deploy (auto on main, manual via dispatch)`. Key differences:
- No `validate_task_definition` step (using Terraform, not Jsonnet)
- Terraform plan on PR replaces task def validation
- Sequential staging → production (not parallel matrix) for safer rollout
- Standalone AWS actions instead of `ageras-com/github-actions` (swap when ready)

#### Deployment Integration Considerations

1. **Shared workflow migration**: Current standalone workflows use the same interface (`environment` + `image-uri` inputs). Swapping to `ageras-com/github-actions` later requires: (a) adding awsonnet task def Jsonnet, (b) replacing deploy step with `awsonnet-ecs-deploy.yml@v11`, (c) configuring `AWSONNET_KEY` secret.

2. **Region difference**: Team uses `eu-north-1` (Stockholm), this project defaults to `eu-west-1` (Ireland). Align region before integrating with shared infra.

3. **Cluster naming**: Team uses `billy-{environment}`, this project uses `librarian-{environment}`. Shared workflows need the `cluster-name` input — not hardcoded.

4. **Health check path**: Team uses `/va-agents/api/health`, this project uses `/health`. Task def health check and ALB target group must agree.

5. **Secrets pattern**: Team uses AWS Secrets Manager paths (`/sensitive/virtual-assistant/*`). This project uses single secret (`anthropic_api_key`). Align naming convention before prod.

### 5. Agent Core for Copilot (Future)

For the outer routing/copilot layer, Agent Core trade-offs vs LangGraph:
- **Gains**: managed session/memory, native multi-agent, no infra to manage
- **Losses**: opaque state (less introspection), less latency control, CloudWatch-only tracing (vs Langfuse/OTel)
- **Migration path**: ADK tool interfaces already provide the abstraction seam. Routing logic is simple enough that either runtime works.

Design the copilot routing interface cleanly so runtime can swap without touching RAG internals.

## Recommendations

1. **Keep Fargate** for RAG API serving (<2sec requirement)
2. **Keep Lambda** for async ingestion only
3. **LangGraph + ADK** for orchestration/tools; defer Agent Core to copilot phase
4. **Two Terraform stacks** with module extraction and environment separation
5. **S3 remote backend** before adding staging/prod
6. **GitHub Actions** for CI/CD pipeline
