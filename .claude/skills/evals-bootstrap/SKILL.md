---
name: evals-bootstrap
description: "Plan the first eval suite for an agent project from the wiki: where it stands now, what is missing, and first cases taken from real failures, with each finding citing a wiki page. Reports by default, and writes one new case file only with --write. Use when asked to set up evals for an agent, start a golden set, or find out how to tell whether a prompt or model change broke something. Do NOT use for running this repo's retrieval evals (make eval-gate), auditing sandboxes and permissions (/harness-audit), testing a course reviewer on planted faults (/review eval), or scaffolding a new agent (/new-agent)."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Bash(uv run librarian wiki ask *)
---

You are planning a first eval suite for an agent project, using the eval experience compiled in this wiki. Run from the librarian repo, so the wiki is on hand.

## Core rule

Every finding cites a wiki page that was opened, and every case comes from a recorded failure in the project, never from imagination.

## Workflow

`$ARGUMENTS` is the path to the project, plus `--write` if given. Empty means this repo. A path that does not exist: say so and stop.

1. **Read the wiki pages.** Open each page you are going to cite, and confirm its file exists before citing it. These are the starting set; follow `## See Also` when a page points somewhere closer. Never open or cite anything in `data/wiki/private/`, and skip pages tagged `tombstone`.

   | Question | Page |
   |---|---|
   | What exists today, and what is the next level? | [[Eval Maturity Ladder]] `data/wiki/eval/eval-maturity-ladder.md` |
   | Are tests being counted as evals? | [[Eval vs Test Distinction]] `data/wiki/eval/eval-vs-test-distinction.md` |
   | What parts does a suite need, kept apart from the agent? | [[Eval Harness Anatomy]] `data/wiki/eval/eval-harness-anatomy.md` |
   | No criteria yet? | [[Manual Review as Eval Bootstrap]] `data/wiki/eval/manual-review-as-eval-bootstrap.md` |
   | How are failures found and named? | [[Error Analysis (Open and Axial Coding)]] `data/wiki/eval/error-analysis-open-axial-coding.md` |
   | Case shape, size and sourcing | [[Golden Set Mechanics]] `data/wiki/eval/golden-set-mechanics.md` |
   | Could the eval fail at all? | [[Eval Falsifiability]] `data/wiki/eval/eval-falsifiability.md` |
   | Is the path scored, or only the answer? | [[Trajectory Over Outcome]] `data/wiki/eval/trajectory-over-outcome.md` |
   | One trial or several? | [[Eval Non-Determinism]] `data/wiki/eval/eval-non-determinism.md` |
   | When does it gate, and what does it print? | [[Run-Then-Assert Eval CI]] `data/wiki/eval/run-then-assert-eval-ci.md` |
   | Could eval rows have leaked? | [[Eval Contamination Defenses]] `data/wiki/eval/eval-contamination-defenses.md` |
   | Is a judge model justified yet? | [[LLM-as-Judge Evaluation]] `data/wiki/eval/llm-as-judge-evaluation.md`, [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] `data/wiki/eval/judge-calibration-tpr-tnr.md` |
   | There is a suite, but it is not telling you anything | [[Eval Suite Maintenance]] `data/wiki/eval/eval-suite-maintenance.md` |

2. **Read the project.** When the project is this repo, leave `data/wiki/private/` out of every search and all evidence. Find existing tests and evals, how the agent is invoked, whether runs are traced, and CI config. If a suite already exists, the job changes: report its level and gaps, and propose cases only for failures it does not catch.

3. **Find real failures.** In priority order: traces and logs, then bug reports, issues, postmortems and regression tests. Each case needs a `from:` pointing at where the failure is recorded. Do not read secrets files.

4. **If there are no recorded failures, write no cases.** Say `First cases: none, no recorded failures`, and make the next step the manual review of 10 to 20 real queries from the page, with its notes becoming the first cases. A synthetic case is only for a project with no traffic, and carries `source: synthetic`, because it is a spec and not a validated regression.

5. **Fill in each case.** Input, the one behaviour expected, and a deterministic grader wherever a rule can decide it. Include at least one case that a bad output must fail. Do not propose a judge model until calibrating it against human labels is realistic, which the calibration page puts at 100 to 200 labels.

6. **Close.** Print the report. If `Not covered` is not `nothing`, record it:
   ```bash
   uv run librarian wiki ask "<reworded topic>"
   ```
   Topic only, with no project name in it. This is not a wiki operation, so nothing goes to `operations.jsonl`, and a run with no cases changes nothing at all.

### `--write`

Writes the proposed cases to `<project>/evals/cases/first-cases.jsonl`, one JSON object per line, and nothing else: no runner, no CI, no git. That is the only path it may write. It needs at least one case with a `from:`. Glob that exact path first: it refuses if a file is already at that path. Case inputs go into the project's repo, so reword them: no customer names, personal data or secrets.

## Output format

```
Evals bootstrap: <project>
Level: <0-4> <name> (→ [[Eval Maturity Ladder]])

Findings:
1. <what is missing or wrong>. Evidence: <path:line, or what was searched>. (→ [[Page]])
2. <what is missing or wrong>. Evidence: <path:line, or what was searched>. (→ [[Page]])

First cases: <n>, from recorded failures (→ [[Golden Set Mechanics]])
- id: <slug>
  input: <reworded input>
  expected: <the one behaviour>
  grader: <rule, or "manual">
  from: <path:line>

Run with: <one command, existing or proposed>
Next: <the one next step> (→ [[Page]])
Wrote: <path | nothing (no --write) | refused (<reason>)>

Read: [[Page A]], [[Page B]]            (pages opened, in order)
Not covered: <what the wiki could not speak to, or "nothing">
```

The parenthesis explains the `Read` field and is not printed.

## Calibration

Inventing cases is the failure this skill exists to stop. Plausible inputs written from the agent's description test what the author already thought of. Three cases from real failures are worth more than thirty invented ones, and a report of zero cases with a manual review next is a correct result.

Over-building is the other failure. The golden-set page puts an initial set at 20 to 50 cases and about 10 for one issue, and the 100 to 1000 figure is for CI after launch. A first suite is one command and a handful of graders, so do not propose dashboards or a judge model.

Do not raise the level on a test suite's account. A suite of unit tests with mocked models is level 0 or 1 for evals, however green it is.
