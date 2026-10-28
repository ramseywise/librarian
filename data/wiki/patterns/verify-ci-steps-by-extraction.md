---
title: Verify CI Steps by Extraction, Not Retyping
tags: [infra, pattern]
summary: "A CI shell step passes through YAML, the runner's expression parser, and bash before it executes — so test it by parsing the step out of the workflow file and running it verbatim, paired with a negative control, because a hand-retyped version escapes differently and a filter that stopped matching reports clean."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-18-template-full-mirror-redesign.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-18-template-full-mirror-redesign.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-cicd-standardization.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-cicd-standardization.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-g1-scheduled-ingestion.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis40-scheduled-ingestion.md
---

# Verify CI Steps by Extraction, Not Retyping

The ai-project-template's render CI greps every rendered project for leftover `{{` (an
unrendered Jinja marker). A rendered GitHub Actions file legitimately contains `${{
github.actor }}`, so the check false-positived and had to learn to ignore Actions'
expression syntax. The fix took three attempts; the first two looked right in the file,
passed a hand-typed shell test, and were dead.

## Three layers, three silent failures

1. **Literal `${{` in a `run:` block** — Actions parses it as an unclosed expression; the
   workflow fails to parse before any grep runs.
2. **`\|\${{` via a variable** — in `grep -v`, an unescaped `$` is the end-of-line
   anchor; the alternative matched nothing and the false positive silently returned.
3. **`\${DOLLAR}{{`** — `\$` is not a YAML escape; YAML passes it through, bash's double
   quotes treat `\$` as literal, `DOLLAR` never expands. A zsh spot-check "passed" because
   zsh resolved the escaping differently from the YAML → bash path.

The landed form sidesteps every layer: put the pattern in `env:` (nothing escapes it
there) and use a character class instead of an escape — `ACTIONS_EXPR: '[$]{{'`.

## The rule

- **Extract and execute.** Load the workflow with `yaml.safe_load`, pull the step's
  `run:` string, and run it verbatim under the same shell. Never retype it.
- **Pair every filter change with a negative control.** Feed the filter one input it
  must still catch. Two of the three broken attempts produced a clean run *because* the
  filter had stopped matching anything.
- **Filter by pattern, not by excluding whole files.** Excluding a file wholesale also
  stops checking its real substitutions.
- **Reword the prose, don't grow the filter.** The one genuine leftover-Jinja hit was a
  skill doc that wrote a literal `{{ }}` while explaining Jinja; rewording it beat adding
  another brittle exclusion.

## The runner's shell flags: `cmd; rc=$?` never reaches `rc` (akira)

A scheduled importer's plan mapped exit code 2 (spend cap reached, an expected partial
run) to a warning instead of a failure:
`npm run import; rc=$?; [ $rc -eq 2 ] && echo "::warning::..." || exit $rc`. That snippet
cannot work. GitHub Actions runs `run:` steps as `bash --noprofile --norc -eo pipefail
{0}`. Under `set -e`, a failing bare command aborts the script before `rc=$?` runs, so
exit 2 went red exactly like exit 1. That is the outcome the step existed to prevent.
`bash -eo pipefail -c 'false; rc=$?; echo got here'` never prints.

**Fix:** `npm run import || rc=$?; [ "${rc:-0}" -eq 2 ] && echo "::warning::..." || exit
"${rc:-0}"`. A command on the left of `||` is exempt from `-e`.

**Test:** the suite reads the workflow YAML, extracts the step's actual `run:` string,
and executes it under the runner's own invocation (`bash --noprofile --norc -eo pipefail
-c`). A stub `npm` on `PATH` exits 0, 1 and 2. The test was confirmed to fail against the
original snippet. A TypeScript re-implementation of the mapping was deliberately not
written, because it would test a module the workflow never runs. The
run-record defects found in the same job are in [[The Run Record Belongs to the Process]].

## Related CI defects from the same repos

- **Cache keyed on a file that cannot exist.** `setup-uv` with `enable-cache: true` keys
  on `**/uv.lock`; a copier template root has no lockfile until after render, so the
  render workflow failed on every PR. The first hypothesis (a checkout action bump) was
  disproven by reading the log.
- **A workflow that has never run is not passing.** One render workflow had been
  "green" only because the repo had no remote and no commits; the first real run exposed
  lint failures in vendored code.

## See Also
- [[Execute Every Toggle Configuration]] — extends (the same false-green class at the render layer)
- [[Paired Allow Test for Deny Rules]] — extends (negative controls for rules that can rot to match nothing)
- [[Silence Reads as Clean]] — instance-of
- [[An Unrun Scan Is Not a Clean Scan]] — related
- [[AI Project Template Scaffold]] — instance-of
- [[Skip Steps, Not Jobs, Behind a Path Filter]] — related (a negated path filter is verifiable only by a real mixed-commit push)
- [[The Run Record Belongs to the Process]] — extends (the same scheduled job's run-history defects)
