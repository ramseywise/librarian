---
imported_hash: d71b386a479436a9
title: RELIABILITY.md
summary: This file defines how the system proves it is healthy and restartable.
order: 37
kind: reading
section: Templates / Openai repo template / Docs
source: learn-ai-engineering/ai-engineering/03-harness/templates/openai-repo-template/docs/RELIABILITY.md
---

# RELIABILITY.md

This file defines how the system proves it is healthy and restartable.

## Standard Paths

- Bootstrap: `[command]`
- Verification: `[command]`
- Start app or service: `[command]`
- Debug or inspect runtime: `[command]`

## Required Runtime Signals

- structured logs for startup and critical flows
- health checks for key services
- trace or timing data for slow paths when available
- user-visible error states for recoverable failures

## Golden Journeys

- `[journey 1]`
- `[journey 2]`
- `[journey 3]`

Each golden journey should have a repeatable verification path and clear failure
signals.

## Reliability Rules

- No feature is complete if the system cannot restart cleanly afterward.
- Runtime failures should be diagnosable from repo-local signals.
- If a repeated failure mode appears, add a benchmark or guardrail for it.
- Cleanup is part of reliability, not a separate concern.
