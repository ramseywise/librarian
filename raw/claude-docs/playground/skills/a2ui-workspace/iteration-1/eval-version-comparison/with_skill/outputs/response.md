# A2UI v0.8 vs v0.9: Version Comparison

## Overview

| Version | Status | Primary Use Case |
|---------|--------|-----------------|
| v0.8 | Stable / production | Default — all renderers support it |
| v0.9 | Draft | Needed for `createSurface`, client functions, or custom catalogs |

---

## Key Differences

### 1. Surface Initialization

**v0.8** has no explicit surface creation step. You begin directly with `surfaceUpdate` messages, then signal rendering with `beginRendering`.

**v0.9** introduces a dedicated `createSurface` message that must come first, and requires specifying a `catalogId`. Every v0.9 message must also include `"version": "v0.9"` at the top level.

### 2. Message Names

| Concept | v0.8 | v0.9 |
|---------|------|------|
| Define components | `surfaceUpdate` | `updateComponents` |
| Update state | `dataModelUpdate` | `updateDataModel` |
| Start rendering | `beginRendering` | (implicit after `createSurface`) |
| Remove surface | `deleteSurface` | (not yet documented) |

### 3. Component Format

**v0.8** wraps the component type in a nested object:
```json
{ "id": "greeting", "component": { "Text": { "text": { "literalString": "Hello" } } } }
```

**v0.9** flattens it — `component` is a plain string, and properties sit at the same level:
```json
{ "id": "greeting", "component": "Text", "text": { "literalString": "Hello" }, "variant": "h1" }
```

### 4. Data Model Updates

**v0.8** uses typed value wrappers in a flat `contents` array:
```json
"contents": [
  { "key": "username", "valueString": "Alice" },
  { "key": "score",    "valueNumber": 42 }
]
```

**v0.9** uses plain JSON values with a `path` pointer (RFC 6901):
```json
{ "path": "/user", "value": { "name": "Alice", "score": 42 } }
```

### 5. Component Renames

| v0.8 | v0.9 |
|------|------|
| `MultipleChoice` | `ChoicePicker` |

All other core components are unchanged.

---

## Which Should You Use for a New Project?

**Use v0.8.**

- **Universal renderer support** — React, Angular, Lit, and Flutter all fully support v0.8. v0.9 support is incomplete.
- **Production stability** — v0.8 is the stable release. v0.9 is a draft, subject to breaking changes.
- **Better ecosystem** — documentation, samples, and community answers all center on v0.8.
- **Clear upgrade path** — core concepts (adjacency list model, data binding, flat component lists) are identical in both versions. Migration when v0.9 stabilizes is a message-format change, not an architectural one.

Only choose v0.9 if you specifically need `createSurface` with custom catalog IDs or the flatter component syntax, and you have confirmed your renderer supports it.

---

## Hello World — v0.8

Two messages: `surfaceUpdate` to define components, then `beginRendering` to start rendering. `beginRendering` must come last.

```json
[
  {
    "surfaceUpdate": {
      "surfaceId": "hello-surface",
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

---

## Hello World — v0.9

Two messages: `createSurface` to initialize, then `updateComponents` to define the tree. Every message requires `"version": "v0.9"`. One component must have `id: "root"`.

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

---

## Summary Table

| Aspect | v0.8 | v0.9 |
|--------|------|------|
| Status | Stable | Draft |
| Version field required | No | Yes (`"version": "v0.9"` on every message) |
| Surface init | Implicit | Explicit `createSurface` + `catalogId` |
| Render trigger | Explicit `beginRendering` | Implicit (root id in `updateComponents`) |
| Component format | Nested `{ "Type": { ...props } }` | Flat `"component": "Type"`, props at same level |
| Data updates | Typed wrappers (`valueString`, etc.) | Plain JSON via `path` |
| Renderer support | All | Partial |
| **Recommended for new projects** | **Yes** | No |
