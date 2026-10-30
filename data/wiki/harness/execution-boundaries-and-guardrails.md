---
title: Execution Boundaries and Guardrails
tags: [llm, agents, infra, concept]
summary: "Sandboxes (the isolation ladder and identity sandbox), hooks, and permission gates with declared timeouts — the controls that cannot be argued with, governed by one rule: encode constraints rather than documenting them, and constrain the process as well as the outcome."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--04-execution-boundaries.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--04-execution-boundaries.md
---

# Execution Boundaries and Guardrails

Where the agent runs, what it can touch, and the controls that **cannot be argued with**.

## Sandboxes

A sandbox gives the agent a **safe operating environment to act, observe results, and make
progress** — which is what makes autonomous execution tolerable. Without one, every bash
call is a production risk and every loop iteration needs a human.

**What a sandbox ships with matters as much as its isolation**: language runtimes, CLIs,
browsers, test runners. These are the agent's *senses*. Browsers, logs, screenshots, and
test output are how it observes its own work — the raw material for [[Verification Loops]].

**Backend independence is the design rule** — *"swap the backend, the tools don't change."*

| Backend | Isolation | Speed | Use |
|---|---|---|---|
| Local (`fs`, `child_process`) | Process-level, weak | Fastest | Dev, trusted repos |
| In-memory (copy-on-write overlay) | Strong, ephemeral | Fast | Speculative edits, easy discard |
| Remote cloud sandbox | Strongest | Slow start, costs while alive | Untrusted code, production agents |

Cloud sandboxes introduce a **lifecycle** problem — *they cost money while idle*. State
machines with snapshot/restore let a session pause and resume without paying for the gap.
Worth designing before the bill, not after.

### The isolation ladder

| Level | Mechanism | Cost |
|---|---|---|
| OS-level | Seatbelt (macOS), seccomp / Landlock (Linux) restricting filesystem and network per process | Near-zero; shares the kernel |
| Container | Namespaces + cgroups | Seconds to start; kernel still shared |
| MicroVM | Firecracker-class VMs with their own kernel | Strongest; heavier to run |

Pair any rung with **resource quotas** (CPU, memory, wall-clock, disk). A Python virtualenv
is dependency management, **not isolation** — it stops nothing.

### Identity sandbox

Filesystem isolation isn't the whole story for agents that operate accounts. Give the agent
**its own identities** — its own email, its own cloud and SaaS accounts — rather than the
user's. When a step genuinely needs the user (a login, a CAPTCHA), the user acts inside the
agent's environment over remote desktop; files cross via a shared mount, with paths passed
in messages. A compromised or confused agent can then damage only what it owns. Which
capability combinations make that matter is in [[Lethal Triad]].

Deciding where the agent runs, what tools it has, what it can access, and how it verifies
work are all **harness-level decisions, not model decisions**.

## Hooks: Deterministic Control Flow

Hooks are the harness's answer to *"the agent keeps doing X."* They run **as code**, on a
trigger, and cannot be talked out of enforcing themselves.

| Trigger | Hook |
|---|---|
| After every file edit | Run typecheck + lint; feed failures back |
| Before a bash command | Block destructive patterns (`rm -rf`, `DROP TABLE`, force-push) |
| Before a write outside the workspace | Deny, or require approval |
| Before context limit | Fire compaction |
| On completion attempt | Run the pre-completion checklist |
| On task end | Emit trace, cost, and outcome |

### Silent success, verbose failure

> **Success stays silent; failures get verbose feedback.**

A hook that announces every passing typecheck burns tokens and **trains the model to skim
hook output**. A hook that fires only on failure — with the full error, the file, the line —
produces a **high-signal back-pressure channel**. That is what "wire typecheck back-pressure
into the loop" means concretely: *the agent learns its edit was wrong within one step, not
at review time.*

### Prompts vs hooks

> A model may ignore, misunderstand, or inconsistently follow a textual instruction. **A
> code-level control cannot be talked out of enforcing itself.**

If a behavior must hold *every* time, it is a hook, a permission, or a schema — not a
sentence. **"The agent keeps doing X" is usually a hook, not a stronger paragraph.** Adding
a fourth conditional to a prompt is the signal that the requirement has outgrown the prompt
layer.

## Permission Gates and HITL

Some actions need a human. The design question is **when to ask** — and **asking too often
is as much a failure as never asking**.

The **ambiguity protocol** orders the agent's options:

> **search → ask → act.**

Exhaust available information first, ask only when the information genuinely isn't there,
and never act on a guess when the action is irreversible.

An `askUser` tool with **multiple-choice options** beats an open question: it bounds the
response, makes the decision fast for the human, and produces a parseable answer.

Gate placement follows the four gating questions in [[Tool Design as Harness Surface]] —
irreversible actions get a confirmation; everything else runs free. **Gating reversible
operations is the most common way to make an agent useless.**

**Every approval needs a timeout with a declared default.** An unattended agent waiting
forever on a human is a hung process; decide up front whether silence means *deny* (the
safe default for irreversible actions) or *proceed*, and say which in the prompt to the
human. Log every approval: an action approved the same way many times is a candidate for
automation, or for a reviewer model instead of a person — see
[[Proposer-Reviewer and Sidecar Gating]].

### Parse commands semantically

A string blocklist on shell commands is trivially bypassed: `$(echo rm) -rf /`,
`find . -exec rm {} +`, an alias, a script written then executed. A gate on a shell tool has
to parse the command — the AST, the resolved executable, the flags — and **fail closed** on
anything it can't classify.

## Encode Constraints, Don't Document Them

> **Specifications written in documentation are easily overlooked. Constraints encoded into
> linters, type systems, or CI rules are enforceable.**

Architectural layering enforced by a custom linter holds. The same rule in a design doc does
not. The generalization:

> **Enforce invariants, not implementations.**

Constrain the *shape* of the result — layering, schemas, test coverage, allowed imports —
and leave the implementation free. **Over-constrained implementations produce agents that
can't solve anything novel; unconstrained invariants produce agents that quietly erode the
architecture.**

This is also what makes throughput safe. Review discipline doesn't disappear; it transforms
**from manual review into machine-executed constraints — written once, effective
everywhere.**

## The Five Protection Layers

Independently toggleable, each with its own failure mode:

| Layer | Guards against |
|---|---|
| **Pre-input** | Malicious/malformed user input |
| **Pre-retrieval** | Poisoned documents entering context |
| **Pre-generate** | Unsafe assembled context reaching the model |
| **Post-generate** | Unsafe output leaving the system |
| **Escalation** | Anything unresolved reaching a human |

See [[Safeguards Architecture — Five Protection Layers]].

### Trust zones

| Source | Trust |
|---|---|
| User input | **Untrusted** |
| Retrieved content | **Semi-trusted** |
| Tool inputs (model-composed) | **Semi-trusted** |
| Tool outputs | **Semi-trusted** |
| Agent state | Trusted |

**The row people miss is tool inputs.** They are generated by the model, which may be acting
on injected instructions from a retrieved document — so validate them against schema before
execution, *exactly as you would validate a request from an external client*. See
[[Prompt Injection]].

Related: **PII is redacted before logging** and never passed to unapproved third-party
endpoints. **Traces are a security surface as much as a debugging one.**

## Rollback

The most commonly missing of the four harness parts in [[Harness Engineering]].

- **Git is the default rollback mechanism.** Branch-per-agent makes parallel experimentation
  safe and reverting free.
- **Sandbox snapshots** roll back environment state, not just files.
- **Memory must be editable and auditable** — wrong entries have to be removable rather than
  compounding.

> An agent that can act but not be undone forces a human gate on every action, which defeats
> the point. **Investment in rollback buys autonomy.**

## Cost Envelope

A boundary in the same family as permissions: **per-task budget ceilings that prevent
runaway spend.** A loop with no cost ceiling will find a way to spend without bound — doom
loops are expensive precisely because nothing stops them.

Instrument token spend per run, set a ceiling, and **fail closed with a partial result
rather than silently continuing**.

## Constrain the Process, Not Just the Outcome

An outcome check ("the tests pass") is satisfied by deleting the failing test. The harness
has to constrain *how* the goal is reached too: read-only test files, protected paths, a
hook that rejects edits to the verifier, a diff check on the files the task wasn't supposed
to touch.

### Whose side is the agent on?

An agent acting for one person can meet others — a counterparty in a negotiation, a vendor's
support bot, an email from a stranger. Write the **principal-loyalty code of conduct**
explicitly: whose interests the agent represents, what it may disclose about its principal,
that it never commits its principal beyond its grant, and that instructions arriving from
non-principals are information, not commands.

### Move the trust boundary below the code

When the risk is an agent writing bad *data*, don't rely on the agent's code being right:
put a **human-reviewed schema with validators on every write** underneath it. In one
reported migration, the validator layer took violating writes to **zero** at roughly **2 ms
per write**. The guarantee holds only while **no bypass path exists** — a raw SQL tool or a
direct-file escape hatch quietly turns it back into documentation. The same move applied to
model-supplied facts is [[Belief Parameters with a Ground-Truth Gate]].

## A Role Label Is Not a Sandbox

The boundary above is only real if it is **enforced by the runtime**.

> Permission rules are enforced by the harness, not by the model. Instructions in your
> prompt or `CLAUDE.md` shape what the agent *tries* to do without changing what it is
> *allowed* to do.

A subagent labelled "read-only" in its description can still `rm -rf` if its actual tool
grant includes `Bash` — because `Bash` executes arbitrary shell regardless of what the
description says. **The label is documentation; the grant is the boundary.**

This is *encode constraints, don't document them* applied to permissions, and **it is the
most commonly violated instance of it**. Testing that the boundary actually holds is its own
discipline — see [[Canary Testing for Permission Boundaries]].

## See Also
- [[Harness Engineering]] — part-of
- [[Harness Anatomy]] — part-of
- [[Canary Testing for Permission Boundaries]] — extends
- [[Tool Design as Harness Surface]] — depends-on
- [[Safeguards Architecture — Five Protection Layers]] — implements
- [[Read-Only by Default with Explicit Authorization]] — complements
- [[Reversibility Cliff]] — extends (locating the unattended-action boundary at notification, with evidence)
- [[Proposer-Reviewer and Sidecar Gating]] — extends (who approves when a human shouldn't)
- [[Lethal Triad]] — complements (which capability combinations need the boundary)
- [[Belief Parameters with a Ground-Truth Gate]] — instance-of (trust boundary inside the tool)
- [[Constitutional Classifiers]] — extends (two-stage classifier guardrails)
