---
title: In-Band Stream Errors Read as Bad Answers
tags: [eval, pattern]
summary: "Streaming LLM protocols report a failed generation as an error chunk inside a 200-status stream, so an eval client that only collects text chunks turns an auth failure into an empty answer scored 0.00 with error null — the parser must treat in-stream error events as row errors, and an all-errored run must print n/a, not a mean."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/vercel-native-ts-agent-scaffold.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--vercel-native-ts-agent-scaffold.md
---

# In-Band Stream Errors Read as Bad Answers

An answer-overlap smoke eval for a TypeScript Vercel AI SDK agent POSTed each golden-QA
question to the running `/agent/chat` route and parsed the UI-message SSE stream. The
first working version collected `text-delta` chunks only. With no API key set, every
request returned **HTTP 200**: the AI SDK's streaming protocol reports a provider failure
(here a 401) as an in-stream `{"type":"error",...}` chunk, not as a non-2xx response. The
parser saw no text, built an empty answer, scored it `0.00` overlap, and recorded
`error: null`.

That is the exact bug class the eval existed to catch — a silent failure that looks like
a bad answer — reproduced inside the eval itself.

## The mechanism

- Once a streaming response has started, the status line is already sent. Anything that
  goes wrong later can only be expressed as stream content.
- A client written against the happy path filters for the content event type and drops
  everything else. Error events fall into "everything else."
- The scorer cannot tell an empty answer from a failed request, so the failure enters the
  aggregate as a legitimate low score and drags the mean toward "model is bad."

## The fix

1. Parse every event type the protocol defines; on an `error` event, **throw**, so the
   per-row `try/catch` records `answer_overlap_ratio: null` plus the real error message.
2. Summaries must distinguish "scored 0" from "could not score": an all-errored run prints
   `mean_answer_overlap: n/a (all requests errored — check the API key and that the server
   is running)`, never `0.000`.
3. Unit-test the stream parser in isolation against synthetic `text-delta` and `error`
   payloads before wiring it into the full render — separate "is the parsing correct"
   from "does the pipeline run."
4. Run the eval once against a deliberately broken environment (no key). This bug was
   invisible to typecheck and lint and surfaced only against a live server.

## Related decision: do not force-fit the grader

The same plan first proposed folding the TS agent into the Python eval runner as one more
backend. Reading the runner showed it grades **retrieval** (hit-rate/MRR from a
`search_fn`); a tool-calling agent with no retrieval step would have produced a permanent,
meaningless 0% hit rate. The resolution was a separate answer-only smoke eval, tagged with
a distinct backend name and written to the same reports directory, so it is discoverable
alongside the others without pretending to be retrieval-comparable.

## See Also
- [[Silence Reads as Clean]] — instance-of (a failure with no error signal enters the score as data)
- [[Streaming Output Scrubbing]] — related (the same stream seam, guarded on the output side)
- [[Silent Failure Catalogue]] — instance-of
- [[A Check Must Say Why It Could Not Check]] — extends (n/a with a reason instead of a zero)
