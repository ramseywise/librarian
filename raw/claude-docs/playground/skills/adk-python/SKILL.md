---
name: adk-python
description:
  Use this skill when working on Google Agent Development Kit agents, tools, decorators,
  and project patterns in this repository.
---

# Google ADK Python

## Source of truth

- First consult `/.docs/adk/llms-full.txt`
- Use `/.docs/adk/llms.txt` as the API map
- Canonical upstream references:
  - `https://google.github.io/adk-docs/llms-full.txt`
  - `https://google.github.io/adk-docs/llms.txt`
- If local and upstream docs differ, call out the difference explicitly before coding

## Expectations

- Only use ADK decorators and APIs confirmed in local docs
- Prefer async implementations
- Use Pydantic for structured schemas
- Keep code aligned with existing `/agents/` and `/shared/` patterns

## Repository layout

- `agents/` — individual agent projects (billy_support, simple_router, wine_expert, etc.)
- `shared/guardrails/` — reusable guardrail callbacks (PII redaction, prompt injection, domain validators)
- `shared/tools/` — reusable tool helpers (chain_callbacks, compact_contract_from_pydantic)
- Tests live under each agent's `tests/` directory; follow the existing pytest patterns

## Implementation notes

- Reuse shared helpers before creating new ones
- Examples must be runnable via `adk run` or `pytest`
- Prefer minimal, production-leaning code over toy examples
- Add dependencies via `uv add <package>` (project uses `uv`; do not edit `uv.lock` manually)

## Before generating code

- Check whether a similar agent already exists in `/agents/`
- Check whether a shared guardrail or tool already exists in `/shared/`
- Verify imports and ADK usage against the local docs
