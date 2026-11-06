# One image: the API plus the built web UI, on one port.
# Build from the repo root: docker build -f apps/api/Dockerfile -t librarian .
#
# Not in the image: data/ (the wiki, courses, glossary), which is mounted read-only at /app/data,
# and anything private. State (search index, caches, logs, flashcard results) is written to
# /app/var, a volume. docker-compose.yml wires both.

# ---- stage 1: the web UI ----
FROM node:22-slim AS web
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web ./
RUN npm run build

# ---- stage 2: the API ----
FROM python:3.12-slim AS api
WORKDIR /app

RUN pip install --no-cache-dir uv \
    && useradd --create-home --uid 1000 librarian

# Dependencies first so editing source does not invalidate this layer. hatchling needs the
# packages listed under [tool.hatch.build.targets.wheel] to exist when the project installs.
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY tools ./tools
COPY apps/__init__.py ./apps/__init__.py
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp
RUN uv sync --frozen --extra api --no-dev

# The embedding model, so the container does not download it on first start (readiness waits for it).
ENV HF_HOME=/opt/hf
RUN /app/.venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    && chmod -R a+rX /opt/hf

COPY --from=web /web/dist ./apps/web/dist

# /app/var is created owned by the app user so a fresh named volume inherits that.
RUN mkdir -p /app/var /app/data && chown librarian:librarian /app/var

ENV PATH="/app/.venv/bin:$PATH" \
    LIBRARIAN_ROOT=/app \
    LIBRARIAN_STATE_DIR=/app/var \
    SERVE_COURSE_SOURCES=false \
    PYTHONUNBUFFERED=1

USER librarian
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"
CMD ["librarian", "api", "--host", "0.0.0.0", "--port", "8000"]
