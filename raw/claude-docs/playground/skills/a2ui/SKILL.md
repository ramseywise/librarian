---
name: a2ui
description: >
  Use this skill when working with A2UI — the open-source protocol (by Google, Apache 2.0) that
  lets AI agents generate rich, interactive UIs across web, mobile, and desktop platforms via
  declarative JSON messages. Trigger whenever the user mentions A2UI, agent-generated UI,
  server-driven UI, A2UI surfaces, A2UI components, A2UI messages, rendering agent responses as
  UI, or wants to build/debug an agent that outputs structured UI JSON. Also trigger when the user
  is working on a demo that integrates A2UI with ADK, React, Angular, Flutter, or Lit renderers,
  or is writing prompts/schemas for LLM-generated interfaces.
---

# A2UI

A2UI is a declarative protocol for AI agents to generate rich, interactive UIs. Agents emit JSON
messages describing components; native clients render them using their own widget libraries.
This means **no code execution** — only data — which prevents UI injection attacks.

Official site: https://a2ui.org  
GitHub: https://github.com/google/A2UI

---

## Protocol Versions

| Version | Status | Use when |
|---------|--------|----------|
| v0.8 | Stable / production | Default — all renderers support it |
| v0.9 | Draft | You need `createSurface`, client functions, or custom catalogs |

v0.9 messages must include `"version": "v0.9"` at the top level.

---

## Core Concepts

### Surfaces
A surface is a top-level UI container identified by `surfaceId`. Multiple surfaces can exist
independently in the same client.

### Adjacency List Model
Components are a **flat list with ID references** — not a nested tree. This lets LLMs generate
components incrementally without perfect nesting in a single pass, and allows targeted updates.

```json
// ✓ Flat adjacency list (correct)
"components": [
  { "id": "root-col",  "component": { "Column": { "children": ["title", "card-1"] } } },
  { "id": "title",     "component": { "Text":   { "text": {"literalString": "Hello"}, "variant": "h2" } } },
  { "id": "card-1",    "component": { "Card":   { "child": "content" } } },
  { "id": "content",   "component": { "Text":   { "text": {"literalString": "Body text"} } } }
]
```

### Data Binding
Separate UI structure from state. Use JSON Pointer paths (RFC 6901):
- `{ "literalString": "Welcome" }` — fixed value
- `{ "path": "/user/name" }` — bound to data model

When data changes, bound components update automatically — no need to re-emit components.

---

## Message Types

### v0.8 (Stable)

**1. `surfaceUpdate`** — define or update components

```json
{
  "surfaceUpdate": {
    "surfaceId": "my-surface",
    "components": [
      {
        "id": "root",
        "component": {
          "Column": {
            "children": ["greeting"]
          }
        }
      },
      {
        "id": "greeting",
        "component": {
          "Text": {
            "text": { "literalString": "Hello, world!" },
            "variant": "h1"
          }
        }
      }
    ]
  }
}
```

**2. `beginRendering`** — signal the client to start rendering (send after initial `surfaceUpdate`)

```json
{
  "beginRendering": {
    "surfaceId": "my-surface",
    "root": "root"
  }
}
```

**3. `dataModelUpdate`** — update state (typed value wrappers in v0.8)

```json
{
  "dataModelUpdate": {
    "surfaceId": "my-surface",
    "contents": [
      { "key": "username",  "valueString":  "Alice" },
      { "key": "score",     "valueNumber":  42 },
      { "key": "active",    "valueBoolean": true }
    ]
  }
}
```

**4. `deleteSurface`** — remove a surface

```json
{ "deleteSurface": { "surfaceId": "my-surface" } }
```

**v0.8 ordering rule**: `surfaceUpdate` messages → `beginRendering` last.

---

### v0.9 (Draft)

**1. `createSurface`** — initialize surface (catalog required)

```json
{
  "version": "v0.9",
  "createSurface": {
    "surfaceId": "my-surface",
    "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json"
  }
}
```

**2. `updateComponents`** — flat format, `component` is a string, one entry must be `id: "root"`

```json
{
  "version": "v0.9",
  "updateComponents": {
    "surfaceId": "my-surface",
    "components": [
      { "id": "root", "component": "Column", "children": ["greeting"] },
      { "id": "greeting", "component": "Text", "text": { "literalString": "Hello" }, "variant": "h1" }
    ]
  }
}
```

**3. `updateDataModel`** — plain JSON values (no type wrappers)

```json
{
  "version": "v0.9",
  "updateDataModel": {
    "surfaceId": "my-surface",
    "path": "/user",
    "value": { "name": "Alice", "score": 42 }
  }
}
```

---

## Component Reference

All components share: `id` (required), `accessibility`, `weight` (flex-grow).

### Layout

| Component | Key Properties |
|-----------|----------------|
| `Column`  | `children` (array of IDs or template), `justify`, `align` |
| `Row`     | `children` (array of IDs or template), `justify`, `align` |
| `List`    | `children` / template, `direction`, `align` |

### Display

| Component | Key Properties |
|-----------|----------------|
| `Text`    | `text` (literal or path), `variant`: `h1`–`h5`, `caption`, `body` |
| `Image`   | `src`, `fit`: `cover`/`contain`, `variant` |
| `Icon`    | `name` |
| `Divider` | `axis`: `horizontal`/`vertical` |

### Interactive

| Component | Key Properties |
|-----------|----------------|
| `Button`  | `child` (component ID), `variant`: `primary`/`secondary`, `action` — **always include `action`**, it's how the client knows what to do when clicked: `{ "type": "event", "name": "myEvent" }` |
| `TextField` | `value` (DataBinding path), `type`: `shortText`/`longText`/`number`/`obscured`/`date`, `label`, `validationRegexp` |
| `CheckBox` | `label`, `value` (DataBinding path) |
| `Slider`  | `value` (path), `minValue`, `maxValue` |
| `DateTimeInput` | `enableDate`, `enableTime` |
| `MultipleChoice` (v0.8) / `ChoicePicker` (v0.9) | `options`, `selections` (path), `maxAllowedSelections` |

### Container

| Component | Key Properties |
|-----------|----------------|
| `Card`    | `child` (single component ID) |
| `Modal`   | `entryPointChild`, `contentChild` |
| `Tabs`    | `tabItems`: array of `{ title, child }` |

---

## Data Binding Patterns

### Literal vs Bound
```json
"text": { "literalString": "Static label" }
"text": { "path": "/product/name" }
```

### Dynamic List (template binds to array)
```json
{
  "id": "product-list",
  "component": {
    "List": {
      "dataBinding": "/products",
      "children": {
        "template": "product-card"
      }
    }
  }
}
```
Inside template, paths are scoped to each array item: `/name` → `/products/0/name`.

### Input Binding (bidirectional)
```json
{
  "id": "search-box",
  "component": {
    "TextField": {
      "value": { "path": "/search/query" },
      "type": "shortText",
      "label": { "literalString": "Search" }
    }
  }
}
```

---

## Agent Development (ADK + A2UI)

### Setup
```bash
pip install google-adk
adk create my_agent
```

### Prompt Pattern

Tell the LLM to separate conversational text from A2UI JSON with a delimiter:

```python
A2UI_INSTRUCTION = """
Your final output MUST be an A2UI UI JSON response.

Rules:
1. Separate conversational text and JSON with: ---a2ui_JSON---
2. First part: your conversational response
3. Second part: a single JSON array of A2UI messages
4. JSON MUST validate against the A2UI schema

{A2UI_SCHEMA}
"""
```

### Parse and validate
```python
import json, jsonschema

def parse_a2ui_response(llm_output: str, schema: dict) -> list:
    delimiter = "---a2ui_JSON---"
    if delimiter in llm_output:
        _, json_part = llm_output.split(delimiter, 1)
    else:
        json_part = llm_output
    messages = json.loads(json_part.strip())
    jsonschema.validate(instance=messages, schema=schema)
    return messages
```

### Full Agent Example
```python
from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
import json

def get_restaurants(tool_context: ToolContext) -> str:
    """Return a list of restaurants."""
    return json.dumps([
        {"name": "Xi'an Famous Foods", "rating": "★★★★☆",
         "detail": "Spicy hand-pulled noodles.", "address": "81 St Marks Pl, NY"}
    ])

root_agent = Agent(
    model="gemini-2.5-flash",
    name="restaurant_agent",
    description="Finds restaurants and renders rich UI.",
    instruction=A2UI_INSTRUCTION,
    tools=[get_restaurants],
)
```

### Get the A2UI schema
Copy `a2ui_schema.py` from the contact lookup sample in the A2UI repo:
`samples/agent/a2ui-over-a2a/contact_lookup/a2ui_schema.py`

---

## Client Setup

### React
```bash
npm install @a2ui/react @a2ui/web-lib
```
Use `<A2UISurface>` component and `useA2UI()` hook.

### Angular
```bash
npm install @a2ui/angular @a2ui/web_core
```
Configure providers with `A2UI_RENDERER_CONFIG`; use `<a2ui-v09-component-host>`.

### Lit
```bash
npm install @a2ui/web-lib lit @lit-labs/signals
```
Use `<a2ui-surface>` with Lit Signals.

### Flutter
```bash
flutter pub add flutter_genui
```
Integrates via the GenUI SDK for native rendering.

---

## Quickstart (Restaurant Demo)

```bash
git clone https://github.com/google/a2ui.git
cd a2ui
export GEMINI_API_KEY="your_key"
cd samples/client/lit
npm install
npm run demo:all
# Opens at http://localhost:5173
```

Test prompts: "Book a table for 2", "Find Italian restaurants near me"

---

## Key Design Rules

1. **Flat components, not nested JSON** — use the adjacency list model
2. **Send `beginRendering` last** (v0.8) — component definitions must precede it
3. **Validate before transmitting** — always run JSON schema validation
4. **Data and structure are separate** — use `dataModelUpdate` for state changes, not new `surfaceUpdate` messages
5. **Use granular data updates** — only update the paths that changed
6. **Agents pick the catalog** — clients advertise supported catalogs; agents select the best match

## Responding to Debugging Questions

When someone reports a blank screen or rendering issue, always include a minimal JSON example alongside the explanation — showing the correct message sequence is more useful than prose alone. The most common cause is a missing `beginRendering` after `surfaceUpdate`; show it fixed:

```json
[
  { "surfaceUpdate": { "surfaceId": "s", "components": [
    { "id": "root", "component": { "Text": { "text": { "literalString": "Hello" } } } }
  ]}},
  { "beginRendering": { "surfaceId": "s", "root": "root" } }
]
```

---

## Deeper Reference

- Protocol spec v0.8: https://a2ui.org/specification/v0.8-a2ui/
- Protocol spec v0.9: https://a2ui.org/specification/v0.9-a2ui/
- Component gallery: https://a2ui.org/reference/components/
- Message reference: https://a2ui.org/reference/messages/
- Agent dev guide: https://a2ui.org/guides/agent-development/
- Client setup: https://a2ui.org/guides/client-setup/
