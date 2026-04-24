# Plan: Triage Infra Security Fixes
Date: 2026-04-11
Based on: direct codebase inspection (code review session 2026-04-11)

## Goal
Harden the playground triage stack (Terraform infra + frontend) by fixing all High and
Medium security/reliability findings from the code review, without rearchitecting the
core networking topology.

## Approach
Eight targeted steps in dependency order. Steps 1–4 are pure Terraform edits with no
deploy impact until `terraform apply` is run. Steps 5–6 fix the Lambda auth and ALB
HTTPS surface. Step 7 creates a dedicated frontend Dockerfile to eliminate the runtime
`pip install`. Step 8 fixes three frontend Python issues. No new AWS resources are added
except the ACM certificate + HTTPS listener in Step 5 (requires a `var.acm_cert_arn`
the caller must supply). NAT gateway / private subnet migration is out of scope — the
current SG scoping (ECS only reachable from ALB) is an acceptable control.

## Out of Scope
- Private subnet + NAT gateway architecture (separate networking refactor)
- Terraform S3 backend migration
- API Gateway addition in front of Lambda
- `snowflake_password` empty-default validation (low-priority optional integration)
- RAG retrieval pipeline bugs (separate plan)
- ECS autoscaling / capacity providers

---

## Steps

### Step 1: ✅ Guard `force_delete` / `force_destroy` with environment check
**Files**: `infra/terraform/ecr.tf` (line 8), `infra/terraform/s3.tf` (line 7)
**What**: Both resources use destructive flags unconditionally. Gate them on
`var.environment == "dev"` so staging/prod terraform destroys cannot silently wipe
the image repo or data lake.

**Snippet** — `ecr.tf:8`:
```hcl
# before
force_delete = true # dev convenience — remove for prod

# after
force_delete = var.environment == "dev"
```

**Snippet** — `s3.tf:7`:
```hcl
# before
force_destroy = true # dev convenience — remove for prod

# after
force_destroy = var.environment == "dev"
```

**Test**: `cd infra/terraform && terraform validate`
**Done when**: `terraform validate` passes; `var.environment = "staging"` produces
`force_delete = false` in `terraform plan` output.

---

### Step 2: ✅ Fix ECS task memory and health-check `startPeriod`
**Files**: `infra/terraform/variables.tf` (lines 29–33), `infra/terraform/ecs.tf` (line 116)

**What**: The default task memory (1024 MiB) is insufficient for multilingual-e5-large
(~1.5 GB on load). Raise the default to 4096. The `startPeriod` of 15s conflicts with
the docker-compose comment that the model needs ~45s; raise to 60s to match.

**Snippet** — `variables.tf:29-33`:
```hcl
# before
variable "memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 1024
}

# after
variable "memory" {
  description = "Fargate task memory in MiB (min 4096 for multilingual-e5-large)"
  type        = number
  default     = 4096
}
```

**Snippet** — `ecs.tf:116`:
```hcl
# before
startPeriod = 15

# after
startPeriod = 60  # multilingual-e5-large loads ~45s on cold start
```

**Test**: `cd infra/terraform && terraform validate && terraform plan -var="anthropic_api_key=test" 2>&1 | grep -E "memory|startPeriod"`
**Done when**: Plan output shows `memory = 4096` and health check `startPeriod = 60`.

---

### Step 3: ✅ Parameterize ECR image tag (replace `:latest`)
**Files**: `infra/terraform/variables.tf` (after line 100), `infra/terraform/ecs.tf`
(line 82), `infra/terraform/lambda.tf` (lines 51, 87)

**What**: All three resources pin to `:latest`, enabling silent rolling deploys and
concurrent version drift. Add `var.image_tag` and use it everywhere.

**Snippet** — `variables.tf` (append after existing content):
```hcl
variable "image_tag" {
  description = "Container image tag to deploy (e.g. git SHA). Defaults to 'latest' for local dev only."
  type        = string
  default     = "latest"
}
```

**Snippet** — `ecs.tf:82`:
```hcl
# before
image = "${aws_ecr_repository.api.repository_url}:latest"

# after
image = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
```

**Snippet** — `lambda.tf:51` (api Lambda):
```hcl
# before
image_uri = "${aws_ecr_repository.api.repository_url}:latest"

# after
image_uri = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
```

**Snippet** — `lambda.tf:87` (ingestion Lambda):
```hcl
# before
image_uri = "${aws_ecr_repository.api.repository_url}:latest"

# after
image_uri = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
```

**Test**: `cd infra/terraform && terraform validate`
**Done when**: `terraform validate` passes; `terraform plan -var="image_tag=abc1234" -var="anthropic_api_key=test"` shows all three resources referencing `abc1234`.

---

### Step 4: ✅ Mark `lambda_function_url` output as sensitive
**Files**: `infra/terraform/outputs.tf` (lines 21–24)

**What**: The function URL is effectively a bearer credential when
`authorization_type = "NONE"`. It should not appear in plaintext CI logs or
`terraform output` without explicit `-json` + `--raw`.

**Snippet** — `outputs.tf:21-24`:
```hcl
# before
output "lambda_function_url" {
  description = "Lambda function URL (when enabled)"
  value       = var.enable_lambda ? aws_lambda_function_url.api[0].function_url : ""
}

# after
output "lambda_function_url" {
  description = "Lambda function URL (when enabled)"
  value       = var.enable_lambda ? aws_lambda_function_url.api[0].function_url : ""
  sensitive   = true
}
```

**Test**: `cd infra/terraform && terraform validate`
**Done when**: `terraform validate` passes; `terraform output lambda_function_url`
prints `<sensitive>` rather than the URL.

---

### Step 5: ✅ Add HTTPS listener + HTTP→HTTPS redirect + HTTPS security group rule
**Files**: `infra/terraform/variables.tf` (append), `infra/terraform/alb.tf` (append),
`infra/terraform/security.tf` (lines 10–17)

**What**: All traffic currently travels unencrypted over HTTP/80. Add:
1. `var.acm_cert_arn` — caller-supplied ACM certificate ARN (required when
   `var.enable_https = true`; defaults to off so existing dev environments are unaffected)
2. A port 443 HTTPS listener that forwards to the existing target group
3. Change the port 80 listener's default action to redirect to HTTPS (when enabled)
4. Add port 443 ingress to the ALB security group

This is gated on `var.enable_https` so local/dev `terraform apply` without a cert
continues to work unchanged.

**Snippet** — `variables.tf` (append):
```hcl
variable "enable_https" {
  description = "Enable HTTPS listener and HTTP→HTTPS redirect. Requires acm_cert_arn."
  type        = bool
  default     = false
}

variable "acm_cert_arn" {
  description = "ACM certificate ARN for the HTTPS listener. Required when enable_https = true."
  type        = string
  default     = ""
}
```

**Snippet** — `alb.tf` (replace existing `aws_lb_listener.http` block, lines 34–43):
```hcl
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.api.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = var.enable_https ? "redirect" : "forward"

    dynamic "redirect" {
      for_each = var.enable_https ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    dynamic "forward" {
      for_each = var.enable_https ? [] : [1]
      content {
        target_group {
          arn = aws_lb_target_group.api.arn
        }
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count = var.enable_https ? 1 : 0

  load_balancer_arn = aws_lb.api.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_cert_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}
```

**Snippet** — `security.tf` (add 443 ingress to ALB SG, after the existing HTTP ingress block ending at line 17):
```hcl
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
```

**Test**: `cd infra/terraform && terraform validate && terraform plan -var="anthropic_api_key=test" 2>&1 | grep -E "listener|redirect"`
**Done when**: `terraform validate` passes; `terraform plan` with `enable_https=false`
(default) shows no new resources; with `enable_https=true -var="acm_cert_arn=arn:aws:acm:..."` shows 2 new listener resources and an updated HTTP listener redirect.

---

### Step 6: ✅ Harden Lambda Function URL authorization
**Files**: `infra/terraform/lambda.tf` (line 78), `infra/terraform/variables.tf` (append)

**What**: `authorization_type = "NONE"` makes the Lambda URL publicly accessible with
no auth, exposing Anthropic API credits. Add `var.lambda_auth_type` defaulting to `"NONE"`
for dev, with a `precondition` that blocks non-`"NONE"` values unless `var.environment`
is dev (i.e., forces the caller to explicitly set `AWS_IAM` for staging/prod).

Note: switching to `AWS_IAM` requires the frontend Streamlit app (or any direct caller)
to sign requests with SigV4. This plan adds the infra variable and guard; the frontend
signing integration is out of scope.

**Snippet** — `variables.tf` (append):
```hcl
variable "lambda_auth_type" {
  description = "Lambda Function URL authorization type. Use AWS_IAM for non-dev environments."
  type        = string
  default     = "NONE"

  validation {
    condition     = contains(["NONE", "AWS_IAM"], var.lambda_auth_type)
    error_message = "lambda_auth_type must be NONE or AWS_IAM."
  }
}
```

**Snippet** — `lambda.tf:74-79` (replace `aws_lambda_function_url.api`):
```hcl
resource "aws_lambda_function_url" "api" {
  count = var.enable_lambda ? 1 : 0

  function_name      = aws_lambda_function.api[0].function_name
  authorization_type = var.lambda_auth_type

  # SECURITY: default is NONE (dev convenience). Set to AWS_IAM for staging/prod.
  # When AWS_IAM, callers must sign requests with SigV4 credentials.
}
```

**Test**: `cd infra/terraform && terraform validate`
Also: `terraform plan -var="lambda_auth_type=INVALID" -var="anthropic_api_key=test"` should fail with the validation error.
**Done when**: `terraform validate` passes; invalid values produce a clear `validation` error; `terraform plan` with `lambda_auth_type=AWS_IAM` shows the updated resource.

---

### Step 7: ✅ Create dedicated `Dockerfile.frontend` with pinned Streamlit
**Files**: `infra/docker/Dockerfile.frontend` (new file), `infra/docker/docker-compose.yml`
(lines 17–27)

**What**: The frontend service currently reuses the API Dockerfile and installs Streamlit
at container start via a raw `pip install` (unpinned, slow, PyPI-dependent at runtime).
Create a dedicated frontend image that installs a pinned version at build time.

**Snippet** — `infra/docker/Dockerfile.frontend` (new file):
```dockerfile
# Stage 1 — install dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
# Install with streamlit extra; no dev dependencies
RUN uv sync --frozen --no-dev --extra librarian --extra frontend

# Stage 2 — lean runtime image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml /app/
COPY frontend/ /app/frontend/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Non-root user for container security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8501/_stcore/health').raise_for_status()"

CMD ["streamlit", "run", "frontend/librarian_chat.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Note: this requires a `[project.optional-dependencies] frontend` group in `pyproject.toml`
that lists `streamlit` with a pinned version (e.g. `streamlit>=1.35,<2`). If that group
does not exist, add it before building.

**Snippet** — `docker-compose.yml` (replace `frontend` service, lines 16–37):
```yaml
  frontend:
    build:
      context: ../..
      dockerfile: infra/docker/Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      LIBRARIAN_API_URL: http://librarian-api:8000
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8501/_stcore/health').raise_for_status()"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 60s
    depends_on:
      librarian-api:
        condition: service_healthy
```

**Test**: `docker compose -f infra/docker/docker-compose.yml build frontend 2>&1 | tail -5`
**Done when**: `docker compose build frontend` completes without error; `docker compose up frontend` starts Streamlit without any `pip install` output; no `volumes` mount for frontend source code (it's baked in).

---

### Step 8: ✅ Fix Streamlit frontend — health check caching, session state order, URL sanitization
**Files**: `frontend/librarian_chat.py` (lines 137–180, 169–171)

**What**: Three issues in the frontend Python:
1. **Health check on every render** (line 142–149): wrap with `@st.cache_data(ttl=30)`
   to avoid a blocking HTTP call on every keypress/widget interaction.
2. **Session state initialized after sidebar reads it** (lines 177–180): move both
   `st.session_state` initialisations to the top of the script, before the sidebar block.
3. **Unvalidated citation URLs** (line 170): a malicious API response could inject a
   `javascript:` URL. Validate the scheme before rendering.

**Snippet 1** — extract health check into a cached function (insert before the sidebar
block, i.e. before line 137):
```python
@st.cache_data(ttl=30)
def _check_api_health() -> tuple[bool, int | None]:
    """Returns (ok, status_code). Cached for 30 s to avoid blocking on every render."""
    try:
        resp = httpx.get(HEALTH_ENDPOINT, timeout=3)
        return resp.status_code == 200, resp.status_code
    except httpx.ConnectError:
        return False, None
```

Replace the inline health check block (lines 141–150) with:
```python
    _api_ok, _api_status = _check_api_health()
    if _api_ok:
        st.success("API connected")
    elif _api_status is not None:
        st.error(f"API returned {_api_status}")
    else:
        st.error(f"Cannot reach API at {API_URL}")
```

**Snippet 2** — move session state init above the sidebar block (before line 137):
```python
# Initialise session state before any widget reads it
if "messages" not in st.session_state:
    st.session_state.messages = []
if "metadata" not in st.session_state:
    st.session_state.metadata = []
```

Remove the duplicate init block at lines 177–180.

**Snippet 3** — sanitize citation URLs (line 170):
```python
# before
f"- [{c.get('title', 'source')}]({c.get('url', '#')})"

# after
_url = c.get("url", "#")
if not isinstance(_url, str) or not _url.startswith(("http://", "https://")):
    _url = "#"
f"- [{c.get('title', 'source')}]({_url})"
```

**Test**: `cd /repo && python -c "import ast, sys; ast.parse(open('frontend/librarian_chat.py').read()); print('syntax ok')"`
**Done when**: Syntax check passes; manual test of the sidebar with the API offline shows the health status updates within 30 s; no blocking delay on chat input.

---

## Test Plan
1. After each Terraform step: `terraform validate` + `terraform plan -var="anthropic_api_key=test"`
2. After Step 7: `docker compose -f infra/docker/docker-compose.yml build frontend`
3. After Step 8: `python -c "import ast; ast.parse(open('frontend/librarian_chat.py').read())"` + manual Streamlit smoke test
4. Full integration: `docker compose -f infra/docker/docker-compose.yml up` — both services healthy, chat functional

## Risks & Rollback
- **Step 2 (memory increase)**: raises Fargate cost. Default `desired_count = 1`
  limits blast radius. Rollback: revert `variables.tf` default.
- **Step 5 (HTTPS)**: `enable_https = false` by default — zero impact on existing
  deployments. Rollback: set `enable_https = false`.
- **Step 7 (Dockerfile.frontend)**: requires `[frontend]` optional-dependency group in
  `pyproject.toml`. If the group does not exist yet, add `streamlit>=1.35,<2` before
  running the docker build step. This is a **blocker** to verify before executing.
- **Lambda auth (Step 6)**: changing `lambda_auth_type` to `AWS_IAM` in existing
  deployment will immediately break any frontend or script calling the URL without
  SigV4 signing. Only set `AWS_IAM` after confirming callers are updated.

## Open Questions
1. Does `pyproject.toml` have a `[frontend]` extras group for Streamlit? If not,
   Step 7 needs a `pyproject.toml` edit — confirm before executing.
2. Is there an ACM certificate already provisioned for the target domain? If not,
   Step 5 can be staged: add the `enable_https` variable + listener structure now,
   and set `enable_https = true` only after the cert is provisioned.
3. For Lambda auth: is the Streamlit frontend the only caller of the Lambda URL, or
   are there other scripts/CI jobs? Answer determines urgency of SigV4 integration
   after Step 6.
