.PHONY: viz api ui install-ui ingest lint help

viz:
	open -a Obsidian $(PWD)/wiki

api:
	cd app && uv run uvicorn backend.main:app --reload --port 8000

ui:
	cd app/ui && npm run dev

install-ui:
	cd app/ui && npm install

install-api:
	uv sync --extra api

ingest:
	@echo "Run /ingest <path> via Claude Code"

lint:
	@echo "Run /lint via Claude Code"

help:
	@echo "viz          — open wiki in Obsidian"
	@echo "api          — start FastAPI backend (port 8000)"
	@echo "ui           — start Vite dev server (port 5173)"
	@echo "install-ui   — npm install for ui/"
	@echo "install-api  — uv sync --extra api"
	@echo "ingest       — reminder: use /ingest <path> in Claude Code"
	@echo "lint         — reminder: use /lint in Claude Code"
