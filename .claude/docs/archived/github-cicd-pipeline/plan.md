# Plan — GitHub CI/CD Pipeline & Deploy Workflows

> Add GitHub Actions for CI (lint, test, terraform plan) and CD (build, push, deploy).
> Blocked by: GitHub App `workflows` permission not configured for Cord push.
> Unblock: push workflow files manually or grant Cord the `workflows` scope.
>
> Date: 2026-04-14
> Status: Ready to execute (pending permissions fix)
> Research: [terraform-restructure](../../in-progress/terraform-restructure/research.md) § 4

---

## Context

Workflow files were created, committed, then removed in `fe8fe82` because Cord's GitHub App
lacks the `workflows` permission. Content is preserved here and in git history. When permissions
are configured (or you push manually), re-create the files from the specs below.

---

## Existing Make/Test Infrastructure

The Makefile defines a tiered eval system that the CI pipeline must respect:

| Target | What it runs | Cost | CI tier |
|---|---|---|---|
| `eval-unit` | `tests/librarian/unit/` | Free, fast | **Always run on every PR + push** |
| `eval-regression` | `tests/librarian/evalsuite/regression/` | Free (InMemoryRetriever + MockEmbedder) | **Run on every PR + push** |
| `eval-capability` | `tests/librarian/evalsuite/capability/` | Slow, downloads 500MB model on cold cache | **Main-only or manual** (gated by `CONFIRM_EXPENSIVE_OPS=1`) |
| `eval-compare` | Variant comparison (hit_rate@k, MRR) | Free | Optional — manual or nightly |
| `eval-experiment` | LangFuse experiment runner | Requires API keys | **Never in CI** — local/manual only |
| `typecheck` | `mypy src/agents/librarian src/core` | Fast | **Run on every PR** |

### Additional tooling
- `uv run ruff check src/ tests/` — linting
- `uv run ruff format --check src/ tests/` — format check
- `uv run pytest tests/ -x --tb=short -q` — full test suite (used as catch-all)
- Pre-commit hooks: ruff, gitleaks, nbstripout, YAML/TOML/JSON checks

---

## Pipeline Design

### `.github/workflows/ci.yml` — Main CI Pipeline

```
Triggers: PR, push to main, workflow_dispatch
Concurrency: cancel-in-progress on non-main branches

PR flow:     lint → test (unit + regression) → typecheck → terraform plan (both stacks)
Main flow:   lint → test → typecheck → docker build/push → deploy staging → deploy prod
Manual flow: lint → test → typecheck → docker build/push → deploy (chosen env)
```

```yaml
name: CI Pipeline
run-name: CI on ${{ github.head_ref || github.ref_name }}

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production

permissions:
  id-token: write
  contents: read
  pull-requests: write

env:
  PYTHON_VERSION: "3.12"
  UV_CACHE_DIR: /tmp/.uv-cache

defaults:
  run:
    shell: bash

jobs:
  # -------------------------
  # LINT
  # -------------------------
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Ruff check
        run: uv run ruff check src/ tests/

      - name: Ruff format check
        run: uv run ruff format --check src/ tests/

  # -------------------------
  # TEST (unit + regression)
  # -------------------------
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Unit tests
        run: uv run pytest tests/librarian/unit/ -v
        env:
          ANTHROPIC_API_KEY: "test-key-not-real"

      - name: Regression tests
        run: uv run pytest tests/librarian/evalsuite/regression/ -v
        env:
          ANTHROPIC_API_KEY: "test-key-not-real"

  # -------------------------
  # TYPECHECK
  # -------------------------
  typecheck:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen

      - name: Mypy
        run: uv run mypy src/agents/librarian src/core

  # -------------------------
  # TERRAFORM PLAN (PR only)
  # -------------------------
  terraform-plan:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    needs: [test, typecheck]
    strategy:
      matrix:
        stack: [librarian_api, librarian_llm]
    defaults:
      run:
        working-directory: infrastructure/infrastructure_as_code/${{ matrix.stack }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.5"

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          aws-region: eu-west-1

      - name: Terraform init
        run: terraform init

      - name: Terraform plan
        id: plan
        run: terraform plan -var-file=environments/dev.tfvars -no-color -out=tfplan
        continue-on-error: true

      - name: Post plan to PR
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const output = `#### Terraform Plan: \`${{ matrix.stack }}\`
            \`\`\`
            ${{ steps.plan.outputs.stdout || 'No changes' }}
            \`\`\`
            *Triggered by @${{ github.actor }} on \`${{ github.event.pull_request.head.ref }}\`*`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

      - name: Fail on plan error
        if: steps.plan.outcome == 'failure'
        run: exit 1

  # -------------------------
  # BUILD & PUSH IMAGE (main or dispatch)
  # -------------------------
  docker-build-push:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    needs: [test, typecheck]
    outputs:
      image-uri: ${{ steps.build.outputs.image-uri }}
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_GITHUB_ACTIONS_ROLE_ARN }}
          aws-region: eu-west-1

      - name: Login to ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        id: build
        env:
          ECR_REGISTRY: ${{ steps.ecr-login.outputs.registry }}
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY_NAME }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          IMAGE_URI="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
          docker build -t "${IMAGE_URI}" -f infrastructure/containers/api/Dockerfile .
          docker push "${IMAGE_URI}"
          echo "image-uri=${IMAGE_URI}" >> "$GITHUB_OUTPUT"

  # -------------------------
  # AUTO DEPLOY (main push)
  # -------------------------
  deploy-staging:
    needs: docker-build-push
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image-uri: ${{ needs.docker-build-push.outputs.image-uri }}
    secrets: inherit

  deploy-production:
    needs: deploy-staging
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
      image-uri: ${{ needs.docker-build-push.outputs.image-uri }}
    secrets: inherit

  # -------------------------
  # MANUAL DEPLOY (workflow_dispatch)
  # -------------------------
  manual-deploy:
    needs: docker-build-push
    if: github.event_name == 'workflow_dispatch'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: ${{ inputs.environment }}
      image-uri: ${{ needs.docker-build-push.outputs.image-uri }}
    secrets: inherit

  # -------------------------
  # FAILURE NOTIFICATION
  # -------------------------
  notify-on-failure:
    if: failure() && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    needs: [deploy-production]
    steps:
      - name: Notify
        run: echo "::error::Deployment pipeline failed on main"
```

### `.github/workflows/deploy.yml` — Reusable Deploy

```yaml
name: Deploy to ECS

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-uri:
        required: true
        type: string

permissions:
  id-token: write
  contents: read

jobs:
  gate:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Environment gate
        run: echo "Deployment approved for ${{ inputs.environment }}"

  deploy:
    needs: gate
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infrastructure/infrastructure_as_code/librarian_api
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars[format('{0}_AWS_ROLE_ARN', inputs.environment)] }}
          aws-region: eu-west-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.5"

      - name: Terraform init
        run: terraform init

      - name: Terraform apply (ECS image update)
        run: |
          terraform apply \
            -var-file=environments/${{ inputs.environment }}.tfvars \
            -var="container_image=${{ inputs.image-uri }}" \
            -auto-approve \
            -target=module.ecs

      - name: Wait for ECS service stable
        run: |
          aws ecs wait services-stable \
            --cluster librarian-${{ inputs.environment }} \
            --services librarian-${{ inputs.environment }}-api \
            --region eu-west-1
        timeout-minutes: 10

      - name: Health check
        run: |
          ALB_DNS=$(terraform output -raw alb_dns_name)
          for i in $(seq 1 10); do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${ALB_DNS}/health" || true)
            if [ "$STATUS" = "200" ]; then
              echo "Health check passed"
              exit 0
            fi
            echo "Attempt $i: status=$STATUS, retrying..."
            sleep 5
          done
          echo "::error::Health check failed after 10 attempts"
          exit 1
```

---

## Execution Steps

### Step 1: Fix GitHub App permissions (prerequisite)
Either grant Cord the `workflows` scope in repo settings, or plan to push workflow files manually.

### Step 2: Create workflow files
Copy the YAML above into `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`.

### Step 3: Configure GitHub repo
- Add environment protection rules for `staging` and `production`
- Set repository variables: `AWS_GITHUB_ACTIONS_ROLE_ARN`, `ECR_REPOSITORY_NAME`
- Set environment-specific variables: `staging_AWS_ROLE_ARN`, `production_AWS_ROLE_ARN`
- Set secrets: `GITHUB_TOKEN` (auto), AWS OIDC federation for role assumption

### Step 4: Validate
- Open a PR → verify lint + test + typecheck + terraform plan runs
- Merge to main → verify build + push + staging deploy + production deploy

---

## Considerations

### Test tier alignment with CI
- `eval-unit` + `eval-regression` run on every PR (fast, free, no API keys)
- `eval-capability` skipped in CI (500MB model download, gated by `CONFIRM_EXPENSIVE_OPS`)
- `eval-experiment` never in CI (requires LangFuse API keys, manual only)
- `typecheck` (mypy) runs in parallel with tests for faster feedback

### Future: shared workflow migration
When integrating with `ageras-com/github-actions`:
1. Replace docker build/push with `ageras-com/github-actions/.github/actions/docker/build-and-push-ecr@v11`
2. Replace terraform deploy with `ageras-com/github-actions/.github/workflows/awsonnet-ecs-deploy.yml@v11`
3. Add Jsonnet task definition if going awsonnet route
4. Align region (`eu-north-1` team standard vs `eu-west-1` current)

### Capability test caching
Consider a scheduled weekly workflow that runs `eval-capability` with model cache warmed
via GitHub Actions cache. This catches regressions without blocking every PR.
