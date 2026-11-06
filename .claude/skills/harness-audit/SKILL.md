---
name: harness-audit
description: "Audit an agent project's harness against the wiki: what the agent can reach, which gates and hooks actually hold, whether it can skip verification, and what it would do in a bad session, with each finding citing a wiki page. Read-only: reports and ranks, changes nothing in the project. Use when asked to audit an agent setup or harness, review its sandbox, hooks and permissions, or ask what a bad session could break. Do NOT use for building an eval suite (/evals-bootstrap), a code security review of a diff (/security-review), stress-testing a design on paper (/fog or /review-defense), a pre-build briefing (/adk-context), or wiki health (/lint)."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(uv run librarian wiki ask *)
---

You are auditing an agent project against the design experience compiled in this wiki. Run from the librarian repo, so the wiki is on hand. You read the project and change nothing in it.

## Core rule

Every finding names evidence in the project and cites a wiki page that was opened, and a concern with no page goes on the `Not covered` line instead.

## Workflow

`$ARGUMENTS` is the path to the project. Empty means this repo. A path that does not exist: say so and stop.

1. **Read the wiki pages for the areas below.** Open each page you are going to cite, and confirm its file exists before citing it. These are the starting set; follow `## See Also` when a page points somewhere closer. Never open or cite anything in `data/wiki/private/`, and skip pages tagged `tombstone`.

   | Area | What to look for | Page |
   |---|---|---|
   | Reach | Where the agent runs, its filesystem boundary, which credentials and network it has | [[Execution Boundaries and Guardrails]] `data/wiki/harness/execution-boundaries-and-guardrails.md` |
   | Exfiltration | Private data, untrusted content and an outbound channel in one agent, with no leg cut | [[Lethal Triad]] `data/wiki/harness/lethal-triad.md` |
   | Gates | Irreversible actions behind a confirmation, reversible ones running free, approvals with a timeout and a declared default, shell gates that parse commands | [[Execution Boundaries and Guardrails]] `data/wiki/harness/execution-boundaries-and-guardrails.md` |
   | Rules | Constraints only stated in a doc, when a hook, linter or CI rule could enforce them | [[Execution Boundaries and Guardrails]] `data/wiki/harness/execution-boundaries-and-guardrails.md` |
   | Tools | Typed schemas, descriptions with negative sections, the four gating questions | [[Tool Design as Harness Surface]] `data/wiki/harness/tool-design-as-harness-surface.md` |
   | Verification | A gate the agent cannot skip, and an evaluator separate from the generator | [[Verification Loops]] `data/wiki/harness/verification-loops.md` |
   | Done | Static, runtime and system checks in order, not only the fastest test | [[Three-Layer Termination Check]] `data/wiki/harness/three-layer-termination-check.md` |
   | Runaways | Retry caps, edit-count detection, forced re-planning, a cost ceiling per run | [[Loop Detection and the Two-Retry Rule]] `data/wiki/harness/loop-detection-and-the-two-retry-rule.md` |
   | Failure messages | Check output an agent can act on: what failed, why, how to fix it | [[Agent-Oriented Error Messages]] `data/wiki/harness/agent-oriented-error-messages.md` |
   | Traces | Each step recorded by the harness rather than left to the agent, with redaction | [[Runtime vs Process Observability]] `data/wiki/harness/runtime-vs-process-observability.md`, [[Agent Trace Anatomy]] `data/wiki/infra/agent-trace-anatomy.md` |
   | Context | Instruction files short and actionable, loaded only when needed | [[Context Engineering]] `data/wiki/context/context-engineering.md` |
   | Stage | Where the project sits on the ladder, and which next item pays most | [[Harness Maturity and Failure Modes]] `data/wiki/harness/harness-maturity-and-failure-modes.md` |

2. **Read the project.** When the project is this repo, leave `data/wiki/private/` out of every search and all evidence. Look at `CLAUDE.md` and `AGENTS.md`, `.claude/settings*.json` and hooks, agent and tool definitions, CI config, Makefile, container or sandbox config, and the agent's own code. Note the names of secrets files and variables, and never open a secrets file or print a value. A file you could not read goes on `Not checked`.

3. **Work out the worst session.** One sentence: with the setup as it stands, the most damaging thing a confused or injected agent could do, unattended. Base it on what you saw, not on what the docs say is forbidden.

4. **Write the findings.** Each has a severity, the area, what is true, evidence as `path:line`, and the page. A check the project passes goes on `Held`, also with evidence. Absence is evidence only after looking: say what was searched.

5. **Rank them.** `HIGH`: an irreversible action or data exposure is reachable with no human or enforced gate. `MED`: a failure would go undetected, or nothing stops a runaway. `LOW`: quality or fit. Enforced controls rank before prompts: a fix that removes the capability beats a fix that asks the agent not to use it.

6. **Close.** Print the report. If `Not covered` is not `nothing`, record it:
   ```bash
   uv run librarian wiki ask "<reworded topic>"
   ```
   Topic only, with no project name in it. This is not a wiki operation, so nothing goes to `operations.jsonl`. If asked to apply a fix, that is a separate edit session.

## Output format

```
Harness audit: <project>
Worst session: <one sentence>
Stage: <ladder stage> (→ [[Harness Maturity and Failure Modes]])

Findings:
1. [HIGH] <area>: <what is true>. Evidence: <path:line>. (→ [[Page]])
2. [MED] <area>: <what is true>. Evidence: <path:line, or what was searched>. (→ [[Page]])
3. [LOW] <area>: <what is true>. Evidence: <path:line>. (→ [[Page]])

Held: <area> (<path:line>), <area> (<path:line>)
Not checked: <what could not be read, or "nothing">
Fix first: <finding number>: <the smallest change>; after it, the worst session is <one sentence>

Read: [[Page A]], [[Page B]]            (pages opened, in order)
Not covered: <concerns the wiki has no page for, or "nothing">
```

The parenthesis explains the `Read` field and is not printed. `Findings:` is followed by `none` when none apply, and then `Fix first: none`.

## Calibration

A list of everything a project could do better is the common failure. Ten findings, ranked, is about the limit: past that, merge or drop `LOW` ones. If the project is small or early, say so and hold it to the page's minimum viable set, because a personal script does not need what production needs.

Passing a project on its documentation is the other failure. A rule in `CLAUDE.md` is a request, so it counts as `Held` only if something enforces it. Otherwise report the gap, and quote the rule as the reason it was not noticed.

Do not claim what you did not see. A runtime sandbox configured outside the repo reads as `Not checked`, not as a finding that there is none.
