---
title: Skill Discovery Failure Modes
tags: [meta, llm, reference]
summary: Why a Claude Code skill silently fails to trigger or gets ignored — the shared ~15k-character description budget that drops skills with no warning, disable-model-invocation removing the description entirely, auto-formatted multi-line YAML, vague descriptions, name/casing mismatches, compaction forgetting — plus how to tune a description with near-miss negative trigger evals.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/skill-creator/references/gotchas.md
  - data/raw/claude-docs/guacamayo/skills/skill-creator/references/gotchas.md
  - data/raw/claude-docs/galactus/skills/skill-creator/references/frontmatter-and-discovery.md
  - data/raw/claude-docs/guacamayo/skills/skill-creator/references/frontmatter-and-discovery.md
  - data/raw/claude-docs/galactus/skills/skill-creator/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-19-skills-layer-audit.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-19-skills-layer-audit.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-3-design-skill-trio.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-3-design-skill-trio.md
---

# Skill Discovery Failure Modes

These are externally sourced skill-authoring notes (medium confidence), vendored as the
`skill-creator` references in galactus and guacamayo.

## How skills load

1. **Startup.** Name and description for every skill go into the system prompt (~100 tokens
   each).
2. **Trigger.** When a query matches a description, the full `SKILL.md` is read from disk.
3. **References.** Linked files are read only when needed.

So the description is the only part of a skill that is always present. Every failure below
comes down to the description being absent, unreadable or unpersuasive.

## Silent failures

- **Description budget starvation (the most dangerous).** All descriptions share a budget of
  about 2% of the context window (fallback ~15–16k characters), plus ~109 characters of
  overhead per skill. Past the budget, skills **silently drop out of context**, with no
  warning. Symptom: skills that used to work stop triggering after new ones are installed.
  For example, 60 skills × 200 characters ≈ 18.5k, which is over budget. In large
  collections, keep descriptions to 130–150 characters. An env override exists
  (`SLASH_COMMAND_TOOL_CHAR_BUDGET`).
- **`disable-model-invocation: true` removes the description entirely.** It does more than
  block auto-invocation: the model cannot see the skill exists unless the user types it.
  Right for side-effecting skills (deploy, commit, send), wrong if you only wanted "known
  but not auto-run."
- **Auto-formatted multi-line YAML descriptions** break discovery. Pin them with
  `# prettier-ignore`.

## Triage order when a skill never triggers

1. Budget exceeded?
2. YAML broken (multi-line, tabs, unclosed quotes)?
3. Description too vague ("helps with projects")?
4. Folder name ≠ `name` field?
5. File not exactly `SKILL.md`?
6. Wrong location?

**Quick probe:** ask "When would you use the X skill?" If the model doesn't know, the skill
isn't in its context.

## Triggers but is not followed

- **Done manually anyway.** Fix with more imperative steps, numbered phases and verification
  commands that force the workflow.
- **Ignored mid-task.** Put critical rules at the top, and move critical validation into
  scripts ("code is deterministic, language isn't").
- **Forgotten after compaction.** The skill body is not durable across a compaction.
- **Overtriggers.** Add negative triggers ("Do NOT use for …") and narrow the domain.

## Tuning a description with trigger evals

The skill-creator workflow optimises the description against about 20 realistic queries,
8–10 should-trigger and 8–10 should-not. **The valuable negatives are near-misses** that
share keywords with the skill but need something else. "Write a fibonacci function" as a
negative for a PDF skill tests nothing. Positives should cover casual and formal phrasing,
cases that never name the skill, and cases where the skill competes with another and should
win. "Bad eval queries lead to bad descriptions."

## Bundled-reference failures (skills-layer audit)

A global skills audit in guacamayo found failures *after* a skill triggers, in the
files it points to:

- **A dangling reference path fails silently.** A skill cited
  `references/schemas.md` three times and the file did not exist. Claude reads a
  missing path and carries on without the schema. Loading follows paths, not meaning.
  One missing file turned out to be six. The skill had been **vendored incompletely**
  from upstream, so its whole eval/benchmark half was non-functional.
- **Don't fake the repair.** Writing only the missing schema file would have invented
  a contract for consumers that were also missing, making the skill *look* fixed while
  it broke one step later. The fix was a complete re-vendor.
- **Re-vendoring is a merge, not a copy.** Diffing local against upstream showed
  upstream plus six additive local edits. One of those edits **corrected an upstream
  error**. A blind overwrite would have silently brought the error back.
- **`disable-model-invocation` can be deliberate.** 13 of 22 global skills carried it.
  The flag removes the description from context entirely, which saved about 1300
  always-on tokens. The audit first called it a bug, assuming skills invoke each
  other. No skill did: every "→ next skill" was prose for the human, across a session
  boundary. Check for a real call site before calling the flag a bug.
- **Split only the outliers.** One skill was four times the next largest and
  warranted progressive disclosure. Fifteen skills under ~760 words would only gain an
  extra hop.
- **Directory-name drift defeats sweeps.** One vendored skill used `reference/`
  (singular) where all others used `references/`, so the audit's own
  `find -path '*/references/*'` missed it.
- **Reproduce before you diagnose.** A phase skill that "did not route" had already
  produced one wrong diagnosis. The rule became: no skill-file edits until it has been
  reproduced in a fresh session.

A separate structural cause, where a skill never triggers because a dominant pipeline
absorbs its intent, is in [[Pipeline-Absorbed Skills]].

## See Also
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — extends (output-quality evals; this page covers trigger evals)
- [[SKILL.md Pattern]] — extends (the format whose frontmatter governs discovery)
- [[Capability vs Phase Skills]] — extends
- [[Claude Workflow System]] — extends
- [[Skill Authoring Discipline]] — prerequisite-for
- [[Pipeline-Absorbed Skills]] — extends (zero invocations from a structural bypass that description rewrites cannot fix)
- [[Dispatcher Carries the Skill Body]] — extends (`disable-model-invocation` also hides skills from subagents)
