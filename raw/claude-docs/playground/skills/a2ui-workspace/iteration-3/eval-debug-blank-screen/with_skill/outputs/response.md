# Debugging a Blank Screen in A2UI

A blank screen when sending `surfaceUpdate` messages is one of the most common A2UI setup issues. Here are the most likely causes, in order of frequency.

---

## 1. Missing `beginRendering` (most common cause)

In v0.8, sending `surfaceUpdate` alone is not enough. You must follow it with `beginRendering` — this is the signal that tells the client to start rendering and which component is the root.

**Broken sequence:**
```json
[
  { "surfaceUpdate": { "surfaceId": "my-surface", "components": [
    { "id": "root", "component": { "Text": { "text": { "literalString": "Hello" } } } }
  ]}}
]
```

**Fixed sequence:**
```json
[
  { "surfaceUpdate": { "surfaceId": "my-surface", "components": [
    { "id": "root", "component": { "Text": { "text": { "literalString": "Hello" } } } }
  ]}},
  { "beginRendering": { "surfaceId": "my-surface", "root": "root" } }
]
```

The `root` field in `beginRendering` must match an `id` in your component list. If it doesn't exist, nothing renders.

---

## 2. Wrong message ordering

All `surfaceUpdate` messages must arrive before `beginRendering`. If the render signal arrives first, the client has no components to work with.

---

## 3. `surfaceId` mismatch

The `surfaceId` in `surfaceUpdate` and `beginRendering` must be identical strings (case-sensitive). A mismatch means the client sees two separate, incomplete surfaces.

---

## 4. Root component ID not in the component list

`beginRendering.root` must reference an `id` that actually exists in your components array. A typo here gives the renderer no entry point.

---

## 5. Nested JSON instead of the adjacency list model

Components must be a flat list with ID references — not a nested tree. Children are referenced by string ID only.

**Wrong (nested):**
```json
"components": [
  { "id": "root", "component": {
    "Column": {
      "children": [
        { "id": "title", "component": { "Text": { "text": { "literalString": "Hello" } } } }
      ]
    }
  }}
]
```

**Correct (flat):**
```json
"components": [
  { "id": "root",  "component": { "Column": { "children": ["title"] } } },
  { "id": "title", "component": { "Text":   { "text": { "literalString": "Hello" } } } }
]
```

---

## 6. Invalid JSON / schema validation failure

Many clients silently ignore malformed messages. Run schema validation before transmitting to catch these issues early.

---

## 7. Using v0.9 messages without `"version": "v0.9"`

Every v0.9 message (`createSurface`, `updateComponents`) requires `"version": "v0.9"` at the top level or the client may ignore it.

---

## Quick Checklist

- [ ] Sending `beginRendering` after `surfaceUpdate`? (v0.8)
- [ ] Does `beginRendering.root` match an existing component `id`?
- [ ] Same `surfaceId` in both messages?
- [ ] Components are a flat adjacency list, not nested?
- [ ] JSON passes schema validation?
- [ ] Using v0.9 messages? Is `"version": "v0.9"` in every message?
