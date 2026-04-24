# Debugging a Blank Screen in A2UI

If you're sending `surfaceUpdate` messages but seeing a blank screen, here are the most common causes to investigate:

## 1. Incorrect Message Structure

The `surfaceUpdate` message must follow the exact schema A2UI expects. A common mistake is nesting components incorrectly or omitting required fields. Check that:
- The top-level `type` field is exactly `"surfaceUpdate"` (case-sensitive)
- The `surface` key exists and is an object
- The `components` array is present and non-empty

## 2. Empty or Missing Components Array

If you send a `surfaceUpdate` with an empty `components` array, or if `components` is null or missing, the client will render a blank surface. Make sure your components array actually contains populated elements.

## 3. Message Not Being Received by the Client

The client may never be receiving your message. Possible reasons:
- The WebSocket or SSE connection was not established before you sent the message
- The message was sent on the wrong channel or to the wrong session ID
- A serialization error caused the message to be dropped silently

Add logging on both sides to confirm the raw message actually arrives at the client before assuming the rendering logic is the problem.

## 4. Unsupported or Misspelled Component Types

If a component's `type` field is not recognized by the client, it may silently skip that component. Common mistakes:
- Wrong casing (e.g., `"Text"` instead of `"text"`)
- Using a component type not supported in the version of A2UI you're running
- Typos in component type names

## 5. Missing Required Fields on Components

Each component type has required fields. If a required field is absent, the client may skip rendering that component entirely. Review the schema for each component type you're using and confirm all required fields are present and correctly named.

## 6. Session or Surface ID Mismatch

A2UI routes surface updates to specific sessions or surfaces by ID. If the ID in your message doesn't match what the client is subscribed to, the update goes to the wrong (or no) surface. Verify you're including the correct `sessionId` or `surfaceId` and that the client is subscribed to that ID.

## 7. Rendering Gated on an Initial Handshake

Some A2UI implementations require the agent to complete a handshake before the client will render anything. If a required setup message (like `agentReady` or `sessionStart`) was never sent, the client may be waiting indefinitely. Review the protocol sequence and confirm all required setup messages were sent before `surfaceUpdate`.

## 8. JavaScript Errors in the Client

Open the browser developer console. A JavaScript exception in the rendering layer will cause a blank screen even if the message was received correctly. Look for errors related to undefined properties, component rendering failures, or connection errors.

## Recommended Debugging Steps

1. Log the raw message on the sending side to confirm it serializes correctly.
2. Log on the client side that the message was received and inspect its contents.
3. Check the browser console for JavaScript errors.
4. Start with the simplest possible `surfaceUpdate` (one text component, no nesting) to isolate whether the issue is structural or content-related.
5. Compare your message structure against a working example from the A2UI documentation.
