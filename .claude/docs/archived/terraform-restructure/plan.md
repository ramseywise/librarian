# Plan — Terraform Infrastructure Restructure

> Restructure flat `infra/terraform/` into enterprise-grade modular layout with two
> isolated stacks (API serving + LLM/data), environment separation, and CI/CD pipeline.
> Informed by research at `.claude/docs/in-progress/terraform-restructure/research.md`.
>
> Date: 2026-04-14
> Status: Draft — awaiting review

---

## Target Structure

```
infrastructure/
├── containers/
│   ├── api/
│   │   └── Dockerfile              # RAG API (Fargate + Lambda compatible)
│   ├── frontend/
│   │   └── Dockerfile              # Streamlit frontend playground
│   ├── eval-dashboard/
│   │   └── Dockerfile              # Streamlit eval dashboard
│   └── docker-compose.yml          # Local dev orchestration
│
├── infrastructure_as_code/
│   ├── librarian_api/              # Stack 1: RAG API serving ("model hosting")
│   │   ├── environments/
│   │   │   ├── dev.tfvars
│   │   │   ├── staging.tfvars
│   │   │   └── prod.tfvars
│   │   ├── modules/
│   │   │   ├── ecr/                # Container registry + lifecycle
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── ecs/                # Fargate cluster + service + task def + IAM
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── alb/                # Load balancer + listeners + TLS
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── vpc/                # VPC + subnets + routing
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── cloudwatch/         # Log groups + alarms + dashboards
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   └── secrets/            # Secrets Manager
│   │   │       ├── main.tf
│   │   │       ├── variables.tf
│   │   │       └── outputs.tf
│   │   ├── main.tf                 # Module composition + provider
│   │   ├── variables.tf            # Stack-level variables
│   │   ├── outputs.tf              # Stack-level outputs
│   │   └── backend.tf              # S3 + DynamoDB remote state
│   │
│   ├── librarian_llm/              # Stack 2: Bedrock/generation + data ("LLM lambda")
│   │   ├── environments/
│   │   │   ├── dev.tfvars
│   │   │   └── prod.tfvars
│   │   ├── modules/
│   │   │   ├── iam/                # Bedrock invoke + cross-service permissions
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── lambda/             # Ingestion trigger + optional API Lambda
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   └── s3/                 # Data lake + event notifications
│   │   │       ├── main.tf
│   │   │       ├── variables.tf
│   │   │       └── outputs.tf
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   │
│   └── _shared/                    # Shared data sources (read-only cross-stack refs)
│       └── data.tf                 # terraform_remote_state for cross-stack lookups
│
└── .github/
    └── workflows/
        ├── deploy-api.yml          # Build → ECR push → ECS rolling deploy
        ├── deploy-llm.yml          # Terraform apply librarian_llm
        └── terraform-plan.yml      # PR preview: plan both stacks on PR

```

## Design Decisions

### Two stacks, not one
- `librarian_api` and `librarian_llm` have different change velocity (API deploys on every push; LLM/data layer changes rarely)
- Independent state files prevent blast radius — a bad S3 change can't break ECS
- Cross-stack references via `terraform_remote_state` data source in `_shared/`

### Module granularity
- One module per AWS service boundary (ECR, ECS, ALB, etc.) — matches team's existing pattern
- Each module has `main.tf` + `variables.tf` + `outputs.tf` (standard convention)
- Modules are stack-local, not extracted to a shared registry (yet) — keep simple until a third stack needs them

### Environment promotion via tfvars
- Same modules, different parameters per environment
- `terraform workspace` avoided — explicit `.tfvars` files are more auditable and match team convention

### S3 remote backend
- Replace local backend before adding staging/prod
- One S3 bucket + DynamoDB table for state locking, partitioned by stack + environment key

### Security group pattern
- ALB SG and ECS SG stay in `librarian_api` stack (tightly coupled)
- Bedrock IAM permissions live in `librarian_llm/modules/iam/` (service boundary)

### Future: copilot routing / Agent Core
- The `librarian_api` ECS module is designed so a second service (copilot) can be added later
- If Agent Core replaces the copilot routing layer, it would be a third stack (`librarian_copilot/`) with Bedrock Agent resources
- ADK tool interfaces in application code provide the clean seam — no Terraform coupling

---

## Execution Steps

### Step 1: Create directory structure + move containers
Move `infra/docker/` → `infrastructure/containers/`, reorganize into per-service subdirectories. Update `docker-compose.yml` build context paths. Verify `docker compose build` still works.

**Files touched**: `infra/docker/*` → `infrastructure/containers/*`
**Risk**: Low — file moves only, no logic changes
**Validation**: `docker compose build` succeeds

### Step 2: Extract Terraform modules from flat files
Decompose each flat `.tf` file into its corresponding module under `librarian_api/modules/`. Wire up `librarian_api/main.tf` to call modules with current variable values as inputs. Keep identical resource configuration — **no behavior change**.

**Source → Module mapping**:
| Source file | Target module |
|---|---|
| `vpc.tf` | `modules/vpc/` |
| `ecr.tf` | `modules/ecr/` |
| `ecs.tf` | `modules/ecs/` |
| `alb.tf` | `modules/alb/` |
| `security.tf` | split across `modules/vpc/` (SGs) or dedicated `modules/security/` |
| `secrets.tf` | `modules/secrets/` |
| `outputs.tf` | stack-level `outputs.tf` (delegates to module outputs) |
| `variables.tf` | stack-level `variables.tf` (passes down to modules) |
| `main.tf` | stack-level `main.tf` (provider + module calls) |

**Risk**: Medium — must preserve resource addresses or use `moved {}` blocks
**Validation**: `terraform plan` shows no changes (zero diff)

### Step 3: Extract librarian_llm stack
Pull Lambda, S3, and Bedrock IAM resources into `librarian_llm/` as a separate stack. Add `_shared/data.tf` for cross-stack references (ECR URL from `librarian_api` state).

**Source → Module mapping**:
| Source file | Target module |
|---|---|
| `lambda.tf` | `librarian_llm/modules/lambda/` |
| `s3.tf` | `librarian_llm/modules/s3/` |
| IAM from `ecs.tf` (Bedrock perms) | `librarian_llm/modules/iam/` |

**Risk**: Medium — state migration (`terraform state mv`) for resources moving between stacks
**Validation**: Both stacks `terraform plan` shows no changes

### Step 4: Add environment tfvars + S3 backend
Create `environments/dev.tfvars` extracting current hardcoded defaults. Set up S3 bucket + DynamoDB table for remote state (can be manual or a bootstrap script). Migrate both stacks from local → remote backend.

**Risk**: Low-Medium — state migration to S3 is well-documented, one-time
**Validation**: `terraform init -migrate-state` succeeds; `terraform plan` shows no changes

### Step 5: Add CloudWatch module
Extract CloudWatch log group from `ecs.tf` into `modules/cloudwatch/`. Add basic alarms (5xx rate, latency p99 > 2s, ECS task health). This is net-new config beyond the current setup.

**Risk**: Low — additive only
**Validation**: `terraform plan` shows expected new resources

### Step 6: GitHub Actions CI/CD
Create three workflows:
- `terraform-plan.yml` — runs `terraform plan` on PR for both stacks, posts diff as PR comment
- `deploy-api.yml` — on merge to main (paths: `src/**`, `infrastructure/containers/api/**`): build → ECR push → ECS rolling deploy
- `deploy-llm.yml` — on merge to main (paths: `infrastructure/infrastructure_as_code/librarian_llm/**`): terraform apply

**Risk**: Low — additive, no infra changes
**Validation**: Dry-run workflow execution

### Step 7: Clean up old infra/ directory
Remove `infra/terraform/` and `infra/docker/` after confirming new structure works. Update any references in docs, CLAUDE.md, or scripts.

**Risk**: Low — only after full validation
**Validation**: Grep for old paths, verify no broken references

---

## Out of Scope

- NAT gateway / private subnets (cost optimization — add when needed for prod)
- OpenSearch Terraform module (separate initiative if moving off Chroma)
- Agent Core / copilot stack (future — design seam is in place)
- Terraform module registry / shared modules repo (premature until third stack)
- Custom domain / Route53 / ACM certificate provisioning
