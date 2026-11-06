# Build from the repo root: docker build -f apps/api/Dockerfile .
# The wiki and courses (data/) are NOT baked in: mount the checkout's data/ at /app/data
# (docker-compose.yml does). apps/web has its own image.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Dependencies first so editing source does not invalidate this layer. hatchling needs the
# packages listed under [tool.hatch.build.targets.wheel] to exist when the project installs.
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY tools ./tools
COPY apps/__init__.py ./apps/__init__.py
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp
RUN uv sync --frozen --extra api --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    LIBRARIAN_ROOT=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["librarian", "api", "--host", "0.0.0.0", "--port", "8000"]
