FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
# The project itself is installed (src layout), so its packages must be present first.
COPY src ./src
COPY tools ./tools
COPY apps/__init__.py ./apps/__init__.py
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp
RUN uv sync --extra api --no-dev
COPY wiki ./wiki
ENV LIBRARIAN_ROOT=/app

EXPOSE 8000
CMD ["uv", "run", "--extra", "api", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
