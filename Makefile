# Shared git-workflow targets (pull, push, quick-pr, ship, md-lint). Optional: the
# repo targets below must keep working on a machine without ~/.claude set up.
-include ~/.claude/Makefile.common

.PHONY: slides slides-all flashcards deck-graph deck-graph-check deck-check app app-build dev deploy-content obsidian api ui mcp index-rebuild install-ui install-api setup-ollama test test-watch test-e2e install-browsers ingest scrape scrape-sessions scrape-docs scrape-repos lint lint-raw help codemap-reindex codemap-api install-codemap install-presenter eval eval-live eval-nofts eval-gate eval-chat eval-chat-dry e2e-container e2e-compose

# The private tmpfs masks need their mountpoints on the host: the data mount is read-only.
LOCAL_COMPOSE = docker compose -f docker-compose.yml -f docker-compose.local.yml

app:
	mkdir -p data/wiki/private data/courses/private
	$(LOCAL_COMPOSE) up librarian

app-build:
	mkdir -p data/wiki/private data/courses/private
	$(LOCAL_COMPOSE) up --build librarian

# Rsync data/wiki + data/courses (+ built var/slides) to $$DEPLOY_HOST:$$DEPLOY_PATH (never private/), then restart the service.
deploy-content:
	scripts/deploy-content.sh

obsidian:
	open -a Obsidian $(PWD)/data/wiki

api:
	LIBRARIAN_DEV_BUILD_SLIDES=1 LIBRARIAN_DEV_WATCH=1 uv run --extra api librarian api --reload --port 8000

mcp:
	uv run librarian mcp

# Force a full drop + re-embed of the wiki index (normal edits re-index incrementally).
index-rebuild:
	uv run librarian mcp --rebuild

ui:
	cd app && npm run dev

# api + ui together, hot reload, no Docker; Ctrl-C stops both. Open http://localhost:5173.
# Open mode: the .env token (for make app) is blanked here, since the api binds loopback only.
dev:
	@if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then \
		echo "port 8000 is in use (make app still running? docker compose stop librarian)"; exit 1; fi
	@[ -d app/node_modules ] || $(MAKE) install-ui
	@echo "open http://localhost:5173 (live UI; :8000 serves the last npm run build)"
	@trap 'kill 0' INT TERM EXIT; LIBRARIAN_API_TOKEN= $(MAKE) api & $(MAKE) ui & wait

install-ui:
	cd app && npm install

install-api:
	uv sync --extra api

install-codemap:
	uv sync --extra codemap

install-presenter:
	uv sync --extra presenter

# Lecture decks for every course. Specs and images live in data/courses; built files are gitignored.
SLIDES_DIR = data/courses/$(PILLAR)

slides:  ## Build a deck: make slides PILLAR=<course>/<module> [LECTURE=<NN-slug>] [PREVIEW=1] [PDF=1] [STRICT=1] [LEVEL=core|practice|deep]
	@test -n "$(PILLAR)" || { echo "usage: make slides PILLAR=<course>/<module> [LECTURE=<NN-slug>] [PREVIEW=1] [PDF=1] [STRICT=1] [LEVEL=core|practice|deep]"; exit 1; }
	@uv run -q --with python-pptx --with pillow --with resvg-py python -m librarian.tools.slides.build_deck \
		$(SLIDES_DIR)/slides/$(if $(LECTURE),lectures/$(LECTURE).yaml,deck.yaml) \
		$(if $(PREVIEW),--preview $(SLIDES_DIR)/slides/$(if $(LECTURE),lectures/.preview/$(LECTURE),.preview)) $(if $(PDF),--pdf) $(if $(STRICT),--strict) $(if $(LEVEL),--level $(LEVEL))

flashcards:  ## Build every module's _flashcards.md from its local deck specs [CHECK=1 to only check]
	@uv run -q python src/librarian/tools/slides/flashcards.py $(if $(CHECK),--check)

slides-all:  ## Build every deck in every course [PDF=1]
	@find data/courses -path '*/slides/deck.yaml' -o -path '*/slides/lectures/*.yaml' | sort | xargs -n1 -I{} uv run -q --with python-pptx --with pillow --with resvg-py python -m librarian.tools.slides.build_deck {} $(if $(PDF),--pdf)

deck-graph:  ## Regenerate data/courses/_decks.md, the map of every module and lecture
	@uv run -q python src/librarian/tools/slides/deck_graph.py build

deck-graph-check:  ## Fail if a lecture's covers or edges name a missing note, or two lectures claim one note
	@uv run -q python src/librarian/tools/slides/deck_graph.py check

deck-check:  ## Fail if a built deck no longer matches its yaml; decks not built yet are reported only
	@python3 src/librarian/tools/slides/deck_stamp.py

codemap-reindex:
	uv run codemap

codemap-api:
	uv run uvicorn librarian.tools.codemap.api:app --reload --host $${CODEMAP_API_HOST:-127.0.0.1} --port $${CODEMAP_API_PORT:-8100}

setup-ollama:
	ollama pull $${OLLAMA_MODEL:-llama3.2}

eval:
	uv run python -m evals.run_eval --verbose --save-baseline

eval-live:
	uv run python -m evals.run_eval --live --verbose --save-baseline

eval-nofts:
	uv run python -m evals.run_eval --live --arm nofts --verbose --save-baseline

# Every gated live arm: healthy pipeline, degraded fallback, uniformly sampled wiki
# pages, lesson search, one-hop graph expansion, and the two-page questions. A ranking
# change must clear all of them, not trade one for another.
# Chat-answer eval (phase 4b): the real agent and a judge on evals/golden_chat.json. BILLABLE; WARN-only.
# `make eval-chat LIMIT=5` runs a few. Ask the owner before the first paid run.
eval-chat:
	uv run python -m evals.run_chat_eval $(if $(LIMIT),--limit $(LIMIT),)

# Same questions, no API client: prints the plan and an estimated cost.
eval-chat-dry:
	uv run python -m evals.run_chat_eval --dry-run $(if $(LIMIT),--limit $(LIMIT),)

eval-gate:
	uv run python -m evals.run_eval --live --arm sem --verbose
	uv run python -m evals.run_eval --live --arm nofts --verbose
	uv run python -m evals.run_eval --live --arm uniform --verbose
	uv run python -m evals.run_eval --live --arm course --verbose
	uv run python -m evals.run_eval --live --arm graph --verbose
	uv run python -m evals.run_eval --live --arm multihop --verbose

.PHONY: wiki-stats wiki-snapshot wiki-check wiki-gaps wiki-graph
.PHONY: skills-check skills-sync chapter-check chapter-check-all link-check curriculum crosswalk crosswalk-check manifest-check import-courses drill-check review-findings signals smoke-labs

wiki-stats:
	uv run librarian wiki stats

wiki-snapshot:
	uv run librarian wiki snapshot

wiki-check:
	uv run librarian wiki check

# The curriculum sections read the course catalog (no api extra needed).
wiki-gaps:
	uv run librarian wiki gaps

wiki-graph:
	uv run librarian wiki graph

test:
	uv run pytest tests/ --ignore=tests/e2e -v

test-watch:
	uv run ptw tests/ --ignore=tests/e2e -- -v

test-e2e:
	uv run pytest tests/e2e/ -v -m e2e

e2e-container:  ## Build the image, run it with a test token and run the e2e set against it (SKIP_BUILD=1, KEEP=1, E2E_PORT)
	tests/e2e/run_container.sh

e2e-compose:  ## Whole stack behind Caddy with 2 API replicas on Postgres, e2e through TLS (REPLICAS, SKIP_BUILD=1, KEEP=1)
	tests/e2e/run_compose.sh

install-browsers:
	uv run playwright install chromium

scrape-sessions:
	uv run librarian scrape sessions

scrape-docs:
	uv run librarian scrape docs

scrape-repos:
	uv run librarian scrape repos

lint-raw:
	uv run librarian ingest lint-raw

scrape: scrape-docs scrape-sessions scrape-repos
	@echo "Done — run /ingest in Claude Code to compile all changed sources into wiki"

ingest: scrape-docs scrape-sessions scrape-repos
	@echo "Done — run /ingest in Claude Code to compile all changed sources into wiki"

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests
	uv run lint-imports
	uv run --all-extras pyright  # pyright resolves imports from every extra, as CI does

# Architecture contracts (pyproject.toml [tool.importlinter]): library core never imports api/mcp/tools, etc.
lint-imports:
	uv run lint-imports

# pyright, basic mode, over src (pyproject.toml [tool.pyright]).
typecheck:
	uv run pyright

help:
	@echo "dev              — api + ui with hot reload, no Docker (http://localhost:5173)"
	@echo "app              — api + built ui in one Docker container (http://localhost:8000; needs LIBRARIAN_API_TOKEN)"
	@echo "app-build        — rebuild Docker images and start"
	@echo "obsidian         — open wiki in Obsidian"
	@echo "mcp              — start MCP server (local, used by Claude Code)"
	@echo "index-rebuild    — force full rebuild of the wiki search index"
	@echo "api              — start FastAPI backend directly (port 8000)"
	@echo "ui               — start Vite dev server directly (port 5173)"
	@echo "flashcards       — build each module's _flashcards.md from its local deck specs"
	@echo "install-ui       — npm install for app/"
	@echo "install-api      — uv sync --extra api"
	@echo "install-codemap  — uv sync --extra codemap"
	@echo "install-presenter — uv sync --extra presenter"
	@echo "codemap-reindex  — reindex repos in codemap repos.local.txt (else repos.txt) → .code_index.duckdb"
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
	@echo "wiki-stats       — print wiki health numbers"
	@echo "wiki-snapshot    — wiki-stats + one dated row in data/telemetry/metrics.jsonl"
	@echo "wiki-check       — private-leak check (exit 1 on a link into private/ or a tracked private file)"
	@echo "wiki-gaps        — regenerate data/telemetry/gaps.md and print the top five"
	@echo "wiki-graph       — hubs, bridges and consensus clusters of the wiki's link graph"
	@echo "eval             — run retrieval + answer graders over golden dataset; save baseline"
	@echo "eval-live        — eval the live sem arm (gated against its baseline); save live baseline"
	@echo "eval-nofts       — eval the degraded no-fts arm (gated); save nofts baseline"
	@echo "e2e-container    — build the image, run it with a token, e2e against it (tests/e2e/run_container.sh)"
	@echo "e2e-compose      — compose stack behind Caddy, 2 API replicas, e2e through TLS (tests/e2e/run_compose.sh)"
	@echo "eval-chat        — BILLABLE: chat answers on evals/golden_chat.json, LLM-judged (WARN-only; LIMIT=N)"
	@echo "eval-chat-dry    — the same, no API calls: plan and estimated cost"
	@echo "eval-gate        — run every gated live arm (sem, nofts, uniform, course, graph, multihop); no baseline written"

# Course checks: stdlib ports of the learn-ai-engineering scripts, run over data/courses/.
# Private lessons (data/courses/private/) are skipped and never named. Paths are relative to data/courses/.
chapter-check-all:  ## Hold the pillared courses to the chapter standard and programming/ to its metadata rules
	uv run librarian courses check chapters --all --strict

chapter-check:  ## Check notes against the chapter standard: make chapter-check PILLAR=data-analytics/06-applied-analyses [STRICT=1]
	@test -n "$(PILLAR)" || { echo "usage: make chapter-check PILLAR=<course>/<module> [STRICT=1]"; exit 1; }
	uv run librarian courses check chapters $(PILLAR) $(if $(STRICT),--strict)

skills-check:  ## Fail if a skill shared with learn-ai-engineering (chapter, papers, readings, curriculum) differs from its template; skips the sibling when absent
	uv run python -m librarian.tools.skillsync check

skills-sync:  ## Render .claude/_shared templates into both repos' shared skills (SIBLING=path to override ../learn-ai-engineering)
	uv run python -m librarian.tools.skillsync sync $(if $(SIBLING),--sibling $(SIBLING))

link-check:  ## Verify relative links in the public lessons resolve
	uv run librarian courses check links

curriculum:  ## Rebuild the curriculum map (.cache/) and print integration issues: make curriculum [PILLAR=data-science/01-classical-ml]
	uv run librarian courses check curriculum build
	uv run librarian courses check curriculum issues $(if $(PILLAR),--pillar $(PILLAR))

crosswalk:  ## Validate drill and round units and links, then regenerate .cache/crosswalk.md
	uv run librarian courses check crosswalk

crosswalk-check:  ## Validate drill and round units and links; fail if .cache/crosswalk.md is stale
	uv run librarian courses check crosswalk --check

import-courses:  ## Mirror learn-ai-engineering into data/courses/ (ARGS='--subject X --dry-run')
	uv run librarian courses import $(ARGS)

manifest-check:  ## Validate practice/manifest.yaml files where present (labs live in learn-ai-engineering)
	uv run librarian courses check manifest

drill-check:  ## Check drill schema: make drill-check [DRILL_PATH=programming/drills/sql]
	uv run librarian courses check drills $(DRILL_PATH)

review-findings:  ## Reviewer precision, open decisions and recurring faults from logs/review/findings.jsonl
	uv run librarian courses review findings report

signals:  ## Weekly review signals (reviewer log, flashcards, drills, wiki searches): make signals [WRITE=1]
	uv run librarian courses review signals $(if $(WRITE),--write)

smoke-labs:  ## Run a practice folder's labs headless: make smoke-labs FOLDER=<course>/<module>/practice
	@test -n "$(FOLDER)" || { echo "usage: make smoke-labs FOLDER=<course>/<module>/practice"; exit 1; }
	uv run librarian courses check smoke-labs $(FOLDER)
