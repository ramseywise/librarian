# Debugging a Blank Screen in A2UI

You're sending `surfaceUpdate` messages but seeing a blank screen. This is one of the most common A2UI setup issues, and it almost always comes down to one of the following causes — in order of likelihood.

## Cause 1: Missing `beginRendering` message

This is the single most common reason for a blank screen.

In v0.8, `surfaceUpdate` only registers components with the client. The client does **not** start rendering until it receives a `beginRendering` message that names the root component.

Send all `surfaceUpdate` messages first, then send `beginRendering` last with the `root` field pointing to your root component's ID.

## Cause 2: The `root` ID in `beginRendering` doesn't match any component

`beginRendering.root` must exactly match one component `id` (case-sensitive). A typo here means the renderer has no entry point and shows nothing.

## Cause 3: `surfaceId` mismatch

Every message must use the identical `surfaceId` string. Mismatches cause messages to be silently ignored.

## Cause 4: Nested JSON instead of the adjacency list model

A2UI uses a flat list with ID references, not nested component trees. Children must be arrays of ID strings referencing other entries in the components list.

## Cause 5: Malformed JSON or schema validation failure

Component type names are PascalCase (`Text`, not `text`). Text values must be wrapped: `{ "literalString": "..." }` not a bare string. Run JSON schema validation to catch these.

## Cause 6: Using v0.9 messages without `"version": "v0.9"`

Every v0.9 message (`createSurface`, `updateComponents`) requires `"version": "v0.9"` at the top level, or the client won't recognize it.
