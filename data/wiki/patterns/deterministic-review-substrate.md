---
title: Deterministic Review Substrate
tags: [llm, pattern]
summary: Review steps that are mechanical (diff scoping, dedup clustering, schema validation, report rendering) are pushed into a CLI the agent shells out to, so the only work left to LLM judgment is the part that actually needs judgment.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/Parallax/agents/parallax.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/evidence-model.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/severity-and-decision.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-GUA-23-review-backbone.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-GUA-23-review-backbone.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-review-agent-system-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-review-agent-system-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-24-GUA-18-19-finding-schema-merge.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-24-GUA-18-19-finding-schema-merge.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-60-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-60-plan.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-62-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-62-plan.md
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


## Adoption in guacamayo: build the backbone, don't fork

guacamayo's review system adopted this substrate as its own Python CLI rather than forking
Parallax. The options weighed were:

- **(A)** Extend the markdown skills only. Dedup, validation and rendering stay
  prompt-based, and the motivating failure (a plan marked DONE with most steps
  uncommitted) has no deterministic fix.
- **(B)** A full agent framework (LangGraph/ADK). Overkill.
- **(C)** A deterministic backbone. **Chosen.**
- **(D)** Fork Parallax. Rejected, because it is coupled to Parallax's seven-subagent
  model.

The schema took roughly 60% of Parallax's fields. Phase 1 shipped:

- Pydantic finding/report models with a `{SRC}-{NNN}` ID pattern and 10 category values.
- Union-find dedup with a 5-line tolerance.
- `verify-commits` ([[Plan Step Done Requires a Commit]]), a stage Parallax does not
  have.

Install is `uv tool install -e`. The external reference point was layered determinism in
commercial reviewers, where about 60–70% of findings are handled before any LLM call.

A follow-up (planned) moved the next rule set out of prose:

- **The SANYI violation-code → merge-impact mapping** (11 codes) becomes testable Python
  that raises on an unknown code instead of quietly defaulting.
- **Merge logic** was written out in prose in three places that had drifted. It moves into
  one shared skill.

The split stays: clustering is deterministic, judging duplicates is the LLM's job, and
merge rules are deterministic again.

## From a CLI the agent calls to a driver that owns the pipeline (guacamayo)

guacamayo took the next step. A Python driver (`review-cli run`) **owns** the review
pipeline: detect signals, spawn dimension agents concurrently through the Claude Agent
SDK, validate, dedup, fingerprint, persist the sweep, diff trends and render. Skills
shrink to "compute scope, run the driver, present the report".

- **Why not a Claude Code workflow script.** Workflow scripts have no filesystem or
  subprocess access, so the gates would run inside agents through Bash, which is
  LLM-mediated again. "Validation is unskippable" holds by construction only in Python
  control flow.
- **Enforce output shape on the driver side.** The SDK's native JSON-schema output
  option enforces the findings shape per query. The six agent markdown files are not
  edited and keep their markdown format for interactive use, so there is zero drift
  surface. An invalid finding gets one repair round-trip, then the run fails non-zero.
  It is never silently dropped.
- **An injectable scan function** makes every gate testable with pytest and no LLM.
- **Never fall back to prose orchestration** when the SDK or CLI is unavailable. Fail
  fast with a clear error.
- **Static analysis as a driver stage, excluded by type rather than by filter.** Lint
  output is a separate `StaticAnalysisResult` model, never a `ReviewFinding`, so it
  cannot reach dedup or sweep persistence. The test asserts the structural property:
  a run with lint violations produces the same merged findings as one without. The
  stage never blocks dispatch and does not touch the merge verdict, since pre-commit
  already gates style. Commands are literal per-tool constants run with
  `shell=False`, and a test asserts that no command contains `--fix`, `--write` or
  `format`. Detect the **linter, not the hook runner**: `pre-commit run` would apply the
  repo's `--fix` hooks and write to the tree. "Not detected" and "configured but not
  installed" are reported separately because their remediations differ. Raw output is
  truncated with an explicit "N more not shown" line, never a silent cap.

The driver's first review found it silently losing findings in its own dedup step.
See [[Paired Bugs That Cancel]].

## See Also
- [[Evidence Classification Model]] — prerequisite-for
- [[Source Severity vs Merge Impact]] — extends
- [[Parallel Dimension Scanner Architecture]] — alternative-to
- [[Merge Impact and Evidence State]] — extends
- [[SANYI Change-Contract System]] — instance-of
- [[Corrective Follow-Up Dispatch]] — extends (reviewer signal as fallback when `detect-signals` misses)
- [[Shared Context Brief]] — extends (tool output recorded verbatim in the brief and report)
- [[Parallax]] — instance-of (the system this substrate belongs to)
- [[Artifact Is Not Evidence: Push and Probe]] — related (tool output over prose, applied to deploy verification)
- [[Re-Scope Over Sequence for Colliding Issues]] — related (a review pass that re-cut issues by file ownership)
- [[Rationale-Blind Worst-Case Review]] — extends (a read-only consequence reporter feeding the same verdict)
- [[Cross-Sweep Finding Fingerprint]] — extends (deterministic identity and trend rules over the findings)
- [[Deterministic Signal Detection for Dispatch]] — extends (determinism applied before review, at dispatch)
- [[Derive the Gate, Don't Copy It]] — extends (how the gate summary handed to reviewers stays honest)
- [[Always-Red Check Carries No Signal]] — extends (when the deterministic layer itself stops carrying information)
- [[Single Typed Verdict, Consumers Never Re-Derive]] — extends (three drifting verdict implementations collapsed into one pure function)
- [[Plan Step Done Requires a Commit]] — extends (the commit-verification stage this substrate added)
- [[Paired Bugs That Cancel]] — related (the finding-loss defect found in the driver's first review)
