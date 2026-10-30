---
imported_hash: 7fd6ae1bbae970e0
title: Drill problems
summary: Cold-attempt material for /env-drill. Unlike dsa/, these ship without solutions — the answer gets written with you at drill time, into solutions/<phase>.md.
order: 250
kind: reading
section: Problems
source: sisyphus/drills/coding/problems/README.md
---

# Drill problems

Cold-attempt material for `/env-drill`. **Unlike `dsa/`, these ship without solutions** —
the answer gets written with you at drill time, into `solutions/<phase>.md`.

| Problem | Env | Fills gap | Timebox | Prompts |
|---|---|---|---|---|
| `token-service/` | env1 | security + PII | 45 min | `prompts.md` — 4 phases |
| `rate-limiter/` | env1 | OOD | 45 min | `prompts.md` — 4 phases |
| `feed-ranker/` | env2 | AI-sandbox feature build | 30 min | `prompts.md` — 1 feature request |
| `property-search/` | env1 | silent ranking bugs in embeddings + FAISS; NLP vs LLM design | 60 min | `prompts.md` — 3 phases |

## Layout

```text
problems/<name>/
  src/          # given code, runnable, seeded bugs where applicable
  prompts.md    # questions only — safe to read before attempting
```

At drill time the skill creates `problems/<name>/solutions/<phase>.md` in the battleship
page contract: question → raw attempt → feedback → better version → What I'd say.

## Rules

- **`src/` is copied from, never edited.** Work in `drills/coding/scratch/`.
- **Read `prompts.md` only.** Nothing here contains an answer key by design, but the
  seeded bugs are only findable once.
- Backlog Hello Interview problems here too, same layout — `src/` + `prompts.md`.

## Sourcing note

`dsa/` (the "Hello, Interview!" open-source repo) is **reference, not drill material** —
every problem ships with its solution and THINKING doc, so reading one spends it. Use it
to refresh a pattern, not to rehearse cold.
