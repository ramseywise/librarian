# A2UI v0.8 vs v0.9: Version Comparison

## Overview

A2UI is an open-source protocol (by Google, Apache 2.0) that lets AI agents generate rich, interactive UIs across web, mobile, and desktop platforms via declarative JSON messages. Two protocol versions exist:

| Version | Status | Summary |
|---------|--------|---------|
| v0.8 | Stable / production | The mature, broadly supported baseline |
| v0.9 | Draft | Adds new primitives; not yet universally supported |

---

## Key Differences Between v0.8 and v0.9

### 1. Surface Initialization

**v0.8** has no surface initialization message. You begin directly with `surfaceUpdate` to define components, then send `beginRendering` to trigger rendering. The ordering rule is strict: all `surfaceUpdate` messages must precede `beginRendering`.

**v0.9** introduces `createSurface`, a dedicated initialization message that requires a `catalogId`. This makes the component catalog explicit and machine-readable, enabling custom or third-party catalogs.

### 2. Message Names

| Purpose | v0.8 | v0.9 |
|---------|------|------|
| Initialize surface | *(none — use surfaceUpdate)* | `createSurface` |
| Define/update components | `surfaceUpdate` | `updateComponents` |
| Update data/state | `dataModelUpdate` | `updateDataModel` |
| Remove surface | `deleteSurface` | *(same)* |

### 3. Component Format

**v0.8** wraps the component type in a nested object keyed by component name:
```json
{ "id": "greeting", "component": { "Text": { "text": {...}, "variant": "h1" } } }
```

**v0.9** flattens the component — the type is a plain string and properties live at the top level of the entry:
```json
{ "id": "greeting", "component": "Text", "text": {...}, "variant": "h1" }
```

The v0.9 root component must have `"id": "root"` — there is no separate `beginRendering` step.

### 4. Data Model Updates

**v0.8** uses typed value wrappers with explicit keys per entry:
```json
"contents": [
  { "key": "username", "valueString": "Alice" },
  { "key": "score",    "valueNumber": 42 }
]
```

**v0.9** uses plain JSON values with a single `path` and `value`:
```json
{ "path": "/user", "value": { "name": "Alice", "score": 42 } }
```

### 5. Version Field

v0.9 messages **must** include `"version": "v0.9"` at the top level of every message. v0.8 has no version field.

### 6. Component Naming Changes

`MultipleChoice` (v0.8) is renamed to `ChoicePicker` (v0.9).

---

## Which Should You Use for a New Project?

**Use v0.8.** It is stable and production-ready, with universal renderer support across React, Angular, Lit, and Flutter. v0.9 is still a draft — renderer support is partial and the spec may change before stabilizing.

Consider v0.9 only if you specifically need `createSurface` with explicit catalog negotiation, client functions, or the flatter component format. Otherwise, start with v0.8 and plan a migration once v0.9 stabilizes.

---

## Hello World Text Surface: v0.8

```json
[
  {
    "surfaceUpdate": {
      "surfaceId": "hello-surface",
      "components": [
        {
          "id": "root",
          "component": {
            "Column": { "children": ["greeting"] }
          }
        },
        {
          "id": "greeting",
          "component": {
            "Text": {
              "text": { "literalString": "Hello, World!" },
              "variant": "h1"
            }
          }
        }
      ]
    }
  },
  {
    "beginRendering": {
      "surfaceId": "hello-surface",
      "root": "root"
    }
  }
]
```

Two messages required: `surfaceUpdate` (component definitions) then `beginRendering` (start render). Component type is a nested object key. No `version` field.

---

## Hello World Text Surface: v0.9

```json
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "hello-surface",
      "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json"
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "hello-surface",
      "components": [
        {
          "id": "root",
          "component": "Column",
          "children": ["greeting"]
        },
        {
          "id": "greeting",
          "component": "Text",
          "text": { "literalString": "Hello, World!" },
          "variant": "h1"
        }
      ]
    }
  }
]
```

`createSurface` replaces the implicit init; `updateComponents` replaces `surfaceUpdate`; component type is a plain string with properties flattened. `"version": "v0.9"` required on every message. No `beginRendering` — root is identified by `"id": "root"`.

---

## Side-by-Side Summary

| Aspect | v0.8 | v0.9 |
|--------|------|------|
| Status | Stable | Draft |
| Renderer support | Universal | Partial |
| Surface init | Implicit (first `surfaceUpdate`) | Explicit `createSurface` + `catalogId` |
| Render trigger | `beginRendering` message | Implicit (root id in `updateComponents`) |
| Component format | `"component": { "TypeName": { ...props } }` | `"component": "TypeName", ...props` |
| Data updates | Typed wrappers (`valueString`, `valueNumber`) | Plain JSON values with path |
| Version field | None | `"version": "v0.9"` on every message |
| Best for | Production projects today | Experimental / catalog-driven projects |

**Recommendation: Use v0.8 for new projects.**
