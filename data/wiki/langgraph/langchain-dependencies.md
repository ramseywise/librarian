---
title: LangChain Dependency Management
tags: [langgraph, llm, reference]
summary: Package structure and version policy for the LangChain ecosystem — langchain/langchain-core/langgraph/langsmith as the required core, provider/tool packages installed a la carte, and the langchain-community non-semver trap.
updated: 2026-08-04
sources:
  - raw/agent-skills/langchain-dependencies/SKILL.md
---

# LangChain Dependency Management

The LangChain ecosystem splits into focused, independently-versioned packages. Getting the package set and version constraints right prevents incompatibilities and keeps upgrades predictable.

**LangChain 1.0 is the current LTS release** — always start new projects on 1.0+. LangChain 0.3 is legacy, maintenance-only until December 2026; do not use it for new work.

## Environment Requirements

| Requirement | Python | TypeScript / Node |
|---|---|---|
| Runtime minimum | Python 3.10+ | Node.js 20+ |
| LangChain | 1.0+ (LTS) | 1.0+ (LTS) |
| LangSmith SDK | >= 0.3.0 | >= 0.3.0 |

## Framework Choice — Pick One Orchestration Layer

See [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] for the full decision guide. At the dependency level, the choice is: install `langgraph` directly, or install `deepagents` (which depends on LangGraph and pulls it in transitively) — never both as separate top-level choices.

| Framework | When to use | Core package |
|---|---|---|
| LangGraph | Fine-grained graph control, custom workflows, loops, branching | `langgraph` / `@langchain/langgraph` |
| Deep Agents | Batteries-included planning, memory, file context, skills | `deepagents` (bundles LangGraph) |

Both sit on top of `langchain` + `langchain-core` + `langsmith`.

## Core Packages (Python)

| Package | Role | Min version |
|---|---|---|
| `langchain` | Agents, chains, retrieval | 1.0 |
| `langchain-core` | Base types & interfaces (peer dep — install explicitly) | 1.0 |
| `langsmith` | Tracing, evaluation, datasets | 0.3.0 |

Model providers are installed a la carte: `langchain-openai`, `langchain-anthropic`, `langchain-google-genai`, `langchain-mistralai`, `langchain-groq`, `langchain-cohere`, `langchain-fireworks`, `langchain-together`, `langchain-huggingface`, `langchain-ollama`, `langchain-aws`, `langchain-azure-ai`.

Common tool/retrieval packages: `langchain-tavily`, `langchain-text-splitters`, `langchain-chroma`, `langchain-pinecone`, `langchain-qdrant`, `langchain-weaviate`, `faiss-cpu`. See [[LangChain RAG Implementation Patterns]] for how these are used.

**`langchain-community`** (1000+ integrations, fallback) does **not** follow semantic versioning — minor releases can break. Prefer a dedicated integration package when one exists (e.g. `langchain-chroma` over the community Chroma integration).

## TypeScript Equivalent

`@langchain/core` (peer dep, install explicitly — not always hoisted in yarn workspaces/monorepos), `langchain`, `@langchain/langgraph`, `langsmith`, plus `@langchain/<provider>` packages.

## Minimal Templates

```
# requirements.txt — LangGraph project
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langgraph>=1.0,<2.0
langsmith>=0.3.0
# + your model provider, e.g. langchain-anthropic
```

```
# requirements.txt — Deep Agents project
deepagents            # bundles langgraph internally
langchain>=1.0,<2.0
langchain-core>=1.0,<2.0
langsmith>=0.3.0
# + your model provider
```

## Versioning Policy

| Package group | Versioning | Safe upgrade |
|---|---|---|
| `langchain`, `langchain-core`, `langgraph`, `langsmith` | Strict semver (1.0 LTS) | Allow minor: `>=1.0,<2.0` |
| Dedicated integration packages (`langchain-tavily`, `langchain-chroma`, ...) | Independently versioned | Allow minor; use latest |
| `langchain-community` | **NOT semver** | Pin exact minor: `>=0.4.0,<0.5.0` |
| `deepagents` | Follows project releases | Pin to tested version in production |

Breaking changes only occur at major version boundaries (1.x → 2.x) for semver-compliant packages; deprecated features stay functional across the whole 1.x series with warnings.

## Common Mistakes

- **Starting new work on LangChain 0.3** — use `langchain>=1.0,<2.0` instead.
- **Unpinned `langchain-community`** — `langchain-community>=0.4` can break on a minor bump; pin `>=0.4.0,<0.5.0` or switch to a dedicated package.
- **Deprecated import paths** — e.g. `from langchain_community.vectorstores import Chroma` instead of `from langchain_chroma import Chroma`. Check the LangChain integrations directory for the canonical import when in doubt.
- **Missing `@langchain/core`** in TypeScript monorepos — it's a peer dependency and won't always hoist automatically.
- **Python < 3.10 or Node < 20** — both are below LangChain 1.0's supported minimums.

## See Also
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]]
- [[Deep Agents Framework]]
- [[LangChain RAG Implementation Patterns]]
- [[Notebook Dependency Staleness]] — complements (the same migrate-vs-pin decision in the ML notebook ecosystem)
