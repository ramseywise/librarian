---
name: insights_analysis
description: "Interpretation framework for Claude Code session data: what patterns matter, what signals to surface, and how to connect stats to concrete workflow improvements."
---

You are interpreting Claude Code usage data to produce actionable workflow improvements — not a usage dashboard. Raw numbers are inputs; the output must be specific recommendations.

## What the data can tell you

Session data from `~/.claude/projects/**/*.jsonl` surfaces:

| Signal | What to look for | Workflow implication |
|--------|-----------------|----------------------|
| **Tool error rate by type** | `edit_failed`, `file_not_found` spikes | Plan steps with wrong file paths; reading before editing |
| **User interruptions** (gap <5s) | High count = agent going off-track | Plans are ambiguous; steps too large |
| **Response time distribution** | Many >5m gaps = user is reviewing, not waiting | Good: human-in-loop working. Many <10s = rubber-stamping |
| **Compact frequency** | Sessions compacted 3+ times | Context budget too tight; documents too large; skills should be lazy-loaded |
| **Top tools** | Bash dominates over Read/Edit | Over-reliance on shell; not using dedicated tools |
| **Error type: `user_rejected`** | High count | Permission model too tight or commands surprising the user |
| **Session duration vs message count** | Long sessions, few messages = big steps | Steps sized too large; agent doing too much per turn |
| **Parallel session overlap** | High = intentional multi-agent | Low = single-threaded; consider background agents for research |

## Patterns that indicate context engineering problems

**Symptom: frequent compacts in the same session**
- Cause: always-loaded files are too large, or plan/research docs are bloating context
- Fix: move `@`-includes to project-level only; lazy-load skills; trim SESSION.md

**Symptom: high `edit_failed` rate**
- Cause: editing files without reading first, or plan has wrong line numbers
- Fix: enforce read-before-edit in execute skill; add plan_check before execute

**Symptom: high interruption rate**
- Cause: agent is making surprising decisions mid-step
- Fix: smaller plan steps; clearer "done when" conditions; more explicit scope boundaries

**Symptom: Bash dominates tool usage**
- Cause: using shell for file reads/searches instead of dedicated tools
- Fix: reinforce Read/Grep/Glob preference in hard-rules or hooks

## What the data cannot tell you

- Whether the work was correct (only whether tests passed)
- Whether a deviation from the plan was good or bad
- Why a user interrupted (reviewing vs. correcting)
- Whether token usage was efficient for the task complexity

Do not over-interpret low-signal metrics. A long session on a hard problem is not a problem.

## Output format for the insights report

For each pattern identified, produce:

```
### [Pattern name]
**Signal**: [what the data shows — specific numbers]
**Interpretation**: [what this likely means]
**Recommendation**: [one concrete change to the setup, workflow, or prompts]
```

Limit to the 3–5 patterns with the clearest signal. More than 5 dilutes actionability.

End with a **Priority** section: which single change would have the highest impact on token efficiency or workflow quality, and why.
