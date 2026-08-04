---
title: Deterministic Review Substrate
tags: [llm, pattern]
summary: Review steps that are mechanical (diff scoping, dedup clustering, schema validation, report rendering) are pushed into a CLI the agent shells out to, so the only work left to LLM judgment is the part that actually needs judgment.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/agents/parallax.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/evidence-model.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/severity-and-decision.md
---

# Deterministic Review Substrate

Parallax's orchestrator prompt states the rule directly: several steps "are deterministic
and must be run as code (`parallax-cli <subcommand>`, piping a JSON payload on stdin), not
re-derived by reasoning about it yourself." The shared skill is blunter about why — where a
rule has a matching CLI subcommand, running it is "the one guarantee here that isn't just
'the model tried to remember the rule correctly.'"

This is the inverse of the usual prompt-engineering move. Rather than writing a longer
prompt to make the model follow a procedure reliably, the procedure is removed from the
prompt's jurisdiction entirely.

## What gets pushed into code

| Subcommand | Replaces the model doing… | Stage |
|---|---|---|
| `diff-scope` | reconstructing the staged/working-tree/branch fallback order | 1 |
| `detect-signals` | eyeballing files for agent-system markers | 1–2 |
| `validate-finding` | checking its own JSON against the schema by eye | 6 |
| `dedup` | reading every finding to spot overlapping ones | 7 step 1 |
| `sanyi-default-impact` | recalling a severity→impact mapping table from memory | 7 |
| `bucket` | sorting findings into report sections | 7 step 4 |
| `validate-report` | confirming the report is well-formed | 9 |
| `render-report` / `render-interview` | hand-formatting Markdown | 8–10 |

## The judgment boundary

The split is not "code does the easy parts." It is drawn at whether the step has a
correct answer independent of context.

`dedup` is the clearest case. It groups findings whose file paths and line ranges overlap
and whose category or symbols match — "purely mechanical, no judgment involved yet." The
model then judges, *within each returned cluster*, whether the findings "are actually the
same underlying issue or merely touch the same code for unrelated reasons." Clustering is
mechanical; deciding what a cluster means is not. The CLI hands the model a smaller,
better-posed question instead of the raw pile.

Same shape at Stage 1a: style, naming, and formatting are checked by the repository's own
linter, and "no dispatched skill's dimensions check for them on purpose." If no linter is
configured, the instruction is explicitly *not* to emulate one with LLM judgment — record
"no static analysis tool detected," declare that layer out of scope, and recommend the
human add one. A deterministic check that cannot run is reported as a gap, never
approximated.

## Suggestion, not override

Determinism is scoped so it doesn't overrule the humans or the reasoning it feeds.
`detect-signals` returning `triggered: true` is "a recommendation to activate the
Agent-System Extension, not an override of what the human already stated — but it beats
guessing when nothing was stated." `sanyi-default-impact` yields "a starting suggestion
the orchestrator (or a human) may still override," not a fixed verdict.

The tool output enters as evidence with a known provenance, which is also how static
analysis results are handled — surfaced "verbatim later in the report's Static Analysis
section — tagged as tool-verified evidence, never merged into or re-derived as a subagent
finding." Tool-verified and model-asserted claims never blend into one undifferentiated
stream. This is the same separation [[Evidence Classification Model]] applies to the
model's own claims.

## Relation to prompt-only review systems

The guacamayo `/akira` scanners in [[Parallel Dimension Scanner Architecture]] encode
comparable rules — fixed severity mappings, mandatory self-verification — but as prompt
instructions the agent is asked to follow. Parallax moves the same class of rule behind an
executable. The tradeoff is a build-and-install step (`uv tool install --editable .`,
once, globally so it works from the reviewed repo's directory) against per-run variance in
whether the rule was applied at all.

## See Also
- [[Evidence Classification Model]] — prerequisite-for
- [[Source Severity vs Merge Impact]] — extends
- [[Parallel Dimension Scanner Architecture]] — alternative-to
- [[Merge Impact and Evidence State]] — extends
- [[SANYI Change-Contract System]] — instance-of
- [[Corrective Follow-Up Dispatch]] — extends (reviewer signal as fallback when `detect-signals` misses)
- [[Shared Context Brief]] — extends (tool output recorded verbatim in the brief and report)
- [[Parallax]] — instance-of (the system this substrate belongs to)
