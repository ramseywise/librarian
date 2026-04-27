FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --extra api --no-dev

COPY app/backend ./app/backend
COPY wiki ./wiki

EXPOSE 8000
CMD ["uv", "run", "--extra", "api", "uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
