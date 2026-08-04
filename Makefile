include ~/.claude/Makefile.common

.PHONY: app app-build obsidian api ui mcp install-ui install-api setup-ollama test test-watch test-e2e install-browsers ingest scrape scrape-sessions scrape-docs scrape-repos lint lint-raw help codemap-reindex codemap-api install-codemap install-presenter eval eval-live

app:
	docker compose up

app-build:
	docker compose up --build

obsidian:
	open -a Obsidian $(PWD)/data/wiki

api:
	cd app && uv run --extra api uvicorn backend.main:app --reload --port 8000

mcp:
	uv run python app/mcp_server/server.py

ui:
	cd app/frontend && npm run dev

install-ui:
	cd app/frontend && npm install

install-api:
	uv sync --extra api

install-codemap:
	uv sync --extra codemap

install-presenter:
	uv sync --extra presenter

codemap-reindex:
	uv run codemap

codemap-api:
	uv run uvicorn tools.codemap.api:app --reload --host $${CODEMAP_API_HOST:-127.0.0.1} --port $${CODEMAP_API_PORT:-8100}

setup-ollama:
	ollama pull $${OLLAMA_MODEL:-llama3.2}

eval:
	uv run python evals/run_eval.py --verbose --save-baseline

eval-live:
	uv run python evals/run_eval.py --live --verbose --save-baseline

test:
	uv run pytest tests/unit/ -v

test-watch:
	uv run ptw tests/unit/ -- -v

test-e2e:
	uv run pytest tests/e2e/ -v -m e2e

install-browsers:
	uv run playwright install chromium

scrape-sessions:
	uv run python core/scrape_sessions.py

scrape-docs:
	uv run python core/scrape_claude_docs.py

scrape-repos:
	uv run python core/scrape_repos.py

lint-raw:
	uv run python core/lint_raw.py

scrape: scrape-docs scrape-sessions scrape-repos
	@echo "Done — run /ingest in Claude Code to compile all changed sources into wiki"

ingest: scrape-docs scrape-sessions scrape-repos
	@echo "Done — run /ingest in Claude Code to compile all changed sources into wiki"

lint:
	@echo "Run /lint via Claude Code"

help:
	@echo "app              — start api + ui via Docker (one command)"
	@echo "app-build        — rebuild Docker images and start"
	@echo "obsidian         — open wiki in Obsidian"
	@echo "mcp              — start MCP server (local, used by Claude Code)"
	@echo "api              — start FastAPI backend directly (port 8000)"
	@echo "ui               — start Vite dev server directly (port 5173)"
	@echo "install-ui       — npm install for app/frontend/"
	@echo "install-api      — uv sync --extra api"
	@echo "install-codemap  — uv sync --extra codemap"
	@echo "install-presenter — uv sync --extra presenter"
	@echo "codemap-reindex  — reindex repos in tools/codemap/repos.txt → .code_index.duckdb"
	@echo "codemap-api      — start Codemap Query API (port 8100)"
	@echo "setup-ollama     — pull the configured Ollama model"
	@echo "test             — run unit tests (no servers needed)"
	@echo "test-watch       — re-run unit tests on file change"
	@echo "test-e2e         — run e2e + screenshot tests (needs api + ui running)"
	@echo "install-browsers — install Playwright Chromium"
	@echo "scrape           — run all scrapers (claude-docs + .agents + sessions) → data/raw/"
	@echo "scrape-sessions  — scrape Claude Code + Codex sessions → data/raw/sessions/"
	@echo "scrape-docs      — scrape .claude/ docs, docs/, .agents/ from all projects → data/raw/claude-docs/"
	@echo "scrape-repos     — scrape CLAUDE.md + skills + docs from repos in data/raw/repos/repos.txt"
	@echo "ingest           — run all scrapers → data/raw/, then run /ingest in Claude Code to compile into wiki"
	@echo "lint-raw         — validate data/raw/ filenames match YYYY-MM-DD-slug convention"
	@echo "lint             — reminder: use /lint in Claude Code"
	@echo "eval             — run retrieval + answer graders over golden dataset; save baseline"
	@echo "eval-live        — eval against the live search core (report-only); save live baseline"
