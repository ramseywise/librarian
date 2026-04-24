# Plan: Research Agent — Note Quality + Batch Automation

**Date**: 2026-04-06
**Research**: `.claude/docs/research/research-agent-refactor.md`
**Status**: Execute complete, pending review + commit

## Goal

Refactor the research agent to produce higher-quality, practitioner-oriented notes with [[wikilinks]] throughout, page references, deprecation flagging, and project context awareness. Add batch processing with token limits for automated 4am cron runs.

## Steps

### Step 1: Project context system ✅
- Added `project_context_file` property + `load_project_context()` to `config.py`
- Created `obsidian/project_context.md` — active projects brief

### Step 2: Refactor prompts — 6-section template ✅
- New `SYSTEM_PROMPT` with deprecation flagging + project awareness + page ref rules
- New `_CHUNK_INSTRUCTIONS`: 6 sections (Summary, Research Questions, Methodology, Key Techniques with failure modes, Critical Assessment, Open Questions)
- New `_MERGE_INSTRUCTIONS`: consolidates chunks, [[wikilinks]] throughout, page refs throughout, inline connections (no standalone Connections section)
- `build_note_prompt()`: added `project_context` parameter
- `build_merge_prompt()`: added `project_context` parameter
- Removed old `NOTE_TEMPLATE`, old `_SECTION_INSTRUCTIONS`

### Step 3: Refactor agent — single merge pass ✅
- `process_pdf()` returns single `Note` (not dual)
- Uses `create_client()` from `shared/client.py` (fixes prior inconsistency)
- Loads project context at init
- Configurable `max_tokens` (constructor arg + `RESEARCH_MAX_TOKENS` env var)
- Single merge pass: chunks → one consolidated note

### Step 4: Batch processing + manifest ✅
- `--batch` mode: scans `readings_dir` recursively for `.pdf` files
- `--max-pdfs N` (default 5): caps PDFs per run to control token spend
- `--max-tokens N` (default 4096): caps output tokens per API call
- `--force`: re-process regardless of manifest
- `--dry-run`: list what would be processed
- SHA-256 manifest at `obsidian/.processed.json` for idempotency
- Per-file error isolation — one failure doesn't abort batch

### Step 5: System cron at 4am ✅
- `scripts/research-cron.sh` — shell wrapper with `RESEARCH_CRON_MAX_PDFS` + `RESEARCH_CRON_MAX_TOKENS` env var limits
- Crontab entry: `0 4 * * * /path/to/repo/scripts/research-cron.sh`
- Logs to `logs/research-cron.log`

### Step 6: Tests ✅
- Updated `test_agent.py`: single merge flow, project context injection, max_tokens config
- Updated `test_writer.py`: single note output
- Updated `test_models.py`: removed ProcessedResult test
- New `test_batch.py`: manifest I/O, hashing, unprocessed detection, force mode

## Verification
- 68/68 tests passing (4 deselected — pre-existing pdftotext-dependent tests)
- `models.py` and `writer.py` unchanged from HEAD (dual-note code added then removed)

## Files changed
| File | Status |
|------|--------|
| `src/agents/shared/config.py` | Modified |
| `src/agents/research/prompts.py` | Modified (major) |
| `src/agents/research/agent.py` | Modified |
| `src/agents/research/__main__.py` | Modified (major) |
| `.gitignore` | Modified |
| `obsidian/project_context.md` | New |
| `scripts/research-cron.sh` | New |
| `tests/research/test_batch.py` | New |
| `tests/research/test_agent.py` | Modified |
| `tests/research/test_writer.py` | Modified |
| `tests/research/test_models.py` | Modified |
