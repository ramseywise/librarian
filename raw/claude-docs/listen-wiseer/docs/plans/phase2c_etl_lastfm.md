# Plan: Phase 2c — ETL Rebuild + Last.fm Integration
Status: COMPLETE (see CHANGELOG.md [0.4.0])

## Goal
Harden ETL, add Last.fm enrichment, wire pre-commit hooks.

## What was built
- **Last.fm API integration** (`src/etl/sync.py`) — enriches tracks with play count, listener count, tags
- 227-test suite (`tests/unit/test_lastfm.py`, `tests/unit/test_sync.py`)
- **Pre-commit config** (`.pre-commit-config.yaml`) — ruff lint/format + pyright hooks
- **ETL rewrite** (`src/etl/bootstrap.py`, `sync.py`, `loader.py`)
- **Spotify client refactor** (`src/spotify/fetch.py`, `auth.py`, `client.py`)
- **`.claude/` skills and commands** — research_synthesis, review_validate_plan, full CLAUDE.md expansion
