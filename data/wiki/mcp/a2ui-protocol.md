---
title: A2UI Protocol
tags: [mcp, concept]
summary: A2UI is the agent-to-user interface protocol in which agents emit declarative JSON messages (a flat adjacency list of components plus a JSON-Pointer data model) that native clients render with their own widgets; it is data only, never code, and the classic bug is a blank screen from a missing beginRendering.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/a2ui/SKILL.md
  - data/raw/claude-docs/playground/skills/a2ui-workspace/iteration-2/eval-debug-blank-screen/with_skill/outputs/response.md
---

# A2UI Protocol

A2UI (Agent-to-User Interface) is the open, Apache-2.0 generative-UI layer of the
[[Agent Interoperability Protocol Stack]]. An agent emits JSON messages that describe
components. Each client (React, Angular, Lit, Flutter) renders them with its own native
widget library. Compiled from the playground repo's `a2ui` skill and a with-skill eval
response on debugging a blank screen.

## Design choices that matter

- **Data, not code.** Messages only describe UI and never execute anything, which rules
  out UI injection. Validate every message against the JSON schema before you send it,
  because most clients silently drop invalid messages.
- **Flat adjacency list, not a nested tree.** Components form a flat list, and parents
  refer to children by ID (`"children": ["title", "card-1"]`). This shape is built for
  LLM generation. The model can emit components incrementally without getting the nesting
  right in one pass, and a later message can update a single component by ID.
- **Structure separate from state.** Values are either `{ "literalString": ... }` or a
  JSON Pointer binding (`{ "path": "/user/name" }`, RFC 6901). A state change is a data
  model update, not a re-emitted component. Bound components refresh on their own, and
  updates should touch only the changed paths. List templates scope paths to each array
  item (`/name` resolves to `/products/0/name`). Input fields bind both ways.
- **Agents pick the catalog.** Clients advertise the component catalogs they support, and
  the agent chooses the best match.
- **Button needs an `action`** (`{ "type": "event", "name": ... }`). Without one, the
  client has no idea what a click should do.

## Versions and message types

| Version | Status | Messages |
|---|---|---|
| v0.8 | Stable, supported by every renderer | `surfaceUpdate`, `beginRendering`, `dataModelUpdate` (typed `valueString`/`valueNumber` wrappers), `deleteSurface` |
| v0.9 | Draft, needs `"version": "v0.9"` | `createSurface` (catalog required), `updateComponents` (`component` is a string, one entry has `id: "root"`), `updateDataModel` (plain JSON at a path) |

A **surface** (`surfaceId`) is a top-level container. Several surfaces can live in one
client independently of each other.

## The blank-screen failure ladder (v0.8)

These are the causes in order of frequency:

1. **Missing `beginRendering`.** The client holds the components in memory and renders
   nothing until a `beginRendering` names the root ID. This is the most common cause.
2. **`surfaceId` mismatch** between messages, for example `my-surface` vs `mySurface`.
   The client ends up with a surface that has a root and no components.
3. **Unreachable children.** The root references IDs that were never defined, and those
   subtrees go missing without any error.
4. **Schema-invalid JSON** is silently discarded. Typical causes are nested trees, or v0.9
   message names sent to a v0.8 client.
5. **Ordering.** `beginRendering` arrives before the `surfaceUpdate`s and the surface
   never recovers.
6. **Bare strings.** `"text": "Hello"` instead of `{ "literalString": "Hello" }`.

When answering a debugging question, show the fixed message sequence as a minimal JSON
example. The sequence is more useful than prose.

## Agent-side wiring

Tell the model to put conversational text first and the JSON array second, separated by
a delimiter (`---a2ui_JSON---`). Split on the delimiter, `json.loads` the second part and
run `jsonschema.validate` before transmitting. In ADK this is just an `instruction` string
plus ordinary tools that return data.

Without a skill the model **hallucinates a fake schema**: nested `children` trees,
`"type": "card"` shorthand and `bind` fields, none of which exist in the protocol.
[[ADK Context Engineering]] records the benchmark, where one SKILL.md added 78pp across
three iterations.

## See Also
- [[Agent Interoperability Protocol Stack]] — related (part of; A2UI is the agent-to-human layer)
- [[A2A Agent Protocol]] — related (the agent-to-agent transport A2UI samples ride over)
- [[Multi-Agent Orchestration Patterns]] — instance-of (an A2UI MCP layer in a working system)
- [[ADK Context Engineering]] — extends (the skill benchmark showing what the protocol knowledge is worth)
- [[SKILL.md Pattern]] — instance-of (the skill that taught the schema)
