---
title: Assumption Audit
tags: [llm, pattern]
summary: Extract every load-bearing assumption from a plan before evaluating any of them — including the ones hiding in confident language, in defaults, in dependencies and in what the plan does not mention — then rank by cheapest-check-for-worst-consequence rather than by how likely each is to hold.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/assumption-audit/SKILL.md
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
---

# Assumption Audit

`/assumption-audit` (`job: frame`, capability skill, report-only) exists because the
natural way to read a plan — nodding along and objecting where something feels wrong — is
exactly the process that lets a load-bearing guess through. Evaluating as you read means
the first plausible assumption anchors the rest.

## Extract first, evaluate second

Pass one produces a flat list of claims the plan depends on, with no judgement attached.
Pass two evaluates. Separating them is the whole method: an assumption you have already
agreed with is one you will not list.

## Four hiding places

| Where | Tell |
|---|---|
| **Confident language** | "obviously", "simply", "just", "the standard approach" — certainty words marking the spot where no argument was made |
| **Defaults** | a config value, a library choice, a threshold nobody chose; see [[Profile Then Select]] on named-source vs default values |
| **Dependencies** | "the API returns…", "the team will have…", "the data includes…" — a claim about something outside the plan's control |
| **Absence** | what the plan does not discuss: failure handling, rollback, the empty case, who is paged |

The fourth is the one that needs the counterfactual move: for each section, ask *what
would have to be true for this to work that the author did not write down?*

## Evaluate by cost of being wrong, not probability of being right

Each extracted assumption becomes an `AA-NNN` claim in the [[Two-Axis Claim Schema]] with
a `check` whose `settles` field is mandatory. Ranking is `decision_impact` first,
`confidence` second, cheaper check breaks ties. The `speculative × fatal` cell goes to the
top of the report even when the author believes the assumption is probably fine — because
"probably fine" is the confidence axis and the report is sorted on the other one.

## Failure modes of the audit itself

- **Listing facts as assumptions** — a verified, cited statement is not an assumption;
  padding the list with them buries the real ones.
- **Evaluating during extraction** — see above.
- **Checks without settling criteria** — "verify the API" is a task, not a check.
- **Resolving instead of reporting** — the skill never edits the plan; the human decides
  what to do with `AA-` items (see [[Capability vs Phase Skills]]).

## See Also
- [[Two-Axis Claim Schema]] — prerequisite-for
- [[Capability vs Phase Skills]] — instance-of
- [[Derived-and-Hidden Design Decisions]] — extends (the "defaults" and "absence" hiding places are where derived decisions live)
- [[Collapse Site Detection]] — alternative-to (sibling frame skill: unknowns rather than assumptions)
- [[Deferred Decision Status]] — extends (an audited assumption with a revisit trigger becomes a deferral)
- [[Verify the Issue's Premise Before Planning]] — extends (worked instances: issue premises and risk-section mitigations that did not exist)
