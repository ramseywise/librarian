---
title: TypeScript Async Patterns
tags: [foundations, pattern]
summary: "A JS promise starts running when it is created (unlike an asyncio coroutine), so the choice is sequential vs Promise.all parallel; Promise.race does not cancel the loser, forEach does not await, and an unbounded Promise.all over thousands of requests needs a concurrency limit — pass an AbortSignal down to cancel real work."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--06-async.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# TypeScript Async Patterns

JavaScript runs on one thread with an event loop. Anything slow (network, disk, timers) returns a
`Promise`, and `await` pauses only the current function, never the whole program. In Node the event
loop is always running — there is no `asyncio.run()` to call; a top-level `await` in an ES module
plays that role.

## Mapping from asyncio

| asyncio | JavaScript | Difference |
|---|---|---|
| `async def` / `await` | `async function` / `await` | Same idea |
| Coroutine object | `Promise` | **A promise starts running as soon as it is created** — no "forgot to schedule it" step |
| `asyncio.gather(*cs)` | `Promise.all(ps)` | Fails fast on the first rejection |
| `gather(..., return_exceptions=True)` | `Promise.allSettled(ps)` | `{status, value \| reason}` per promise |
| `asyncio.wait_for(c, t)` | `Promise.race([p, timeout])` or `AbortSignal.timeout(ms)` | `race` does **not** cancel the loser |
| `asyncio.Semaphore(n)` | A worker pool or `p-limit` | |

The Python side is covered in [[Python Concurrency Models]].

## Writing async functions

```ts
async function loadUser(id: number): Promise<User> {
  const res = await fetch(`https://api.example.com/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()) as User;     // `as` checks nothing — parse instead
}
```

- An `async` function **always** returns a `Promise`; annotate the return as `Promise<T>`.
- A thrown error becomes a rejected promise; handle it with `try/catch` around `await`.
- The `as User` above is the classic unchecked boundary — see [[Runtime Validation with Zod]].

## Sequential vs parallel

```ts
const a = await getA(); const b = await getB();             // sequential: total = a + b
const [a, b] = await Promise.all([getA(), getB()]);         // parallel: total = max(a, b)
```

Use `Promise.all` for independent work; use `allSettled` when one failure should not discard the
others' results (partition into fulfilled and rejected afterwards).

## Common bugs

| Bug | Symptom | Fix |
|---|---|---|
| Forgotten `await` | `Promise { <pending> }`, or an unhandled rejection surfacing later | Lint rule `@typescript-eslint/no-floating-promises` |
| `await` inside `forEach` | Callbacks are not awaited | `for…of` + `await` (sequential) or `Promise.all(xs.map(…))` (parallel) |
| `Promise.all` over 10,000 requests | Rate limits, exhausted sockets | Limit concurrency (`mapLimit`, a worker pool) |
| Timeout via `race` with no cleanup | Process won't exit, or work continues after the timeout | Clear the timer, and pass an `AbortSignal` to cancel the actual work |

The `race` row is the non-obvious one: `Promise.race` decides which result *you* see, but the
losing promise keeps running. A timeout built only from `race` stops waiting, not working.

## Timeouts, retries, concurrency limits

The building blocks the course has you implement:

- **`withTimeout`** — race the work against a timer, and clear the timer whichever wins.
- **`retry` with backoff** — re-invoke a promise-*returning function* (a promise cannot be re-run;
  it started when created), waiting longer between attempts.
- **`mapLimit`** — a worker pool that caps how many requests
  are in flight at once; the `asyncio.Semaphore` equivalent.
- **`partitionSettled`** — `allSettled`, then split values from reasons.

Which failures deserve a retry at all is a separate question — see [[Agent Retry Taxonomy]].

## Cancellation: `AbortController`

```ts
const res = await fetch(url, { signal: AbortSignal.timeout(5_000) });   // cancels the request itself
```

`fetch`, Node streams and most SDKs (including the Anthropic SDK) accept a `signal`. Pass it down
through your own async functions too, so a timeout at the top cancels work at the bottom.

## Callbacks to promises, and async iteration

Old Node-style `(err, result) => …` APIs are wrapped once with `promisify` from `node:util`
(typing a generic `promisify` yourself is a good generics exercise).

```ts
for await (const chunk of stream) process.stdout.write(chunk);
```

Streaming LLM responses use exactly this shape — see [[TypeScript for AI Apps]].

## See Also
- [[Programming Curriculum]] — related (course map)
- [[Python Concurrency Models]] — prerequisite-for
- [[TypeScript for Python Developers]] — prerequisite-for
- [[TypeScript for AI Apps]] — extends
- [[Agent Retry Taxonomy]] — related (which failures to retry; this page is how to retry them)
- [[Asynchronous Agent Event Loop]] — related (an agent-harness event loop built on the same queue-and-await ideas)
