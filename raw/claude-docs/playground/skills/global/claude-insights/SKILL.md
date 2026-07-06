---
name: claude-insights
description: "Cartographer analysis: session notes are the canonical source for the HTML insights report; JSONL enriches when available. Includes migration from JSONL and a comparison view to validate note coverage."
disable-model-invocation: true
---

Surface workflow improvements from session notes written by `/compact-session`. JSONL enriches when available but is not required.

If `$ARGUMENTS` is `skills-only`, skip to section 2.

## Data sources and philosophy

Session notes are the canonical, portable source — they work on any machine (local, cord) and capture qualitative context JSONL never can. JSONL is supplementary until there's a centralized store.

| Layer | Path | Written by | Role |
|-------|------|-----------|------|
| Session notes | `.claude/sessions/*.md` | `/compact-session` | **Primary** — always write these |
| Session JSONL | `~/.claude/projects/**/*.jsonl` | Claude Code (per machine) | **Enrichment** — quantitative stats when present |
| Friction log | `.claude/friction-log.jsonl` | PostToolUse Bash hook | **Cron only** — local friction patterns |

**Implication**: always end sessions with `/compact-session`. The HTML report is only as good as the notes you've written.

---

## 1. HTML insights report

```bash
uv run cartographer --dry-run    # stats only (JSON → stdout), no API call
uv run cartographer              # HTML → .claude/docs/insights/report.html
```

### Source routing

| Session notes | JSONL | Mode |
|:---:|:---:|------|
| ✅ | ✅ | Notes as primary + JSONL quantitative enrichment |
| ✅ | ❌ | Notes only (cord / any machine) |
| ❌ | ✅ | JSONL only — run `--migrate` first to create notes |
| ❌ | ❌ | Error |

### Report sections

| Section | Primary source |
|---------|---------------|
| What You Work On | Notes (work field) / JSONL (project paths) |
| How You Use Claude Code | JSONL (tool ratios, response times) + notes (key tools) |
| Wins | Both |
| Friction | Notes (friction signals, attribution) + JSONL (error counts) |
| Features to Try | Derived from friction patterns |
| New Patterns | Notes (session insights, skill candidates) |
| On the Horizon | Notes (skill candidates) + both |

---

## 2. Friction analysis + skill suggestions (local artifacts)

```bash
uv run cartographer --cron      # → .claude/docs/insights/{date}.md
```

Reads `.claude/sessions/` + `.claude/friction-log.jsonl`. Outputs a markdown report with:
- Workflow insights (signal → interpretation → recommendation)
- GENERATE / SKIP / MERGE verdict on skill candidates from session notes
- Auto-writes approved skills to `.claude/skills/`

---

## 3. Migrate JSONL history to session notes

First-time setup: convert existing JSONL sessions into skeleton notes so history isn't lost.

```bash
uv run cartographer --migrate    # creates .claude/sessions/{date}T{hhmm}.md per JSONL session
                                 # skips dates where a note already exists
```

Generated notes have quantitative fields filled (tools, tokens, files, duration, first prompt) and qualitative fields left as placeholders. Edit them to add gotchas, attribution, and skill candidates.

---

## 4. Compare JSONL vs session notes

Validate that your session notes are capturing what matters — or find gaps.

```bash
uv run cartographer --compare                           # diff to stdout
uv run cartographer --compare --output .claude/docs/insights/compare.md
```

Output is a per-date table showing what each source captured, what's missing, and whether key fields (gotchas, attribution, skill candidates) were filled in.

---

### Signal taxonomy

#### Context engineering (CE) — are the right augmentation tools being used?

| Signal | Field | Threshold | Interpretation | Attribution |
|--------|-------|-----------|---------------|-------------|
| Bash antipatterns | `bash_antipatterns` | >1/session | Shell used where Read/Grep/Glob exists | Missing tool awareness; wastes context |
| No skill invocations | `skill_invocations` | empty | Skills exist but aren't being triggered | Skills not discoverable or scoped wrong |
| Low read/edit ratio | `read_edit_ratio` | <1.0 | Editing without reading first | Overconfident plan steps |
| Hook blocks absent | `hook_blocks` | 0 across sessions | Hooks may be misconfigured or not firing | Check `settings.json` hook matchers |
| Long sessions, no TodoWrite | `long_sessions_without_todo` | >0 | No planning structure on complex tasks | Skill or habit gap |
| Low cache hit rate | `cache_read_tokens` | near 0 | Context not being reused across turns | CLAUDE.md / memory not primed correctly |
| Compact triggers | (friction log) | 3+/session | Context too dense per phase | CLAUDE.md verbosity or phase boundaries |
| Skill candidates accumulating | (session notes) | 3+ unprocessed | Automatable pattern without a trigger | Skill candidate |

#### Prompt engineering (PE) — are outputs appropriately sized and well-directed?

| Signal | Field | Threshold | Interpretation | Attribution |
|--------|-------|-----------|---------------|-------------|
| High output tokens/msg | `output_tokens_per_msg` p75 | >800 | Verbose responses; consider brevity instruction or lower max_tokens | Prompt missing scope constraint |
| User interruptions | `user_interruptions` | >3/session | Intent unclear upfront | Prompt ambiguity |
| `edit_failed` / `file_not_found` | `tool_errors` | >2/session | Prompts producing wrong file paths | Plan phase — paths not verified |
| `user_rejected` errors | `tool_errors` | >1/session | Permissions too tight or unexpected scope | Settings / permissions |
| Input token growth | `input_tokens` | >20% week-over-week | Context bloat | CLAUDE.md density or memory verbosity |

### Recommendation categories

| Category | Action |
|----------|--------|
| **Hook** | Add/modify `settings.json` PreToolUse or PostToolUse entry |
| **Skill** | Create `.claude/skills/<name>/SKILL.md` |
| **Condense** | Merge overlapping skills or trim verbose ones |
| **Session preference** | Update compact trigger, note format, or memory convention |
| **CLAUDE.md** | Tighten or expand project operating rules |
| **Settings** | Update model, permissions, env, or timeout values |

For each pattern: **Signal** (numbers) → **Interpretation** → **Recommendation** (category + one concrete change) → **Attribution** (root cause). Limit to 3-5 patterns.

---

## Output

Terse table: `| Area | Signal | Recommendation category | Action taken |`
