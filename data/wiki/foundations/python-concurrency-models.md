---
title: Python Concurrency Models
tags: [foundations, comparison]
summary: "Pick by what you're waiting on: threads (ThreadPoolExecutor) for a few dozen blocking I/O calls, asyncio for hundreds of concurrent requests or async SDKs, processes for CPU-bound pure Python — and in asyncio, never block the event loop, bound fan-out with a Semaphore, add deadlines, and retry only transient errors with backoff plus jitter."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--python--03-language-for-engineers--notes--07-concurrency.md
---

# Python Concurrency Models

Waiting on the network or disk is **I/O-bound**: use threads or `asyncio`. Crunching numbers in
pure Python is **CPU-bound**: use processes (or NumPy, which releases the GIL). Pick by what
you're waiting on. (Sources: Python `asyncio` and `concurrent.futures` docs.)

## Which tool

| Work | Tool | Why |
|---|---|---|
| A few dozen blocking HTTP calls, existing sync code | `ThreadPoolExecutor` | Threads release the GIL while waiting on I/O |
| Hundreds+ concurrent requests, an async SDK, a web server | `asyncio` | One thread, cheap tasks, explicit `await` points |
| CPU-heavy pure Python | `ProcessPoolExecutor` | Separate interpreters, so no GIL contention |

The **GIL** lets only one thread run Python bytecode at a time — so threads give no speedup for
CPU-bound pure Python. Free-threaded builds (3.13t+) remove it, but most code and libraries still
assume it.

## Threads with concurrent.futures

```python
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch, url): url for url in urls}
    for fut in as_completed(futures):
        url = futures[fut]
        try:
            results[url] = fut.result()
        except Exception as err:
            errors[url] = err
```

- `submit` + `as_completed` collects per-item results and errors as they finish.
- `pool.map(fn, items)` is simpler when you want input order and any exception should stop you.
- Shared mutable state between threads needs a `threading.Lock`. Better: have each task **return** its result and combine in the main thread.

## asyncio

```python
async def main(urls: list[str]) -> list[str]:
    sem = asyncio.Semaphore(10)                        # at most 10 in flight
    async with httpx.AsyncClient() as client:
        async def limited(url):
            async with sem:
                return await fetch(client, url)
        async with asyncio.TaskGroup() as tg:          # 3.11+: cancels the rest if one fails
            tasks = [tg.create_task(limited(u)) for u in urls]
    return [t.result() for t in tasks]

asyncio.run(main(urls))
```

- `async def` makes a coroutine function. **Calling it does nothing** until it is awaited or scheduled as a task.
- `TaskGroup` (3.11+) cancels siblings when one fails and raises an `ExceptionGroup` ([[Python Exceptions and Context Managers]]). `asyncio.gather(*coros, return_exceptions=True)` instead collects results and errors without cancelling.
- `asyncio.Semaphore` bounds fan-out so you don't open hundreds of connections at once.
- Deadlines: `asyncio.timeout(5)` (3.11+) or `asyncio.wait_for(coro, 5)`.
- **Never block the event loop**: `time.sleep`, `requests.get` or heavy CPU work inside `async def` freezes every task. Use `await asyncio.sleep`, an async client, or `await asyncio.to_thread(blocking_fn, ...)`.

This is the same model as JavaScript promises: `Promise.all` corresponds to `gather` and
`TaskGroup` ([[TypeScript Async Patterns]]).

## Retries with backoff

```python
async def with_retry(make_call, attempts=4, base=0.5):
    for i in range(attempts):
        try:
            return await make_call()
        except (TimeoutError, ConnectionError):
            if i == attempts - 1:
                raise
            await asyncio.sleep(base * 2**i + random.random() * base)   # exponential + jitter
```

- Retry only errors that can succeed next time (timeouts, 429, 5xx), **never 4xx validation errors**.
- LLM SDKs already retry for you — check before wrapping them.
- The synchronous decorator-factory form of retry is in [[Python Closures and Decorators]].

## See Also
- [[TypeScript Async Patterns]] — alternative-to (the same event-loop model in JS/TS)
- [[Python Closures and Decorators]] — prerequisite-for (the retry wrapper shape)
- [[Python Exceptions and Context Managers]] — prerequisite-for (ExceptionGroup from TaskGroup)
- [[Agent Retry Taxonomy]] — extends (per-failure-mode retry decisions for agents)
- [[Asynchronous Agent Event Loop]] — related (an agent-level event loop built on these primitives)
- [[Programming Curriculum]] — related (course map)
