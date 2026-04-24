# Plan: Phase 2 — Infrastructure & Credentials Refactor
Status: COMPLETE (see CHANGELOG.md [0.2.0])

## Goal
Replace Flask prototype with production-ready structure: custom OAuth httpx client, FastMCP server, DuckDB/Polars ETL, Chainlit stub, centralised config.

## What was built
- `src/spotify/` — custom OAuth httpx client, fetch/write ops, `SpotifyActions`
- `src/mcp_server/server.py` — FastMCP server with stubbed Spotify tools
- `src/app/main.py` — Chainlit entry point (stub)
- `src/utils/config.py` — pydantic-settings, all env vars centralised
- `src/utils/exceptions.py` — typed exception hierarchy
- `src/etl/` — DuckDB bootstrap/sync, Polars loader with Parquet cache
- `setup.sh`, `.env.example`
- `docker-compose.yml` rewrite — MCP port 8765, Jaeger + Postgres profiles
- `Dockerfile` — python:3.11-slim, uv install
- `pyproject.toml` — removed OpenAI/Streamlit; added Anthropic, LangGraph, LightGBM
