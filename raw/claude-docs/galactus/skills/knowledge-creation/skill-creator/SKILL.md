---
name: skill-creator
description: >
  Create new Claude Code skills or improve existing ones. Use when the user wants to build a new
  skill, refine an existing SKILL.md, or iterate based on test results. Triggers on: "make a skill
  for X", "create a /foo command", "improve this skill", "the skill isn't working right", "update
  the skill description", or whenever a workflow from this conversation should be captured as a
  reusable skill.
---

# Skill Creator

Help the user create or improve a Claude Code skill — a `SKILL.md` file that gives Claude
specialized instructions for a domain or workflow.

## Core loop

1. **Understand intent** — What should the skill enable? When should it trigger? What does good
   output look like? Extract answers from the conversation history first; ask only about gaps.

2. **Write SKILL.md** — Draft using the structure below. Under 300 lines; move long reference
   content to `references/` and link to it.

3. **Test with 2–3 prompts** — Spawn background agents (or run inline if unavailable), each with
   the skill loaded and a realistic user prompt. Show results to the user.

4. **Iterate** — Rewrite based on feedback. Repeat from step 3 until satisfied.

Stay flexible — if the user says "just vibe with me, no tests needed", skip step 3.

## SKILL.md structure

```markdown
---
name: skill-name
description: When to trigger (specific phrases + contexts). What it does.
---

# Title

One-sentence purpose.

## [Section per major concern]

Concrete, imperative rules. Explain the *why* behind non-obvious ones.

## Examples (optional)

Input → output for the most important case.
```

### Frontmatter

- `name`: matches directory name and slash command (`/skill-name`)
- `description`: what Claude reads to decide whether to invoke — be specific, include concrete
  trigger phrases. Claude tends to undertrigger, so make it slightly pushy: instead of "helps with
  dashboards", write "use whenever the user mentions dashboards, data viz, or wants to display
  metrics, even if they don't say 'dashboard'"

### Body

- Imperative mood ("Do X", "Never Y")
- Explain the *why* for non-obvious rules — models follow reasoning better than bare commands
- Skip sections that don't apply
- At ~300 lines, factor reference content into `references/<topic>.md` and link from SKILL.md

## Bundled resources

```
skill-name/
├── SKILL.md
├── references/    # Docs loaded on demand (include a ToC if >300 lines)
├── scripts/       # Executable helpers — run without loading into context
└── assets/        # Templates, static files
```

Scripts beat inline code for deterministic, repeatable operations — bundle them so every invocation
reuses rather than reinvents.

## Testing

Spawn a background agent per test case with:
- The skill path (so it loads SKILL.md)
- A realistic user prompt — concrete and specific, not abstract ("my boss sent me Q4 sales.xlsx and
  wants profit margin added" beats "add a column to a spreadsheet")
- Output saved somewhere reviewable

Run with-skill and without-skill (or old-vs-new skill) in the same turn. Review side by side; give
specific feedback ("the table section is missing" beats "not quite right").

## Iterating on skill quality

- **Generalise from failures** — don't overfit to the test cases; aim for the principle
- **Cut dead weight** — remove instructions that aren't improving output
- **Explain why, not just what** — reasoning is more robust than a list of MUSTs
- **Bundle repeated work** — if test runs all independently wrote the same helper, put it in
  `scripts/` and tell the skill to use it
