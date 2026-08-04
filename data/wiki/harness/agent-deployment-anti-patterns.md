---
title: Agent Deployment Anti-Patterns
tags: [agents, infra, reference]
summary: "Eight recurring agent-deployment failures that present as model limitations but are engineering-constraint failures — with the reframe that a rule written in documentation is a hope, while a rule enforced by a hook is a constraint."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--agents-guardrails.md
---

# Agent Deployment Anti-Patterns

Eight failure patterns common enough to be diagnostic. The framing that makes the list
worth more than its parts:

> Many seem to indicate insufficient model capabilities, but in retrospect, they stem from
> inadequate engineering constraints.

Each one is misattributed the same way — the agent looks unreliable, so the model looks
too weak, so the response is to wait for a better model. The list is an argument that the
response should instead be to fix the harness. This is the "skill issue" reframe from
[[Harness Engineering]] arrived at from the deployment side, and it is the reason these
are anti-patterns rather than limitations.

## The eight

| # | Anti-pattern | Presenting symptom | Fix |
|---|---|---|---|
| 1 | **System prompts as a knowledge base** | Prompt grows without bound; key rules start getting ignored | Prompts carry *conventions*; knowledge moves to skills |
| 2 | **Uncontrolled tool count** | Agent frequently picks the wrong tool | Merge overlapping tools; define clear namespaces |
| 3 | **No verification loop** | Agent claims completion it cannot substantiate | Attach acceptance criteria per task type |
| 4 | **Boundaryless multi-agent system** | State drift; failures cannot be attributed to an agent | Define roles and permissions; isolate with worktrees |
| 5 | **Inconsistent memory** | Decision quality degrades after ~20 turns of a long dialogue | Monitor token counts; trigger compaction on a threshold |
| 6 | **No evaluation** | Unclear whether a change introduced a regression | Convert every failure case into a test case immediately |
| 7 | **Premature multi-agent** | Coordination overhead exceeds the parallelism gained | Establish the single-agent limit before scaling out |
| 8 | **Constraints based on expectation, not mechanism** | Documented rules are followed selectively | Enforce with tools — linters, hooks, verification |

## The three that are most often misread

**#1 — the prompt as knowledge base** is the one that degrades invisibly. Nothing breaks
when a system prompt reaches 4,000 tokens; instructions simply stop being followed at a
rate nobody measures. The distinction the source draws is precise and worth keeping:
**prompts should carry conventions, skills should carry knowledge**. A convention is a
rule that applies to every call. Knowledge is material relevant to some calls, and loading
it on every call is what produces the bloat. See [[SKILL.md Pattern]] for the loading
mechanism and [[Why Context Is Finite]] for why the ceiling is forced rather than
stylistic.

**#7 — premature multi-agent** inverts the usual diagnostic instinct. When a single agent
struggles, adding agents feels like adding capacity. But coordination is not free, and the
prescription — *verify the single-agent limit before scaling* — asks for evidence that the
ceiling was actually reached rather than assumed. Most reported multi-agent wins are
recoverable single-agent wins with better tools. See
[[Multi-Agent Orchestration Patterns]] for when the escalation is genuinely warranted.

**#8 — constraints based on expectation** is the general case the other seven are
instances of, and the most useful single line in the source:

> Rules in documentation are selectively followed by agents; use tools for
> verification / linter / hook.

A rule written in `AGENTS.md` is a *probabilistic* constraint — it competes for attention
with everything else in the window, and its compliance rate falls as the window fills. A
rule enforced by a pre-commit hook is a *deterministic* one, with a compliance rate of
100% regardless of context pressure. The two are not different strengths of the same
mechanism; they are different mechanisms, and treating documentation as enforcement is
the root error.

The practical test: **for any rule you rely on, ask what happens if the agent ignores it.**
If the answer is "nothing catches it," the rule is documentation. This is the same
distinction [[Execution Boundaries and Guardrails]] draws between a prompt instruction and
a permission gate.

## Guardrails as the quality gate

The source treats guardrails as the gate between *the agent says it's done* and *the task
is finalized* — three approaches, of which production systems typically use at least two:

| Approach | Good for | Cost |
|---|---|---|
| **Deterministic code** | Output format, length, schema conformance | Fast, cheap — prefer wherever applicable |
| **LLM-as-judge** | Nuanced checks: is this factually consistent with the sources? | A model call per check |
| **Human-in-the-loop** | Approval before an irreversible action | Human latency |

The ordering is a preference, not a menu: **use deterministic code wherever the property
is mechanically decidable**, and escalate only for properties that are not. An LLM judge
checking JSON validity is a slower, less reliable schema validator.

The LLM-judge path has one structural feature worth naming — when the judge fails a
response, it explains *why*, and that explanation is fed back to the agent for a revision
attempt. The judge is therefore not only a gate but a **feedback channel**, which is what
distinguishes it from a simple assertion. See [[LLM-as-Judge Evaluation]] and
[[Verification Loops]].

## Where these come from

Anti-patterns 3, 5, 6, and 8 are each the absence of a harness component rather than a
mistake in one — no verification loop, no compaction trigger, no eval suite, no
enforcement mechanism. That is a stronger claim than it first appears: **the majority of
this list is what a system looks like with no harness at all**, which is why the failures
are misattributed to the model. There is nothing else in the system to blame.

## See Also
- [[Harness Engineering]] — extends (the "skill issue" reframe, from the deployment side)
- [[Agent Security Risk Taxonomy]] — complements (the risks these engineering gaps expose)
- [[Harness Maturity and Failure Modes]] — complements (failures of harness maturity, distinct from these deployment failures)
- [[Execution Boundaries and Guardrails]] — implements (mechanism-based enforcement for #8)
- [[SKILL.md Pattern]] — implements (the knowledge-out-of-prompt fix for #1)
- [[Tool Design as Harness Surface]] — implements (namespacing and tool consolidation for #2)
- [[Verification Loops]] — implements (acceptance criteria for #3)
