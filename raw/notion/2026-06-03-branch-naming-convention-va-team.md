# Branch Naming Convention — Virtual Assistant Team

**Source:** https://app.notion.com/p/372f148b3ab7808e975aebbdfb5d6f93
**Last edited:** 2026-06-03
**Project:** Virtual Assistant
**Type:** Documentation

## Why a branch naming convention?

As the Virtual Assistant team grows across multiple repos, inconsistent branch names make it harder to trace work back to Linear tickets, understand the nature of a change at a glance, or automate parts of the CI/CD pipeline. A shared convention brings:

- **Traceability** — every branch is instantly linked to a Linear ticket
- **Clarity** — the type prefix tells you the nature of the change before opening a PR (`feat` vs `fix` vs `infra` are very different scopes of review)
- **Consistency** — onboarding is faster when rules are the same across `va-agents` and `project-g`

## Repositories

- `product-a-webapp` — Frontend
- `va-agents` — Backend / AI agents
- `project-g` — Data science / Eval pipeline

## Format

```
<type>-VIR-XXX-short-description
```

- **`type`** — the nature of the change (see tables below, per repo)
- **`VIR-XXX`** — the Linear ticket identifier, copied directly from Linear
- **`short-description`** — a short slug in kebab-case, max 4–5 words

> Tip: on any Linear ticket, click "Copy git branch name" — it generates a slug like `vir-215-adding-eslint-rules`. Prepend the type: `chore-VIR-215-adding-eslint-rules`.

## `va-agents` — Backend / AI agents

Next.js backend powering the Virtual Assistant: agent orchestration, Langfuse prompt management, invoice/quote/customer tooling, AWS/ECS infrastructure.

| Type | When to use | Example |
|---|---|---|
| `feat` | New agent capability or business feature | `feat-VIR-310-create-quote-agent` |
| `fix` | Bug fix on an agent, tool, or API route | `fix-VIR-215-invoice-summary-crash` |
| `prompt` | Modification of a system prompt | `prompt-VIR-198-virtual-assistant-system` |
| `refactor` | Code restructuring with no functional change | `refactor-VIR-222-agent-routing-cleanup` |
| `chore` | Dependencies, config, tooling, CI | `chore-VIR-201-upgrade-langfuse-sdk` |
| `infra` | AWS, ECS, Docker, environment config | `infra-VIR-175-ecs-task-healthcheck` |
| `test` | Adding or fixing tests | `test-VIR-230-invoice-agent-unit-tests` |

`prompt` is specific to `va-agents` — prompt changes have a distinct review/deployment lifecycle from code and deserve their own visibility.

### Exception — `hotfix`

Used when a critical bug is blocking users in production and no existing branch can absorb the fix. The only type that branches directly off `main`.

```
hotfix-short-description
```

Use when: the bug actively blocks users (payment failure, crash, data loss), no open feature branch can absorb it, and the fix must ship without waiting for the normal cycle. Must be merged back into `main` to avoid being overwritten by the next release.

## `project-g` — Data science / Eval pipeline

Evaluation, experimentation, and enablement repo for the VA team. Ingests data from product-a/Intercom, runs multi-layer LLM evaluations, hosts agent prototypes (LangGraph, Google ADK, RAG).

| Type | When to use | Example |
|---|---|---|
| `eval` | New grader, eval pipeline, or runner | `eval-VIR-301-add-friction-grader` |
| `data` | Data ingestion, PII scrubbing, dataset prep | `data-VIR-288-intercom-pii-scrub-pipeline` |
| `exp` | Experiment or prototype that may not merge | `exp-VIR-295-langgraph-vs-adk-ablation` |
| `nb` | Analysis notebook (`nbks/`) | `nb-VIR-277-golden-traces-analysis` |
| `fix` | Bug fix in a pipeline, grader, or script | `fix-VIR-312-mrr-score-off-by-one` |
| `refactor` | Refactoring with no change in eval output | `refactor-VIR-299-ragas-grader-cleanup` |
| `chore` | Dependencies, Makefile, env config | `chore-VIR-305-upgrade-deepeval` |
| `test` | Regression gates, capability tests | `test-VIR-320-bkh-regression-harness` |

`exp` matters in a data science context — some branches are explorations that may be abandoned. Distinguishing them from `feat` avoids polluting PR history with unfinished work.
