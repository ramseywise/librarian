# Skills Guide

Generic workflows (research/plan/execute/code-review phases, quick-commit, quick-pr,
compact-session, insights, sanyi, …) are **global** — they live in `~/.claude/skills/`
and load in every session. Never copy them here (`~/.claude/CLAUDE.md` → Config Layering).
The old `global/` copy of that set was removed 2026-07-17.

Phase artifacts: one doc per work item at `.claude/docs/plans/YYYY-MM-DD-<slug>.md`
with a `Status:` line — no SESSION.md, no in-progress/ (convention: `~/.claude/rules/docs.md`).

This directory holds **playground-specific** skills only:

| Skill | What it does |
|---|---|
| `adk-python` | Google ADK Python patterns for the VA projects |
| `agent-creation` | Agent scaffolding workflow |
| `eval-creation` | Eval suite creation workflow |
| `knowledge-creation` | Knowledge-base content workflow |
| `langgraph` | Project-specific LangGraph topology, state, and test conventions |
| `nextjs` | Next.js App Router architecture rules (ts_google_adk, librarian UI) |
| `planning/` | Planning helpers incl. `linear-spike` |
| `skill-eval` | Skill evaluation harness |
| `workflow` | Repo workflow map |
