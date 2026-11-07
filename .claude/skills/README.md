# Skills by product

Claude Code finds a skill only at `.claude/skills/<name>/SKILL.md`, one level deep, so the
directories stay flat and the grouping lives here. Invocation names are unchanged. A skill keeps
the judgement and the order; anything a script can decide is a `librarian` verb the skill calls.

## Wiki (compile, query and maintain `data/wiki/`)

| Skill | Calls these verbs |
|---|---|
| `ingest` | `ingest lint-raw`, `ingest triage`, `wiki index-add`, `wiki verify`, `ingest mark`, `wiki relink`, `wiki check`, `wiki log` |
| `learn` | the `ingest` verbs, scoped to `data/raw/web/` |
| `seed-kb` | `scrape sessions\|bookmarks`, then `ingest` |
| `lint` | `wiki stats --json`, `wiki lint`, `wiki check` |
| `query`, `write`, `challenge`, `quiz` | wiki search only; `wiki ask` records an unanswered question |
| `compact-wiki` | `wiki stats`, `wiki relink` |
| `gaps` | `wiki gaps` |
| `wiki-weekly` | `wiki snapshot`, `wiki stats` |
| `wiki-graph` | `wiki graph` |
| `wiki-rename` | `wiki rename` |
| `wiki-sync` | read-only taxonomy audit |

## Course (author and review `data/courses/`)

`curriculum`, `pillar`, `practice`, `review`, `slides`, `weekly`, `write-chapter`. Verbs: `courses check ...`,
`courses review ...`.

Reading-queue skills `chapter`, `papers`, `readings` live here but drive the `scripts/papers/` tooling
(`potw.py`, ledger, inbox), which exists only in the learn-ai-engineering repo, not in this one. They
say "Run from the learn-ai-engineering repo" and that is still true; the notes they edit are in
`data/courses/` here.

## Build (agent projects, outside the wiki)

`adk-context`, `harness-audit`, `evals-bootstrap`, `codemap` (`codemap` entry point and the MCP
code-index tools).

## Provided elsewhere

`new-agent`, `fog` and `review-defense` show up in the skill list but are not in this repo's
`.claude/skills/`; they come from the global config or plugins.

## Unattended runs

`librarian jobs list` shows the jobs; `librarian jobs run <name>` runs one headless through the
Agent SDK with the same skills (`feeds-ingest` = scrape then `/learn`, `wiki-weekly`, `weekly`) and a
restricted tool list that excludes git commits and pushes. Run `librarian jobs run <name> --dry-run`
to print the prompt and tools without calling the model. Nothing is installed by the repo; the examples below are for you to adapt by hand.

Crontab (weekly wiki review, Mondays 08:00):

```
0 8 * * 1 cd /absolute/path/to/librarian && /opt/homebrew/bin/uv run --extra jobs librarian jobs run wiki-weekly >> logs/jobs.out 2>&1
```

launchd, `~/Library/LaunchAgents/com.example.librarian-wiki-weekly.plist` (load with `launchctl load`
yourself; this repo never does):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.librarian-wiki-weekly</string>
  <key>WorkingDirectory</key><string>/absolute/path/to/librarian</string>
  <key>ProgramArguments</key><array>
    <string>/opt/homebrew/bin/uv</string><string>run</string><string>--extra</string><string>jobs</string>
    <string>librarian</string><string>jobs</string><string>run</string><string>wiki-weekly</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer>
  </dict>
  <key>StandardOutPath</key><string>/absolute/path/to/librarian/logs/jobs.out</string>
  <key>StandardErrorPath</key><string>/absolute/path/to/librarian/logs/jobs.out</string>
</dict></plist>
```

The agent needs `ANTHROPIC_API_KEY` (or a logged-in Claude Code) in the job's environment.
Each run appends a row to `logs/jobs.jsonl` (outcome, turns, cost, denied tool calls).

## Checks

`tests/skills/test_skill_contract.py` checks section order, description and output templates for
the contract skills offline. Each `evals/evals.json` holds trigger examples for the skill-creator
harness, which needs a model and is not run in CI.
