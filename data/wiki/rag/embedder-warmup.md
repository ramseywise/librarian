---
title: Embedder Warmup
tags: [rag, infra, concept]
summary: Force-loading the embedding model during application startup (before the first request) to prevent a 3–8s cold-start spike on the first query in production.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
---

# Embedder Warmup

Embedding models (especially cross-encoders like `ms-marco-MiniLM`) are lazy-loaded by default — the model weights are downloaded and loaded into memory on first use. In production, this means the first request after a deploy or restart takes 3–8 seconds instead of ~100ms.

## The Fix

Force the model to load during the application lifespan startup hook:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Force model load before accepting traffic
    embedder.embed_query("warmup")
    reranker.predict([("warmup", "warmup")])
    yield
    # Cleanup on shutdown

app = FastAPI(lifespan=lifespan)
```

A dummy embed call during lifespan triggers the lazy load. All subsequent requests hit a warm model.

## What to Warm

| Model | Lazy load penalty |
|---|---|
| Embedding model (e5-large, MiniLM) | 2–5s on first call |
| Cross-encoder reranker | 1–3s on first call |
| Chroma client connection | ~500ms |

Warm all of them in the lifespan. The warmup call itself is fast (<1s) once loaded.

## Why It Matters in Production

Without warmup:
- First user after deploy gets a visibly slow response
- Load balancers may timeout the first request
- Health checks may fail if the first real request exceeds their timeout

With warmup, all requests including the first get consistent <500ms embedding latency.

## See Also
- [[Production Hardening Patterns]]
- [[Librarian RAG Architecture]]
- [[RAG Retrieval Strategies]]
