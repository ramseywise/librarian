---
title: Q0–Q5 Quality Ladder
tags: [eval, llm, pattern]
summary: A six-level per-feature quality ladder (unit/schema → golden set → LLM judge → adversarial/safety → human acceptance → production monitoring) where every level is owned by name, judges are never the sole authority, and the golden set is written from the requirement before the function to avoid the own-oracle trap.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/playground/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/playground/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/skills/design-product/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-product/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-roadmap/SKILL.md
---

# Q0–Q5 Quality Ladder

akira's product-design skill gives every AI-touching requirement a quality plan on a fixed
ladder:

| Level | Check |
|---|---|
| Q0 | unit and schema tests |
| Q1 | golden set |
| Q2 | LLM judge |
| Q3 | adversarial / safety |
| Q4 | human acceptance |
| Q5 | production monitoring |

## Rules

- **Every level is owned by name.** Q3 in particular must be assigned to a named person —
  unowned adversarial testing does not happen. The roadmap stage files an issue for each
  unowned level.
- **Judges are never the sole authority.** Q2 sits between a golden set and humans, never
  in place of them.
- **The own-oracle trap:** a golden set written after the function encodes what the
  function does, not what it should do. Author it from the requirement *before* the code.
- Every roadmap issue carries its quality level; an AI issue whose eval corpus has zero
  rows is blocked by the issue that produces the rows.

## See Also
- [[Eval Maturity Ladder]] — alternative-to (a system-level maturity ladder; this one is per feature)
- [[Traffic-Gated Evaluation Ladder]] — related (which evaluation methods are available when)
- [[LLM-as-Judge Evaluation]] — part-of (Q2)
- [[Four-Stage Design Pipeline with Backflow]] — part-of (the product stage that assigns levels)
- [[Eval Ladder]] — alternative-to
