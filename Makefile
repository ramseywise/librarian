.PHONY: app app-build obsidian api ui mcp install-ui install-api setup-ollama test test-watch test-e2e install-browsers ingest lint help

app:
	docker compose up

app-build:
	docker compose up --build

obsidian:
	open -a Obsidian $(PWD)/wiki

api:
	cd app && uv run --extra api uvicorn backend.main:app --reload --port 8000

mcp:
	uv run python app/mcp_server/server.py

ui:
	cd app/ui && npm run dev

install-ui:
	cd app/ui && npm install

install-api:
	uv sync --extra api

setup-ollama:
	ollama pull $${OLLAMA_MODEL:-llama3.2}

test:
	uv run pytest tests/unit/ -v

test-watch:
	uv run ptw tests/unit/ -- -v

test-e2e:
	uv run pytest tests/e2e/ -v -m e2e

install-browsers:
	uv run playwright install chromium

ingest:
	@echo "Run /ingest <path> via Claude Code"

lint:
	@echo "Run /lint via Claude Code"

help:
	@echo "app              — start api + ui via Docker (one command)"
	@echo "app-build        — rebuild Docker images and start"
	@echo "obsidian         — open wiki in Obsidian"
	@echo "mcp              — start MCP server (local, used by Claude Code)"
	@echo "api              — start FastAPI backend directly (port 8000)"
	@echo "ui               — start Vite dev server directly (port 5173)"
	@echo "install-ui       — npm install for ui/"
	@echo "install-api      — uv sync --extra api"
	@echo "setup-ollama     — pull the configured Ollama model"
	@echo "test             — run unit tests (no servers needed)"
	@echo "test-watch       — re-run unit tests on file change"
	@echo "test-e2e         — run e2e + screenshot tests (needs api + ui running)"
	@echo "install-browsers — install Playwright Chromium"
	@echo "ingest           — reminder: use /ingest <path> in Claude Code"
	@echo "lint             — reminder: use /lint in Claude Code"
