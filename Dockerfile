# One image: the API plus the built web UI, on one port.
# Build from the repo root: docker build -t librarian .
#
# Not in the image: data/ (the wiki, courses, glossary), which is mounted read-only at /app/data,
# and anything private. State (search index, caches, logs, flashcard results) is written to
# /app/var, a volume. docker-compose.yml wires both.

# ---- stage 1: the web UI ----
FROM node:22-slim AS web
WORKDIR /web
COPY app/package.json app/package-lock.json ./
RUN npm ci
COPY app ./
RUN npm run build

# ---- stage 2: the API ----
FROM python:3.12-slim AS api
WORKDIR /app

RUN pip install --no-cache-dir uv \
    && useradd --create-home --uid 1000 librarian

# Backup tools for `librarian ops` (the compose `backup` service runs from this same image, so the
# host only pulls): pg_dump/pg_restore 17 to match the postgres service, age, and the aws CLI for S3/R2.
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-17 age awscli \
    && rm -rf /var/lib/apt/lists/*

# Dependencies from the lockfile, with CPU-only torch: the locked linux torch pulls ~3 GB of CUDA
# wheels a single-user host cannot use. Torch is installed from the CPU index at the locked
# version; everything else (minus torch, triton and the nvidia-* wheels) comes from uv.lock.
# A slow link with many parallel downloads makes uv's default 30 s timeout restart big wheels forever.
ENV VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH" UV_HTTP_TIMEOUT=300 UV_CONCURRENT_DOWNLOADS=4
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv venv /app/.venv \
    && uv export --frozen --extra api --extra observability --no-dev --no-emit-project --no-hashes -o /tmp/req.txt \
    && TORCH_VERSION=$(sed -n 's/^torch==\([0-9.]*\).*/\1/p' /tmp/req.txt) \
    && grep -Ev '^(torch|triton|nvidia-|cuda-)' /tmp/req.txt > /tmp/req-nocuda.txt \
    && uv pip install --no-deps -r /tmp/req-nocuda.txt \
    && uv pip install --no-deps --index-url https://download.pytorch.org/whl/cpu "torch==${TORCH_VERSION}"

# The embedding model, so the container does not download it on first start (readiness waits for it).
# Before `COPY src`, so a code change keeps this layer. A download that stalls is killed after
# 5 minutes and retried, so the build fails instead of hanging.
ENV HF_HOME=/opt/hf HF_HUB_DOWNLOAD_TIMEOUT=60
RUN for attempt in 1 2 3; do \
        timeout 300 /app/.venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
        && break; \
        echo "model download attempt ${attempt} failed" >&2; \
        [ "${attempt}" = 3 ] && exit 1; \
    done \
    && chmod -R a+rX /opt/hf

# hatchling needs the packages listed under [tool.hatch.build.targets.wheel] to exist when the
# project installs.
COPY src ./src
RUN uv pip install --no-deps -e .

COPY --from=web /web/dist ./app/dist

# /app/var is created owned by the app user so a fresh named volume inherits that.
RUN mkdir -p /app/var /app/data && chown librarian:librarian /app/var

# The image has no .git: pass the release at build time
# (docker build --build-arg LIBRARIAN_RELEASE=<short sha> ...).
ARG LIBRARIAN_RELEASE=dev
ENV LIBRARIAN_RELEASE=${LIBRARIAN_RELEASE} \
    LIBRARIAN_ROOT=/app \
    LIBRARIAN_STATE_DIR=/app/var \
    SERVE_COURSE_SOURCES=false \
    LIBRARIAN_PUBLIC=true \
    PYTHONUNBUFFERED=1

COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/entrypoint.sh

USER librarian
EXPOSE 8000
# Readiness, not liveness: healthy means the index is built and the model loaded. The first start
# builds the index in the background (dev default; production runs `librarian index build`), so the
# start period covers that build.
# /readyz is public (no bearer token) and only reads the handle's state: a probe opens nothing.
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=8)"
ENTRYPOINT ["entrypoint.sh"]
CMD ["librarian", "api", "--host", "0.0.0.0", "--port", "8000"]
