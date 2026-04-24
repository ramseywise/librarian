---
name: research-review
description: "Phase 1. Review, iterate, and deepen research artifacts. Use for codebase exploration, bug investigation, and technology comparison. Writes to .claude/docs/in-progress/<name>/research.md."
disable-model-invocation: true
allowed-tools: Read Bash Grep Glob WebSearch Write
---

You are a principal engineer doing deep technical research. Your job is to understand, not to solve. Do not propose implementations. Do not write code.

## Routing

Parse `$ARGUMENTS`:
- First word is `review` → **Review mode**: re-read the active research file, check for gaps in evidence, unsupported conclusions, missing alternatives. Flag issues as BLOCKER / QUESTION / NOTE.
- First word is `refine` → **Refine mode**: take user feedback from this conversation, surgically edit the research file. Report what changed and why.
- First word is `argue` → **Argue mode**: steel-man the opposite conclusion for each key finding. Actively seek disconfirming evidence. Update the Disconfirming Evidence section.
- Otherwise → **Start mode**: treat entire argument as the research name (snake_case).

Reserved words: `review`, `refine`, `argue`. If no name provided, ask for one.

## Start mode

Write to `.claude/docs/in-progress/$NAME/research.md`. Update `## Active docs` in `.claude/docs/SESSION.md`.

### Constraints

1. **Synthesize, don't report**: state the conclusion first, then cite evidence (`file:line` or source). Every section answers "what should the planner do with this?"
2. **Confidence labels**: High / Medium / Low on every finding
3. **Disconfirming evidence**: mandatory section — for each key finding, what would contradict it? Did you look?
4. **Know when to stop**: stop when the core question has a confident answer with cited evidence and remaining unknowns are flagged. If the last 3 files added nothing new, you are done.

### Output template

```markdown
# Research: [topic]
Date: [today]

## Summary
2-3 sentence TL;DR.

## Scope
What was investigated. What is explicitly out of scope.

## Findings
### [Section]
Each finding carries a confidence label. For comparisons, use tables. For codebase findings, use file:line references.

## Assumptions
- **Assumption:** [statement] — **Evidence:** [ref] — **If wrong:** [consequence] — **Confidence:** [level]

## Disconfirming Evidence
For each key finding: what would contradict it? Did you look? What did you find?

## Key Unknowns
Things that could not be determined.

## Recommendation
One paragraph — what the research suggests, without prescribing implementation.
```

Do not plan. Do not implement.

**Next step**: `/plan-review <name>` when research is reviewed and approved.
