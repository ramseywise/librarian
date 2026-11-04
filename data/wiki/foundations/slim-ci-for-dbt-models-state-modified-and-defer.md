---
title: "Slim CI for dbt Models: state:modified and defer"
tags: [foundations, pattern]
summary: "Build only what a pull request changed by comparing the project with the production manifest, resolve unselected parents from production with defer, write to a per-PR schema, and make the test check required so a failing test stops the merge."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Slim CI for dbt Models: state:modified and defer

Rebuilding everything on every pull request is slow on a real warehouse and unnecessary. The pieces below ran for real on dbt with DuckDB, in a small project with one warehouse file and one schema per environment.

## Environments without naming a schema

Models do not name a schema; a `CI_SCHEMA` environment variable picks it per run, so each pull request gets its own schema with no file edit. Anything that varies between deploys lives outside the code. A deploy from main leaves a `manifest.json`, the description of what production is now; keep it as an artefact.

## Select only what changed

`state:modified` compares the current project with the saved manifest and selects new and changed nodes; a trailing `+` adds everything downstream. Changing one model out of 12 resources selected 3 with `state:modified` (the model and its two tests) and 5 with `state:modified+` (adding the monthly model that reads it and the dashboard exposure that reads that). A change at the root, such as a staging model, selects 9 resources: a wide blast radius CI should show. Refresh the manifest on each deploy or the comparison is against an old picture.

## Defer to production

The changed model reads a parent that is not built in the PR schema. `--defer` with the production state resolves a `ref` from the manifest when the node is unselected and missing in the current environment: the PR reads real production data for what it did not change and writes only to its own schema. Compiled SQL read from `prod`, outputs landed in `pr_42`, and the totals differed (prod 108320, PR 98370) by exactly the refunds the change should remove, which is what a reviewer should look at (see [[Parallel Run and Reconcile at the Grain People Read]] for data diffs). Closing the PR drops the schema: a disposable environment. Caveats: limits applied only in development may select more data than expected, and tests with several parents may run across environments.

## Failing tests stop the merge

A second change grouped by one column too many, so a day had two rows. The model built, the `unique` test failed, dbt skipped everything downstream, the exit code was 1, and production still had 28 rows. Make the check required in branch rules, or a failure is only advice. Tests are covered in [[dbt Build Test Semantics, Severity and Source Freshness]].

## Other CI gates

- **DAG lint:** an orchestrator file that fails to load takes its schedule with it. The scheduler re-parses files repeatedly, so top-level work (a network call at import) runs every parse; a lint over the source found "work at the top level" and a dependency cycle without installing the orchestrator. A real loader test in an image matching production still belongs in CI. Add a check each time a mistake gets through.
- **Secrets:** keep them in the CI system or a secret manager, referenced by name via an environment variable; test: could the code be public right now? A pattern scan caught a password value and an access-key pattern while passing clean files. A hit needs rotation, not just a deleted line, since the value stays in history. Do not rely on log masking.
- **Catalog gate:** fail CI when a mart model has no owner or description ([[Metric Definitions, Exposures and a Manifest Catalog]]).
- **Green on a small sample** passes tests a year of data would fail; know what CI does not cover, and keep one check from raw input to final output.

## See Also
- [[dbt Build Test Semantics, Severity and Source Freshness]] — related
- [[dbt Layers, Materialisations and the ref Graph]] — prerequisite-for
- [[Lineage for Blast Radius and Rebuild Lists]] — related
- [[Infrastructure as Code Plans: Drift, Replacement and State]] — related
