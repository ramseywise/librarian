---
imported_hash: e00cf55e9e6c1471
title: Advanced Repo Template
summary: Copy this starter into a real repository when you want an OpenAI-style agent-first documentation surface instead of only a minimal harness.
order: 29
kind: reading
section: Templates / Openai repo template
source: learn-ai-engineering/ai-engineering/03-harness-engineering/templates/openai-repo-template/README.md
---

# Advanced Repo Template

Copy this starter into a real repository when you want an OpenAI-style
agent-first documentation surface instead of only a minimal harness.

## Copy Order

1. Copy `AGENTS.md` and `ARCHITECTURE.md` to the repo root.
2. Copy the whole `docs/` tree.
3. Fill in `docs/PRODUCT_SENSE.md`, `docs/QUALITY_SCORE.md`, and
   `docs/RELIABILITY.md` first.
4. Add your first active plan under `docs/exec-plans/active/`.
5. Keep the entrypoint files short and route detail into the linked docs.

## What This Template Optimizes For

- durable repo-local context
- progressive disclosure instead of one giant instruction file
- explicit plan lifecycle
- quality tracking over time
- readable boundaries for agents and humans

Treat every file here as a starter. Replace placeholders, examples, and sample
commands with your real project specifics before relying on it.
