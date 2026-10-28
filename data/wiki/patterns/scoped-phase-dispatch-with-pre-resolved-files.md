---
title: Scoped Phase Dispatch with Pre-Resolved Files
tags: [llm, pattern]
summary: Dispatch one build agent per plan phase with a pre-resolved `Files:` list that is a floor, not a fence — the agent may read beyond it but must write only inside it — and apply the repo's documentation definition-of-done at execute time, because telemetry showed stale docs were 28% of all review findings when the DoD lived only in the reviewer's head.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/playground/agents/build-scout.md
  - data/raw/claude-docs/akira/agents/build-scout.md
  - data/raw/claude-docs/kiez-archive/agents/build-scout.md
  - data/raw/claude-docs/akira/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/diskoe/agents/build-scout.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-02-agent-pipeline-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-09-02-agent-pipeline-audit.md
---

# Scoped Phase Dispatch with Pre-Resolved Files

A build-stage subagent design from the akira workflow pipeline (`/workflow-triage →
/workflow-build → /workflow-review`). The orchestrator never hands an agent the whole
plan. It hands it **one phase**, with the plan's file references already resolved to
paths that exist on disk.

## The mechanism

- **One phase per dispatch.** The brief names the phase, the acceptance check, and a
  `Files:` block. The agent writes nothing outside that block; anything the phase turns
  out to need beyond it is reported back as a scope finding, not silently edited.
- **`Files:` is a floor, not a fence on reading.** The agent is expected to read
  neighbours, tests, callers, and the docs that mention the touched paths. Only the
  *write* set is bounded. This keeps the orchestrator's pre-resolution from becoming a
  blindfold.
- **Pre-resolution happens upstream.** The orchestrator checks each path exists before
  dispatch. A plan step that names a file which is not in the tree is a plan defect —
  the same stance as [[No-Placeholder Plan Discipline]] — and goes back to planning, not
  to the build agent to improvise.
- **Documentation DoD runs here, not at review.** The repo's change → doc table (which
  README, roadmap row, design-of-record section must move with which kind of change) is
  applied by the build agent as part of the phase, and the touched docs are listed in
  its report.

## Why the DoD moved to execute

The pipeline's own telemetry audit found that **13 of 45 unique review findings were
stale README / spec / design-of-record content** — one branch had 5 of 6 findings in
that class, another 3 of 4, all "doc asserted pre-change reality". The DoD table existed
and was correct, but no plan skill, build skill, or scout agent referenced it:

```
grep -l "roadmap.md\|design-requirements.md" .claude/skills/workflow-*/ .claude/agents/
→ (nothing)
```

Execute never applied it, so review rediscovered it on every branch. Wiring the table
into the build agent was ranked the highest-leverage fix in the audit: it removes the
finding class at source rather than catching it one stage later.

## Why one phase, measured

The previous design dispatched one agent per issue. Those agents ran 300–560 turns and
ended near 366k tokens of context, past the point where each turn is spent re-reading
what the agent already did. Scoping to a phase is the fix, not compaction. Two companion
rules keep the phase agent's context small: test and gate output is redirected to a file
(`> /tmp/out.txt 2>&1`) and read back with `tail`/`grep`, never pasted whole; and gate
targets are derived from the Makefile at run time rather than listed in the agent
definition (see [[Derive the Gate, Don't Copy It]]).

When the same agent is dispatched to fix review findings, it must **never touch
`merge_impact: blocker` findings** — those are the orchestrator's and the human's call,
and a builder that "fixes" a blocker has silently re-scoped the change. It fixes the rest
and lists the blockers as untouched (see [[Merge Impact and Evidence State]]).

## Report discipline

The agent's final report is capped (30 lines). The orchestrator keeps every subagent
message in its own context for the rest of the run, so a long report is a tax paid on
every later turn. Detail belongs in the artifact (the diff, the plan's execution log);
the report is a pointer plus the verdict.

## See Also
- [[Claude Workflow System]] — instance-of (the build stage of the triage → build → review pipeline)
- [[No-Placeholder Plan Discipline]] — extends (a path that does not resolve is a plan defect)
- [[Shared Context Brief]] — extends (the brief is the agent's only context; pre-resolution is what makes it sufficient)
- [[Workflow Pipeline Telemetry Audit]] — derived-from (the 28%-doc-drift finding that moved the DoD)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — complements (the other build-agent rule from the same definition)
- [[Multi-Agent Role Specialization]] — instance-of
- [[Stage-Scoped Scout Agents]] — extends
