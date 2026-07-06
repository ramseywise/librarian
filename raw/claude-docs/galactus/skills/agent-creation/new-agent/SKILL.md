---
name: new-agent
description: >
  Scaffold a complete AI agent from scratch — framework-agnostic, project-agnostic.
  Generates all files for a LangGraph or Google ADK agent: schema, state,
  graph/callbacks, retrieval subgraph, infra (pyproject, Makefile, Dockerfile),
  tests, eval harness, and docs. Dispatches parallel subagents — one per concern —
  so all files are written simultaneously.
  Triggers on: "scaffold a new agent", "create /new-agent", "new LangGraph agent",
  "new ADK agent", "/new-agent <name>".
updated: 2026-05-26
---

# /new-agent — AI Agent Factory

Scaffold a complete agent in one command — framework-agnostic, project-agnostic.
Parallel subagents write every file simultaneously; total wall-clock time ≈ single-subagent time.

---

## Usage

```
/new-agent <name> [--framework adk|langgraph] [--domain <string>] \
  [--capabilities cap1,cap2,...] [--output path/to/dir]
```

**Arguments:**

| Arg | Default | Description |
|-----|---------|-------------|
| `<name>` | required | snake_case agent name, e.g. `order_support`, `insights_agent` |
| `--framework` | `langgraph` | `langgraph` or `adk` |
| `--domain` | `general` | Free-form label for the agent's domain — injected into prompts and README (e.g. `ecommerce`, `finance`, `hr`) |
| `--capabilities` | none | Comma-separated from the capability list below |
| `--output` | auto | Defaults to `src/agents/{name}` |

**Capability tokens:**

| Token | What it adds |
|-------|-------------|
| `rag` | CRAG retrieval subgraph + Bedrock/RAG backend toggle |
| `search` | Web/KB search tool with result formatting |
| `forecast` | Time-series forecasting pipeline (Polars + statsmodels) |
| `cluster` | Clustering / segmentation pipeline |
| `kg` | Knowledge-graph retrieval tool (Neptune / in-memory) |
| `genai` | GenAI tools: image gen, document analysis, code execution |
| `hitl` | Human-in-the-loop interrupt gates + approval flows |
| `streaming` | SSE streaming endpoint + token-level output |
| `batch` | Batch runner with JSONL I/O + progress tracking |
| `vision` | Image/PDF ingestion + multimodal prompting |
| `langchain` | LCEL chains, output parsers, retrieval chain, memory, streaming callbacks |
| `a2a` | Agent-to-agent protocol (Google A2A) client + server stub |
| `finetune` | Fine-tuning data pipeline + experiment tracking |
| `rlhf` | RLHF preference data collection + reward model scaffold |

---

## Execution steps

### Step 1 — Parse arguments

Extract from the invocation string:
- `name` (required, snake_case)
- `framework` (default: `langgraph`)
- `domain` (default: `custom`)
- `capabilities` list (split on `,`, strip whitespace)
- `output_path`:
  - If `--output` provided: use as-is
  - Else: `src/agents/{name}` (generic default — user can override)

Validate:
- `name` matches `^[a-z][a-z0-9_]*$` — error if not
- `framework` is one of `langgraph`, `adk` — error if not
- Each capability is in the capability list above — warn and skip unknowns

### Step 2 — Load spec files

Read these files with the Read tool. Load ALL of them unconditionally:

```
~/.claude/skills/new-agent/specs/core.md
~/.claude/skills/new-agent/specs/framework-{framework}.md
~/.claude/skills/new-agent/specs/infra.md
~/.claude/skills/new-agent/specs/test.md
~/.claude/skills/new-agent/specs/eval.md
~/.claude/skills/new-agent/specs/docs.md
```

For each capability in `--capabilities`, also load:
```
~/.claude/skills/new-agent/specs/cap-{capability}.md
```

If a capability spec file doesn't exist, log a warning and skip — do not error.

### Step 3 — Dispatch parallel subagents

**In a SINGLE message**, spawn all subagents via the Agent tool with
`isolation: "worktree"`. Do not await between spawns.

**Always spawn these six:**

---

**schema-builder**
```
You are the schema-builder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{core_md_content}

Write all files. No summary needed.
```

---

**agent-builder**
```
You are the agent-builder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{framework_spec_content}

Write all files. No summary needed.
```

---

**infra-builder**
```
You are the infra-builder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{infra_md_content}

Write all files. No summary needed.
```

---

**test-scaffolder**
```
You are the test-scaffolder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{test_md_content}

Write all files. No summary needed.
```

---

**eval-harness-builder**
```
You are the eval-harness-builder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{eval_md_content}

Write all files. No summary needed.
```

---

**docs-builder**
```
You are the docs-builder for the /new-agent factory.

Agent config:
- name: {name}
- framework: {framework}
- domain: {domain}
- output_dir: {output_path}
- capabilities: {capabilities_list}

Your job: write exactly the files listed in your spec below. Substitute:
- {AGENT_NAME} → {name}
- {DOMAIN} → {domain}
- {FRAMEWORK} → {framework}
- {OUTPUT_DIR} → {output_path}

Spec:
{docs_md_content}

Write all files. No summary needed.
```

---

**Capability subagents** — spawn only for capabilities present in `--capabilities`:

| Capability | Role name | Spec file |
|-----------|-----------|-----------|
| `rag` | rag-builder | cap-rag.md |
| `search` | search-builder | cap-search.md |
| `forecast` or `cluster` | data-pipeline-builder | cap-forecast.md and/or cap-cluster.md (concatenate) |
| `kg` | kg-builder | cap-kg.md |
| `genai` | genai-tools-builder | cap-genai.md |
| `hitl` | hitl-builder | cap-hitl.md |
| `streaming` | streaming-builder | cap-streaming.md |
| `batch` | batch-builder | cap-batch.md |
| `vision` | vision-builder | cap-vision.md |
| `a2a` | a2a-builder | cap-a2a.md |
| `finetune` | finetune-builder | cap-finetune.md |
| `rlhf` | rlhf-builder | cap-rlhf.md |

Each capability subagent uses the same prompt template as above, with
`{spec_content}` replaced by the loaded capability spec content.

**Token efficiency:** Each subagent receives only its relevant spec (5-15 KB), not
the full conversation context. Parallel dispatch means all subagents run
simultaneously. Total cost ≈ n_subagents × ~10K tokens each — far cheaper than a
single 50K-token sequential loop. Never pass all spec content to all subagents.

### Step 4 — Post-generation validation

After all subagents complete, run from `{output_path}`:

```bash
uv run ruff check . --fix --exclude .venv
uv run pytest tests/ -x -q
```

Report:
- Files written (grouped by subagent)
- Lint warnings fixed / remaining
- Test pass/fail summary
- Any subagent that failed to write its files

---

## Output structure (LangGraph)

```
{output_path}/
  schema.py           # schema-builder
  config.py           # schema-builder
  observability.py    # schema-builder
  memory.py           # schema-builder
  state.py            # agent-builder
  agent.py            # agent-builder
  subgraphs/
    __init__.py
    retrieval.py      # agent-builder (or rag-builder if rag cap)
  prompts/
    answer.txt        # schema-builder
    clarify.txt       # schema-builder
    escalate.txt      # schema-builder
  tests/
    __init__.py
    test_schema.py    # test-scaffolder
    test_agent.py     # test-scaffolder
  evals/
    runner.py         # eval-harness-builder
    graders.py        # eval-harness-builder
    data/
      qa.jsonl        # eval-harness-builder (3 seed examples)
  pyproject.toml      # infra-builder
  Makefile            # infra-builder
  Dockerfile          # infra-builder
  .env.example        # infra-builder
  README.md           # docs-builder
```

## Output structure (ADK)

```
{output_path}/
  schema.py           # schema-builder
  config.py           # schema-builder
  observability.py    # schema-builder
  memory.py           # schema-builder
  agent.py            # agent-builder
  app.py              # agent-builder
  sub_agents/
    __init__.py       # agent-builder
    domain_agent.py   # agent-builder
  prompts/
    {name}.txt        # agent-builder
    answer.txt        # schema-builder
    clarify.txt       # schema-builder
    escalate.txt      # schema-builder
  tests/
    __init__.py
    test_schema.py    # test-scaffolder
    test_agent.py     # test-scaffolder
  evals/
    runner.py         # eval-harness-builder
    graders.py        # eval-harness-builder
    data/
      qa.jsonl        # eval-harness-builder (3 seed examples)
  pyproject.toml      # infra-builder
  Makefile            # infra-builder
  Dockerfile          # infra-builder
  .env.example        # infra-builder
  README.md           # docs-builder
```
