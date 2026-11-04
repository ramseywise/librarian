---
title: "Connection Pooling Turns Failure into Waiting"
tags: [foundations, concept]
summary: "Each Postgres connection is a server process under a fixed max_connections, so a burst beyond it fails; a pool shares a few connections and converts the failures into queueing, with PgBouncer transaction mode breaking session state."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--05-operating-data-stores.md
---

# Connection Pooling Turns Failure into Waiting

Each Postgres connection is a server process, and `max_connections` is fixed at server start and sizes shared memory, so it is not a value to raise freely: more processes contending for the same CPU and disk rarely help, and a very high value once stopped a server restarting mid-incident with a semaphore error. A few slots stay reserved for superusers, which is how you get in during an exhaustion incident.

## Measured

Bench with `max_connections` of 30; 100 clients, 500 requests:

| Setup | Result |
|---|---|
| New connection each query | 1.27 ms per connect versus 0.02 ms on a held connection |
| No pool | 0.40 s, slowest 99 ms, 349 of 500 failed |
| Pool of 10 | 2.58 s, slowest 521 ms, 0 of 500 failed |

The pool's 2.58 s is close to 500 x 50 ms / 10, the capacity it exposes. It turns failure into waiting and makes the bottleneck visible: the slowest request tells you the queue length. The connect cost was on a local socket with no TLS, so the real gap is larger.

## Beyond one process

An in-process pool serves one application; many instances each with a pool can still exceed the limit. A proxy such as PgBouncer (read about, not run) handles that. Modes:

| Mode | Server connection held | Breaks |
|---|---|---|
| Session | Until client disconnects | Nothing, saves little |
| Transaction | Per transaction | `SET`, `LISTEN`, session advisory locks, `PREPARE`, `WITH HOLD` cursors, `PRESERVE ROWS` temp tables |
| Statement | Per query | Multi-statement transactions too |

`SET lock_timeout` is session state, so run migrations on a direct connection ([[Lock Queue and lock_timeout for Live DDL]]).

## See Also
- [[Backend Scaling Fundamentals]] — related
- [[Vacuum, Bloat and Idle Transactions]] — related
- [[Lock Queue and lock_timeout for Live DDL]] — related
