---
title: ADK Observability
tags: [adk, infra, pattern]
summary: Four-tier observability for ADK agents — Cloud Trace (always-on), prompt-response logging, BigQuery Agent Analytics plugin, and third-party platforms (AgentOps, Phoenix, MLflow, etc.).
updated: 2026-07-14
sources:
  - raw/claude-docs/project-g/.agents/skills/adk-observability-guide/SKILL.md
  - raw/claude-docs/project-g/.agents/skills/adk-observability-guide/references/bigquery-agent-analytics.md
  - raw/claude-docs/project-g/.agents/skills/adk-observability-guide/references/cloud-trace-and-logging.md
  - raw/agent-skills/adk-observability-guide/SKILL.md
  - raw/agent-skills/adk-observability-guide/references/bigquery-agent-analytics.md
  - raw/agent-skills/adk-observability-guide/references/cloud-trace-and-logging.md
  - raw/agent-skills/observability/SKILL.md
---

# ADK Observability

ADK provides four tiers of observability that can be combined. Cloud Trace is always-on; the others are opt-in.

For deployment setup, see [[ADK Deployment Patterns]]. For the broader GCP observability comparison, see [[Observability and Runtime Patterns]].

---

## Observability Tiers

| Tier | What It Does | Default State | Best For |
|---|---|---|---|
| **Cloud Trace** | Distributed tracing — execution flow, latency, errors via OpenTelemetry spans | Always enabled | Debugging latency, understanding execution flow |
| **Prompt-Response Logging** | GenAI interactions → GCS (JSONL), BigQuery, Cloud Logging | Disabled locally; enabled when deployed | Auditing LLM interactions, compliance |
| **BigQuery Agent Analytics** | Structured agent events (LLM calls, tool use, outcomes) → BigQuery | Opt-in (`--bq-analytics` at scaffold time) | Conversational analytics, custom dashboards, LLM-as-judge evals |
| **Third-Party Integrations** | External observability platforms (AgentOps, Phoenix, MLflow, etc.) | Opt-in per-provider | Team collaboration, specialized visualization |

---

## Cloud Trace

ADK uses OpenTelemetry for distributed tracing. Every agent invocation produces spans covering the full execution flow.

**Span hierarchy:**
```
invocation
  └── agent_run (one per agent in the chain)
        ├── call_llm (model request/response)
        └── execute_tool (tool execution)
```

**Setup by deployment type:**

| Deployment | Setup |
|---|---|
| Agent Engine | Automatic — traces exported to Cloud Trace by default |
| Cloud Run (scaffolded) | Automatic — `otel_to_cloud=True` in the FastAPI app |
| Cloud Run (manual) | Configure OpenTelemetry exporter manually |
| Local dev | Works with `make playground`; visible in Cloud Console |

View traces: **Cloud Console → Trace → Trace explorer**

**Troubleshooting:** If no traces appear, verify `otel_to_cloud=True` in FastAPI app and that the service account has the `cloudtrace.agent` role.

---

## Prompt-Response Logging

Captures GenAI interactions (model name, tokens, timing) and exports to GCS (JSONL), BigQuery (external tables), and Cloud Logging.

**Privacy-preserving by default** — only metadata is logged unless explicitly configured.

### Environment Variables

| Variable | Purpose |
|---|---|
| `LOGS_BUCKET_NAME` | GCS bucket for completions and logs. Required to enable logging |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | `NO_CONTENT` (metadata only), `true` (full content), `false` (disabled) |
| `BQ_ANALYTICS_DATASET_ID` | BigQuery dataset for telemetry |
| `BQ_ANALYTICS_CONNECTION_ID` | BigQuery connection for GCS access |
| `GENAI_TELEMETRY_PATH` | Optional: override upload path within bucket (default: `completions`) |

**Local enable:**
```bash
export LOGS_BUCKET_NAME="your-bucket-name"
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="NO_CONTENT"
make playground
```

**Disable in deployed environments:** set `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` in `deployment/terraform/service.tf` and re-apply.

### Terraform-Provisioned Infrastructure (Scaffolded Projects)

All provisioned by `deployment/terraform/telemetry.tf`:

- **Cloud Logging bucket** — 10-year retention, analytics enabled, dedicated to GenAI telemetry
- **Log sinks** — Route GenAI inference + feedback logs to the telemetry bucket
- **Linked dataset** — Cloud Logging bucket linked to BigQuery for SQL access
- **GCS logs bucket** — Stores completions as NDJSON
- **BigQuery dataset** — External tables over GCS data
- **BigQuery connection** — Service account for GCS access from BigQuery

### BigQuery Dataset Naming

BigQuery dataset names cannot contain hyphens. Terraform automatically converts hyphens to underscores:
- Project name `my-agent` → BQ dataset `my_agent_telemetry`

Two datasets:
- `{name}_telemetry` — External tables over GCS completions data
- `{name}_genai_telemetry_logs` — Linked dataset from Cloud Logging bucket

### Verification

```bash
# Check GCS data
gsutil ls gs://${PROJECT_ID}-${PROJECT_NAME}-logs/completions/

# Check Cloud Logging bucket
gcloud logging buckets describe ${PROJECT_NAME}-genai-telemetry \
  --location=us-central1 --project=${PROJECT_ID}

# Query BigQuery
bq query --use_legacy_sql=false \
  "SELECT * FROM \`${PROJECT_ID}.${PROJECT_NAME}_telemetry.completions\` LIMIT 10"
```

---

## BigQuery Agent Analytics Plugin

Optional plugin that logs structured agent events to BigQuery via the Storage Write API.

**Enable:**
- At scaffold time: `uvx agent-starter-pack create . --bq-analytics`
- Post-scaffold: add the plugin manually to `app/agent.py`

**Key features:**
- Conversational analytics — session flows, user interaction patterns
- LLM-as-judge evals — structured data for evaluation pipelines
- Looker Studio integration for custom dashboards
- Tool provenance tracking: `LOCAL`, `MCP`, `SUB_AGENT`, `A2A`, `TRANSFER_AGENT`
- Auto-schema upgrade (new fields added without migration)
- GCS offloading for multimodal content (images, audio)
- Distributed tracing via OpenTelemetry span context

**BigQuery plugin in code:**
```python
# Enabled via plugin on the App object (scaffolded projects set this up automatically)
# Check app/agent.py for BigQueryAgentAnalyticsPlugin configuration
# BQ_ANALYTICS_DATASET_ID env var must be set
```

**Troubleshooting:** Verify plugin is configured in `app/agent.py` and `BQ_ANALYTICS_DATASET_ID` env var is set.

---

## Third-Party Integrations

| Platform | Key Differentiator | Self-Hosted | Setup |
|---|---|---|---|
| **AgentOps** | Session replays, 2-line setup, replaces native telemetry | No (SaaS) | Minimal |
| **Arize AX** | Commercial, production monitoring, eval dashboards | No (SaaS) | Low |
| **Phoenix** | Open-source, custom evaluators, experiment testing | Yes | Low |
| **MLflow** | OTel traces to MLflow Tracking Server, span tree visualization | Yes | Medium (needs SQL backend) |
| **Monocle** | 1-call setup, VS Code Gantt chart visualizer | Yes (local files) | Minimal |
| **Weave (W&B)** | Team collaboration, timeline views | No (SaaS) | Low |
| **Freeplay** | Prompt management + evals + observability in one platform | No (SaaS) | Low |

For setup details, fetch the relevant ADK integration docs pages.

**Note:** Some providers (AgentOps) replace native telemetry — check whether you need both native Cloud Trace and the third-party platform.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| No traces in Cloud Trace | Verify `otel_to_cloud=True`; check SA has `cloudtrace.agent` role |
| Prompt-response data not appearing | Check `LOGS_BUCKET_NAME` is set; verify SA has `storage.objectCreator`; check app logs for telemetry setup warnings |
| Privacy mode misconfigured | Check `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` value |
| BigQuery Analytics not logging | Verify plugin in `app/agent.py`; check `BQ_ANALYTICS_DATASET_ID` env var |
| Third-party integration not capturing spans | Check provider-specific env vars (API keys, endpoints) |
| Traces missing tool spans | Check trace explorer filters — tool spans appear under `execute_tool` |
| High telemetry costs | Switch to `NO_CONTENT` mode; reduce BigQuery retention; disable unused tiers |

---

## See Also

- [[ADK Deployment Patterns]]
- [[Observability and Runtime Patterns]]
- [[Langfuse Platform]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Production Hardening Patterns]]
