# Web Client

A browser-based chat interface for ADK agents. Supports both text chat (streaming SSE) and live voice chat (bidirectional WebSocket) with real-time audio, transcriptions, tool call visibility, and response timing.

## Setup

**1. Install dependencies** (from the repo root):

```bash
uv sync
```

**2. Configure environment variables** — create a `.env` file in the repo root:

```env
GOOGLE_API_KEY=your_key_here
# Optional for Vertex AI / context caching:
# GOOGLE_CLOUD_PROJECT=your_project
# GOOGLE_CLOUD_LOCATION=us-central1
```

**3. Start the server** (from the repo root):

```bash
python web_client/server.py
```

**4. Open in browser:**

```
http://localhost:3000
```

> **Note:** Use `localhost`, not `127.0.0.1` or your machine's IP. Browsers only grant microphone access to `localhost` or HTTPS origins.

---

## Configuration

Edit [`config.json`](config.json) to control which agents appear in the UI, which is selected by default, and which are pre-loaded at server startup to reduce first-request latency.

```json
{
  "excluded_agents": ["hello_world", "wine_expert"],
  "default_agent": "native_skill_mcp",
  "warmup": {
    "agents": ["live_mcp", "native_skill_mcp"],
    "cache_warmup_agents": []
  }
}
```

---

### `excluded_agents`

A list of agent directory names to hide from the dropdown. The server discovers every folder under `agents/` that contains an `agent.py` — this list lets you suppress agents you don't want to expose without deleting them.

```json
"excluded_agents": ["hello_world", "wine_expert", "dynamic_skill_mcp"]
```

Use the exact directory name (e.g. `agents/hello_world` → `"hello_world"`).

---

### `default_agent`

The agent that is pre-selected when the page loads. If the agent is found in the dropdown the UI connects to it automatically — the user can start chatting immediately without picking an agent.

```json
"default_agent": "native_skill_mcp"
```

Set to `null` or remove the field to show the empty *"Select an agent…"* placeholder instead.

---

### `warmup`

Controls which agents are pre-loaded when the server starts. Without warmup, the first user request pays the cold-start cost: importing the Python module, building the system prompt, connecting to the MCP server, and fetching all tool schemas. Warmup moves that cost to server startup so users never see it.

#### `warmup.agents`

Agents to load at startup. For each agent listed the server will:

1. Import the agent module and build the system prompt
2. Connect to the MCP server (starts the stdio subprocess)
3. Fetch all tool schemas from the MCP server
4. Create and cache the ADK `Runner`

**Cost:** Free — no Gemini API calls are made.
**Benefit:** Removes 1–3 seconds of cold-start latency from the first user request.

```json
"agents": ["live_mcp", "native_skill_mcp"]
```

#### `warmup.cache_warmup_agents`

Agents to prime with a real (but trivial) API call at startup. After loading the agent, the server sends a dummy `"hi"` message through the runner. This causes Gemini to process the full system prompt and store it in the **context cache** — so the first real user turn gets a cache hit instead of paying full input token cost for the system prompt.

**Cost:** Tokens equal to roughly the system prompt size, charged once per server restart.
**Benefit:** For agents with large system prompts (e.g. `live_mcp` has all 6 skill blocks preloaded), this can meaningfully reduce per-turn cost and first-turn latency.
**Recommendation:** Enable in production. Leave empty in development to avoid paying token costs on every restart.

```json
"cache_warmup_agents": ["live_mcp"]
```

---

## Features

### Agent selector

The dropdown is populated from the `/agents` endpoint, which scans the `agents/` directory automatically. Each agent shows a 🎙 badge if it uses a live (BIDI streaming) model.

Agent detection rules:
- **Live agent** — `agent.py` contains an uncommented line matching `gemini-*live*`
- **Audio-only** — model matches `gemini-*live*preview`; text input is disabled and the textarea shows *"Voice only — use the microphone"*

### Text chat

For non-live agents. Messages are streamed token by token via SSE. Supports full GFM markdown rendering including tables, code blocks, and bold/italic.

### Live voice chat

For live agents. Audio is captured from the microphone (16 kHz PCM), streamed to the server as binary WebSocket frames, and forwarded to the Gemini Live API. The model's audio response (24 kHz PCM) is streamed back and played through the browser's Web Audio API.

Both user and model speech appear as transcription bubbles in the chat. The text transcript of the model's response is rendered as a markdown message bubble when the turn completes.

### Tool call display

Every tool call and response is shown as a numbered step row below the agent bubble:

- `⚡ tool_name` — call in progress
- `✓ tool_name` — response received

Hover a row to see the full JSON arguments or response in a tooltip.

Use the **Tools** button in the toolbar to show or hide all tool rows.

### Response timing

Click the ⏱ badge below any agent message to expand the timing panel:

- **First token / First word** — latency to first streamed token (text) or first audio chunk (voice), measured from the last processing milestone
- **LLM** spans — time spent in each model call
- **Tool** spans — time spent executing each tool call

For voice turns with tool calls the first word label shows `Xs + Ys` — time before the final LLM call started plus time from that LLM call to first audio.

---

## Agent discovery

The server scans `agents/` at each `/agents` request and returns all directories that:

1. Are not in `excluded_agents`
2. Are not named `__pycache__` or `shared`
3. Do not start with `_`
4. Contain an `agent.py` file

To add a new agent, create `agents/my_agent/agent.py` with a `root_agent` variable. It will appear in the dropdown automatically.

---

## WebSocket protocol (live agents)

**Browser → Server**

| Frame | Content |
|-------|---------|
| Binary | Raw PCM audio — 16-bit signed, 16 kHz, mono |
| Text | `{"type": "text", "content": "..."}` — typed message |
| Text | `{"type": "close"}` — end session |

**Server → Browser**

| Frame | Content |
|-------|---------|
| Binary | Raw PCM audio — 16-bit signed, 24 kHz, mono |
| Text | `{"type": "transcription", "role": "user"\|"model", "content": "...", "finished": bool}` |
| Text | `{"type": "text", "content": "...", "partial": bool}` |
| Text | `{"type": "tool_calls", "calls": [...]}` |
| Text | `{"type": "tool_responses", "responses": [...]}` |
| Text | `{"type": "turn_complete"}` |
| Text | `{"type": "error", "content": "..."}` |
