.PHONY: viz ingest lint help

viz:
	open -a Obsidian $(PWD)/wiki

ingest:
	@echo "Run /ingest <path> via Claude Code"

lint:
	@echo "Run /lint via Claude Code"

help:
	@echo "viz    — open wiki in Obsidian graph view"
	@echo "ingest — reminder: use /ingest <path> in Claude Code"
	@echo "lint   — reminder: use /lint in Claude Code"
