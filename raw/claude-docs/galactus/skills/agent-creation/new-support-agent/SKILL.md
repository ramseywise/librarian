---
name: new-support-agent
description: "Scaffold a complete galactus support agent from scratch — foundation skeleton + RAG retrieval + 5-layer guardrails + eval harness. Opinionated L3 bundle for agents that answer customer questions from a Bedrock KB. Triggers on: 'create a new support agent', 'new HC agent', 'scaffold support agent', 'build a new customer-facing agent'."
allowed-tools: Read Grep Glob Bash Write
---

You are scaffolding a new galactus support agent end-to-end. This skill orchestrates three L2 skills in sequence — it does not duplicate their logic.

## Step 0 — Gather requirements

Ask the user (if not already clear from `$ARGUMENTS`):

1. **Agent name** — snake_case, e.g. `hc_billing`, `hc_tax` (becomes the module directory)
2. **Framework** — `langgraph` or `adk`
3. **Domain** — one-line description of what it answers, e.g. "German VAT and tax questions"
4. **Output directory** — default: `src/support_agents/{agent_name}/`

## Step 1 — Read the ref docs

Before generating any code, read:
1. `docs/google-adk.md` or `docs/langgraph.md` depending on framework
2. `docs/support-agents/invocation-flow.md` — full request pipeline
3. `docs/support-agents/observability.md` — what every agent must emit

## Step 2 — Foundation skeleton

Create the following files. This is the minimum viable agent shell — no capability code yet.

```
src/support_agents/{agent_name}/
  __init__.py
  schema.py       ← AssistantResponse, Source (copy from hc_adk/schema.py, adjust domain)
  config.py       ← Pydantic BaseSettings from .env
  main.py         ← FastAPI app, /chat endpoint, session management
  agent.py        ← Agent factory (ADK) or graph builder (LangGraph)
  prompts/
    system.txt    ← System prompt for the domain
  tests/
    test_schema.py
    test_agent_structure.py
```

For `schema.py`, use the canonical `AssistantResponse` from CLAUDE.md:
```python
class AssistantResponse(BaseModel):
    message: str
    suggestions: list[str] = []
    sources: list[Source] = []
    contact_support: bool = False
```

For `config.py`, include at minimum:
```python
bedrock_kb_id: str = Field(..., env="BEDROCK_KB_ID")
aws_region: str = Field("eu-west-1", env="AWS_REGION")
gemini_model: str = Field("gemini-2.5-flash", env="GEMINI_MODEL")  # ADK only
langfuse_secret_key: str = Field("", env="LANGFUSE_SECRET_KEY")
```

## Step 3 — Apply L2 capabilities in order

After the skeleton is written, run the three capability skills in this order:

1. **`/add-rag {output_dir}`** — wire Bedrock KB retrieval with RRF merge
2. **`/add-guardrails {output_dir}`** — wire 5-layer safeguard pipeline
3. **`/add-eval {agent_name}`** — create eval harness + seed JSONL dataset

Do not implement these capabilities yourself — invoke the L2 skills.

## Step 4 — Register the agent

Add to `infra/docker-compose.yml` (or `Makefile`) following the pattern of existing agents:
```yaml
{agent_name}:
  build: src/support_agents/{agent_name}
  ports:
    - "808X:8080"
  env_file: src/support_agents/{agent_name}/.env
```

## Step 5 — Update CLAUDE.md safeguards table

Add a row for the new agent to the 5-layer safeguards table in `CLAUDE.md`.

## Step 6 — Smoke test

Run:
```bash
uv run pytest src/support_agents/{agent_name}/tests/ --tb=short -q
make eval-{agent_name}  # dry-run the eval harness
```

## Done when

- All foundation files exist and import without errors
- `/chat` endpoint returns `AssistantResponse` with correct schema
- RAG retrieval, guardrails, and eval harness are wired (per L2 skill done-when conditions)
- CLAUDE.md safeguards table updated
- Smoke tests pass
