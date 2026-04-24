# Debugging a Blank Screen in A2UI

You're sending `surfaceUpdate` messages but the client shows nothing. This is one of the most common A2UI setup issues and it almost always comes down to one of a handful of root causes. Work through these in order.

---

## 1. Missing `beginRendering` — the most common cause

In v0.8, sending `surfaceUpdate` alone is not enough to make anything appear. The client waits for a `beginRendering` message before it renders anything at all. You must send this as the final message after all your component definitions, and it must specify which component is the root.

**What you need to send (in this order):**

```json
// Step 1: define your components
{
  "surfaceUpdate": {
    "surfaceId": "my-surface",
    "components": [ ... ]
  }
}

// Step 2: tell the client to start rendering
{
  "beginRendering": {
    "surfaceId": "my-surface",
    "root": "root"
  }
}
```

If you only send `surfaceUpdate` and never follow it with `beginRendering`, the surface stays blank. The `root` field must match the `id` of the top-level component you defined.

---

## 2. The `root` ID doesn't match any component ID

Even if you send `beginRendering`, if the `root` value references an ID that doesn't exist in your components list, nothing renders. Check exact casing and spelling.

---

## 3. Children reference IDs that don't exist

Every ID listed in a `children` array must have a matching component definition. If `Column` lists `["header", "body"]` but `"body"` was never defined, that slot is silently empty.

---

## 4. Wrong `surfaceId`

Every message must use the same `surfaceId`. If your client is watching `"main"` but your messages say `"my-surface"`, nothing displays.

---

## 5. v0.9 setup issues

If using v0.9: every message needs `"version": "v0.9"`, you must send `createSurface` (with a `catalogId`) first, and use `updateComponents` — not `surfaceUpdate`.

---

## 6. Schema validation failure — message silently dropped

Common mistakes: using a plain string for `text` instead of `{ "literalString": "..." }`, or nesting components directly instead of using the flat adjacency list model.

---

## Quick Checklist

- Are you sending `beginRendering` after `surfaceUpdate`? (v0.8)
- Does `root` in `beginRendering` match an `id` in your components array?
- Does every ID in every `children` array have a matching component definition?
- Does `surfaceId` match what your client is configured to display?
- If v0.9: does every message have `"version": "v0.9"` and did you send `createSurface` first?
- Does your JSON pass schema validation?

The blank screen is almost always caused by #1 (missing `beginRendering`) or #2 (mismatched root ID).
