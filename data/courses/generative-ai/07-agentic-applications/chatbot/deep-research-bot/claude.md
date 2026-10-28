---
imported_hash: f801164bbd7bffb2
title: CLAUDE
summary: ''
order: 4
kind: reading
section: Chatbot / Deep research bot
source: learn-ai-engineering/generative-ai/07-agentic-applications/chatbot/deep-research-bot/CLAUDE.md
---

## uv for Dependency managment
Always use `uv` for:
- installing dependencies and dependency management
- running python files, e.g. `uv run`

## Weave Evaluations
If you have the wandb MCP server tools available to you; When asked to instrument code with `weave` Evaluations from Weights & Biaes, always use the `wandb` MCP Server tools, specifically the support bot tool, in order to check the weave docs and ensure that you're doing it correctly.

## Testing
Always run tests with `uv` and `pytest`, e.g. `uv run pytest -vv`. use `-vv` to get more detail about the test progress.

## Structured data
Always try use pydantic objects when passing around and retrning data, avoid using jon.dumps

## Typing
Always stick to modern python practices, 3.12 and later, e.g. `list` instead of `List`
