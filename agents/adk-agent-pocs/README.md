# ADK Agent Samples

A repository of reference implementations for the **Agent Development Kit (ADK)**. Each sample demonstrates a specific pattern — from minimal environment verification to a fully safety-hardened, domain-restricted agent.

## Repository Structure

```text
agents/          # Standalone agent definitions (prompts, callbacks, tests)
mcp_servers/     # FastMCP servers exposing tool stubs (e.g. Billy accounting)
agent_gateway/   # FastAPI server that runs ADK agents and parses A2UI responses
shared/          # Reusable guardrail and tool modules shared across agents
scripts/         # Convenience launchers for each agent and supporting services
web_client/      # Custom chat UI — text streaming + live voice (see below)
```

## Agents

### `hello_world` — Minimal baseline

A bare-minimum agent used to verify environment setup and confirm the ADK installation is working. No guardrails, no tools.

```bash
bash scripts/run_hello.sh
```

---

### [`wine_expert`](agents/wine_expert/README.md) — Safety & domain-restriction reference

The primary reference implementation for testing the full ADK safety stack. It demonstrates:

- **Multi-layer domain enforcement** — a strict system prompt ("Vineyard Walls") backed by a deterministic keyword classifier, so both must be defeated simultaneously to get an off-topic response
- **`WineGuardrailsPlugin`** — an ADK `BasePlugin` that runs a 7-stage pre-LLM pipeline on every user message: normalisation → size check → domain classification → injection detection → PII redaction → session envelope → XML advisory notes
- **`before_agent_callback`** — reads plugin-set flags and optionally short-circuits the LLM entirely (`HARD_REFUSE` mode)
- **`after_model_callback`** — validates grounding sources returned by Google Search; logs and flags untrusted domains
- **Google Search grounding** — real-time vintage, producer, and market data via the `google_search` tool
- **Regression tests** — `tests/test_policy.py` covers domain allow/refuse, injection detection, and oversize truncation without any LLM calls

See the [Wine Expert README](agents/wine_expert/README.md) for architecture diagrams, pipeline detail, session state schema, and test documentation.

```bash
bash scripts/run_wine.sh
```

---

### [`wine_expert_multi_agent`](agents/wine_expert_multi_agent/README.md) — Supervisor + specialist multi-agent orchestration

Extends the Wine Expert into a **multi-agent system** where a supervisor agent delegates every request to a team of four specialised experts via `AgentTool`. It demonstrates:

- **Supervisor / specialist pattern** — the root `supervisor_agent` never answers from its own knowledge; it always delegates to the appropriate expert
- **Parallel expert calls** — compound questions (e.g. "recommend a wine, suggest food pairings, and explain how it's made") trigger simultaneous calls to `food_pairing_expert` and `wine_knowledge_expert` after an initial sequential call to `recommendation_expert`
- **Typed I/O contracts** — each sub-agent has a Pydantic `input_schema` and a validated structured `output_key`; the supervisor must pass correct fields and can read results from session state
- **Shared safety stack** — reuses `WineGuardrailsPlugin` and `before_agent_callback` from `wine_expert` unchanged

See the [Wine Expert Multi-Agent README](agents/wine_expert_multi_agent/README.md) for the full architecture diagram, orchestration flow, parallel-call walkthrough, and I/O schema reference.

```bash
bash scripts/run_wine_multi.sh
```

---

### [`a2ui_mcp`](agents/a2ui_mcp/README.md) — A2UI accounting assistant

A Billy accounting assistant that renders responses as interactive UI surfaces using the [A2UI protocol](https://a2ui.org). Demonstrates:

- **Lazy skill loading** — domain tools (invoices, customers, products, analytics) are loaded on demand via `load_skill`, keeping each turn's tool registry small
- **A2UI output** — after each response the agent appends `---a2ui_JSON---` followed by A2UI v0.9 messages; the `agent_gateway` parses these and streams them to the React frontend
- **Self-fetching panels** — financial insight panels (revenue, aging, top customers) fetch their own data directly from the Billy REST API — no numbers pass through the agent
- **UI event round-trips** — clicking Edit/Save in the rendered surface fires a `[ui_event]` back to the agent, which acts without re-asking

Requires four services (see [Quick Start](#quick-start) below).

See the [a2ui_mcp README](agents/a2ui_mcp/README.md) for the full architecture diagram, skill list, and A2UI message walkthrough.

```bash
bash scripts/run_mcp_billy.sh       # Terminal 1 — Billy MCP server  (port 8765)
bash scripts/run_billy_api.sh       # Terminal 2 — Billy REST API     (port 8766)
bash scripts/run_agent_gateway.sh   # Terminal 3 — Agent gateway      (port 8000)
bash scripts/run_a2ui_web_client.sh # Terminal 4 — A2UI web client    (port 5173)
# Open http://localhost:5173
```

---

## Shared Guardrails

Located in `shared/guardrails/`, these modules are pure functions (no I/O, no side effects) reusable by any agent:

| Module                | Function                     | What it does                                                           |
|-----------------------|------------------------------|------------------------------------------------------------------------|
| `domain_wine.py`      | `is_wine_related(text)`      | Keyword + regex domain classifier for wine topics                      |
| `pii_redaction.py`    | `detect_and_redact(text)`    | Replaces emails, phones, cards, SSNs, API keys, PEM blocks with tokens |
| `prompt_injection.py` | `looks_like_injection(text)` | Regex heuristics for instruction-override and jailbreak patterns       |

## Quick Start

1. **Set up environment**

```bash
cp .env.example .env
# Add your GOOGLE_API_KEY (and optionally GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION) to .env
```

1. **Install dependencies**

```bash
uv sync
```

1. **Start the Billy MCP server** *(required for `dynamic_skill_mcp`, `skill_assistant_mcp`, and `a2ui_mcp`)*

```bash
bash scripts/run_mcp_billy.sh
# Listens on http://127.0.0.1:8765/sse  — leave this terminal running
```

1. **Launch the web chat client** *(text + voice — for all non-A2UI agents)*

```bash
bash scripts/run_web_client.sh
# Open http://localhost:3000 in your browser
```

Select any agent from the dropdown. Agents that use a live model (e.g. `dynamic_skill_mcp`) show a **LIVE** badge and a microphone button — click it to speak; transcriptions and audio responses appear inline.

> **Voice note:** the browser will ask for microphone permission on first use. Serve over HTTPS (or use `localhost`) to allow `AudioContext` to start.

1. **Run the `a2ui_mcp` agent with its interactive UI** *(requires four services)*

Open four terminals from the repo root:

```bash
bash scripts/run_mcp_billy.sh       # Terminal 1 — Billy MCP server  (port 8765)
bash scripts/run_billy_api.sh       # Terminal 2 — Billy REST API     (port 8766)
bash scripts/run_agent_gateway.sh   # Terminal 3 — Agent gateway      (port 8000)
bash scripts/run_a2ui_web_client.sh # Terminal 4 — A2UI web client    (port 5173)
```

- **`run_billy_api.sh`** starts the Billy stub REST API (docs at `http://127.0.0.1:8766/docs`). The A2UI insight panels fetch data directly from this server — they bypass the agent entirely.
- **`run_agent_gateway.sh`** runs the FastAPI server that hosts ADK agent sessions, parses `---a2ui_JSON---` output, and streams text and A2UI events to the frontend over SSE.
- **`run_a2ui_web_client.sh`** starts the Vite/React frontend (`npm install` is run automatically on first use).

Open <http://localhost:5173> in your browser and try prompts like `list customers`, `create an invoice for Acme A/S`, or `show me the revenue overview`.

1. **Or use the ADK built-in dev UI** *(all agents, text only)*

```bash
bash scripts/run_web.sh         # all agents on http://localhost:8000
bash scripts/run_wine.sh        # wine_expert only
bash scripts/run_wine_multi.sh  # wine_expert_multi_agent only
bash scripts/run_hello.sh       # hello_world only
```

1. **Run tests**

```bash
pytest agents/wine_expert/tests/ -v
```

1. **Update ADK Project Skills**

Follow the ADK project skills tutorial at
<https://google.github.io/adk-docs/tutorials/coding-with-ai/>

Refresh the skills files copied into this repository:

```bash
npx skills add google/adk-docs/skills -y
cp -R .claude/skills .github
```

Update the local ADK documentation snapshots:

```bash
mkdir -p .docs/adk
curl -fsSL https://google.github.io/adk-docs/llms.txt -o .docs/adk/llms.txt
curl -fsSL https://google.github.io/adk-docs/llms-full.txt -o .docs/adk/llms-full.txt
```


## AWS Bedrock RAG Access

Some agents use a **Retrieval-Augmented Generation (RAG)** pipeline backed by an AWS Bedrock Knowledge Base. Accessing this requires an active AWS SSO session in the correct account.

| Field      | Value                                   |
|------------|-----------------------------------------|
| Account    | Machine Learning Development            |
| Account ID | `980921737304`                          |
| Email      | `aws-management+ml-training@ageras.com` |

### 1. One-time profile setup

Add the following to `~/.aws/config` (run `aws configure sso` or edit the file directly):

```ini
[profile default]
sso_session = MLDeveloperAccess
sso_account_id = 980921737304
sso_role_name = MLDeveloperAccess
region = eu-west-1
output = json

[sso-session default]
sso_start_url = https://ageras.awsapps.com/start
sso_region = eu-west-1
sso_registration_scopes = sso:account:access
```

### 2. Login before running any Bedrock-backed agent

```bash
aws sso login --sso-session default
```

If the session expires mid-run you will get `ExpiredTokenException` errors — re-run the command above to refresh.
