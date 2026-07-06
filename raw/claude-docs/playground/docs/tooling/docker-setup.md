# Docker Setup Guide for Billy VA

Quick reference for working with containers in this project. Not a Docker tutorial — assumes familiarity with `docker run` and basic container concepts.

## What's in containers here?

Each service (frontend, agents, RAG, MCP backend) runs in its own container. Services communicate via Docker network using their service names (aliases in `docker-compose.yml`).

```
frontend (3000)
    ↓ calls
mcp-server (8766)          [tool backend: CRM access, etc]
    ↓ calls
va-gateway-lg (8001)      [LangGraph agent]
    ↓ calls
va-support-rag (8002)     [retrieval: search knowledge base]
    ↓ calls
postgres (5432)           [vector DB + LangGraph checkpoints]
```

## Build & Run

**First time (or after Dockerfile changes):**
```bash
make va-up-lg    # Build va-gateway-lg + va-support-rag, start containers
```

What happens:
1. Docker reads each Dockerfile
2. Executes RUN commands in sequence (each RUN = one layer, cached for future builds)
3. Starts the container using CMD
4. All logs stream to terminal

**Subsequent runs (if code changed but not Dockerfile):**
```bash
make va-up-lg    # Still uses --build flag; skips unchanged layers due to caching
```

**Stop services:**
```bash
make va-down     # Stop and remove containers (volumes/data persist)
```

## Understanding Dockerfiles

Each Dockerfile follows this pattern:

```dockerfile
FROM python:3.12-slim           # Base OS image

WORKDIR /app                    # Set working directory

COPY pyproject.toml uv.lock ./  # Copy dependency files first
RUN uv sync --frozen --no-dev   # Install dependencies (cached if unchanged)

COPY src/ ./src/                # Copy code (invalidates cache if code changes)

CMD ["python", "main.py"]       # Run on startup
```

**Key insight:** Docker caches layers. Put expensive operations early (dependencies), cheap operations late (code). If you change code, only the code layer rebuilds; dependencies use the cache.

In this project:
- Layer 1: base image + system tools
- Layer 2: dependency files + `uv sync` (slowest, cached aggressively)
- Layer 3: application code (fast rebuilds)
- Layer 4: config + startup command

## Debugging

**View logs:**
```bash
docker compose -f infrastructure/containers/docker-compose.yml logs -f va-gateway-lg
```

**Enter a running container:**
```bash
docker exec -it playground-va-gateway-lg-1 /bin/bash
# Now inside the container
python -c "import structlog; print('OK')"  # verify imports work
```

**Inspect image layers:**
```bash
docker image history playground-va-gateway-lg
# Shows size of each layer, when it was built, etc
```

**Check venv location:**
```bash
docker exec playground-va-gateway-lg-1 which python
# Should output: /app/.venv/bin/python
```

## Common Issues

**"ModuleNotFoundError: No module named 'X'"**
- Dependencies aren't installed. Check: did `uv sync` run? Is the venv at `/app/.venv`?
- Solution: Rebuild with `--build` to force re-run of RUN commands.

**"Connection refused" between services**
- Services can't reach each other. Check: are they on the same Docker network? Use service names, not localhost.
- Example: `httpx.get("http://va-support-rag:8002/health")` ✓ (service name)
- Example: `httpx.get("http://localhost:8002/health")` ✗ (localhost = container's own localhost)

**Build takes forever**
- `uv sync` downloading large packages. First build is slow; subsequent builds use cache.
- Tip: avoid changing `pyproject.toml` or `uv.lock` unless necessary (invalidates cache).
- If `uv.lock` is out of sync: `cd va-langgraph && uv lock --upgrade`, commit, rebuild.

**Container starts then crashes**
- Check logs: `docker compose logs va-gateway-lg`
- Common cause: imports fail, env var missing, database not ready.
- Solution: enter container and test manually (`docker exec -it ...`).

## Environment Variables

Docker Compose reads `.env` file for variables passed to containers:
```bash
cat .env  # see what's set
```

In Dockerfile:
```dockerfile
ENV MY_VAR=value     # hardcoded in image
```

In docker-compose.yml:
```yaml
environment:
  - MY_VAR=${MY_VAR}  # read from .env or host
```

## Volumes

Persistent data (postgres, billy.db) lives in named volumes so it survives `docker compose down`:
```bash
docker volume ls                                    # see all volumes
docker volume inspect playground_postgres_data     # inspect one
docker volume rm playground_postgres_data          # delete (careful!)
```

## Performance Tips

1. **Skip frontend if testing API:** Use `make va-up-lg` instead of `make va-up`. Saves 2+ min build time.
2. **Use `.dockerignore`:** Prevents copying unnecessary files (tests, .git, __pycache__).
3. **Multi-stage builds:** Separate build stage from runtime. Example: build wheels, then copy only wheels into slim runtime image.

## Resources

- [Docker docs](https://docs.docker.com/): Comprehensive but verbose.
- [Docker Compose docs](https://docs.docker.com/compose/): Focuses on multi-container.
- [Dockerfile best practices](https://docs.docker.com/develop/dev-best-practices/): Layering, caching, security.
