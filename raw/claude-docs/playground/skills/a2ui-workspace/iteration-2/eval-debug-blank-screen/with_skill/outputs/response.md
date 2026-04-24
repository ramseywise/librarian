# Debugging a Blank Screen in A2UI

A blank screen after sending `surfaceUpdate` messages is one of the most common A2UI issues. Here are the most likely causes, in order of frequency.

---

## 1. Missing `beginRendering` (most common cause)

In v0.8, sending `surfaceUpdate` alone is not enough to trigger rendering. You must follow it with a `beginRendering` message that tells the client which component is the root. Until `beginRendering` arrives, the client holds all component definitions in memory but renders nothing.

**Wrong:**
```json
[
  { "surfaceUpdate": { "surfaceId": "my-surface", "components": [
    { "id": "root", "component": { "Text": { "text": { "literalString": "Hello" } } } }
  ]}}
]
```

**Correct:**
```json
[
  { "surfaceUpdate": { "surfaceId": "my-surface", "components": [
    { "id": "root", "component": { "Text": { "text": { "literalString": "Hello" } } } }
  ]}},
  { "beginRendering": { "surfaceId": "my-surface", "root": "root" } }
]
```

The `root` field in `beginRendering` must match the `id` of the component you want at the top of the tree.

---

## 2. `surfaceId` mismatch

Every message must use the exact same `surfaceId` string. A typo between messages (e.g., `"my-surface"` vs `"mySurface"`) means the client treats them as different surfaces. The surface receiving `beginRendering` has no components, so nothing renders.

---

## 3. No component is reachable from the root

If the root component's `children` references IDs that don't exist in the components list, those subtrees are silently missing. Add the missing component:

```json
{ "surfaceUpdate": { "surfaceId": "s", "components": [
  { "id": "root", "component": { "Column": { "children": ["greeting"] } } },
  { "id": "greeting", "component": { "Text": { "text": { "literalString": "Hello" } } } }
]}}
```

---

## 4. Invalid JSON or schema validation failure

If the JSON is malformed or doesn't match the A2UI schema, most clients silently discard the message. Common pitfalls: nested component trees instead of the flat adjacency list, wrong component name key structure, or using v0.9 message names (`updateComponents`) when the client expects v0.8 (`surfaceUpdate`).

---

## 5. Message ordering violation

In v0.8, all `surfaceUpdate` messages must arrive before `beginRendering`. If `beginRendering` is sent first, the client may render an empty surface and never recover.

---

## 6. `text` field missing the wrapper object

`Text` components require `{ "literalString": "..." }` or `{ "path": "..." }` — not a bare string.

**Wrong:** `"text": "Hello"`  
**Correct:** `"text": { "literalString": "Hello" }`

---

## Minimal Working Example (v0.8)

```json
[
  { "surfaceUpdate": { "surfaceId": "debug-surface", "components": [
    { "id": "root", "component": { "Column": { "children": ["msg"] } } },
    { "id": "msg", "component": { "Text": { "text": { "literalString": "If you see this, rendering works." }, "variant": "h2" } } }
  ]}},
  { "beginRendering": { "surfaceId": "debug-surface", "root": "root" } }
]
```

Start with this. If it renders, your client works and the problem is in your message structure.

---

## Quick Checklist

- `beginRendering` is sent after all `surfaceUpdate` messages
- `surfaceId` is identical in every message
- The `root` ID in `beginRendering` exists in the components list
- All `children` / `child` references point to defined IDs
- `text` fields use `{ "literalString": "..." }` not bare strings
- Message names match the protocol version your client targets
- JSON validates against the A2UI schema before sending

The single most common fix is simply adding the `beginRendering` message — start there.
