---
title: Skill Authoring Discipline
tags: [agents, llm, pattern]
summary: "How to write a skill rather than what a skill is — the description as routing logic under a token/precision tension, negative examples as the higher-leverage half, explicit invocation where routing must be deterministic, and why skills plus network access is an exfiltration path."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--skills-design.md
---

# Skill Authoring Discipline

[[SKILL.md Pattern]] covers the file format and the loading strategies. This is the
authoring layer on top: given the format, what separates a skill that fires correctly
from one that fires at the wrong time or not at all.

Everything here follows from the one structural fact about skills — **only the name and
description stay resident; the body loads on activation.** That asymmetry sets the
economics of every decision below: resident text is expensive and must be terse, body text
is nearly free and should be generous.

## The description is routing logic, not documentation

The description is the *only* text available when the agent decides whether to load the
skill. It is not a summary of the skill; it is the decision procedure. Written well it
answers three questions:

- When should I use this?
- When should I **not** use this?
- What are the outputs and success criteria?

Two constraints pull against each other — **token cost** (the description is resident in
every window, on every call, forever) and **routing precision**. The source's verdict:
terse wins.

```markdown
# bad (~45 tokens)
description: |
  This skill handles the complete deployment process to production.
  It covers environment checks, rollback procedures, and post-deploy
  verification. Use this before deploying any code to production.

# good (~9 tokens)
description: Use when deploying to production or rolling back.
```

The bad version spends **5× the tokens for the same routing signal**. Everything it adds —
environment checks, rollback procedures, post-deploy verification — is body material,
useful once the skill has fired and pure overhead until then. The error is a natural one:
it reads like a good docstring. It is a bad description because a docstring is written for
someone who has already decided to use the thing.

## Negative examples are the higher-leverage half

A misfire costs a full body load plus a wrong-track start, so the description should say
explicitly what *not* to use it for:

```markdown
Don't call this skill when… (and what to do instead).
```

The reasoning is worth internalizing beyond skills:

> Negative examples are higher-leverage than positive ones, because the positive case is
> usually obvious from the name and the negative case never is.

A skill named `deploy` already signals its positive case; the name does that work for
free. What the name cannot signal is the boundary — that this is not the skill for staging
deploys, or not for rollbacks, or not for the other service. **The name carries the
positive case; only the description can carry the negative one**, which is why spending
scarce description tokens on positives is usually spending them twice.

Note also the `and what to do instead` clause. A pure exclusion leaves the agent with a
gap; a redirect turns the negative example into a routing edge.

## Templates and examples belong in the body

They are effectively free when unused, since the body loads only on activation. This makes
skills the right home for material too bulky to keep resident — structured reports,
escalation triage summaries, account plans, data analysis writeups.

> A worked example in the body beats a paragraph describing the desired format.

This is the same claim [[Few-Shot Prompting]] makes, with the cost objection removed. The
usual reason to describe a format rather than demonstrate it is that the demonstration is
long; progressive disclosure makes length free until the moment it is needed.

## Design for long runs before you need to

Container reuse and compaction are cheaper to build in than to retrofit. A skill expected
to run for more than a few minutes should assume it will be interrupted: **write progress
to disk, resume from checkpoint.**

The retrofit asymmetry is the point. Adding checkpointing to a skill that has one is
configuration; adding it to a skill that assumed uninterrupted execution means finding
every place that holds state in memory. See [[Long-Horizon Execution]] and
[[Context Compaction]].

## For determinism, invoke explicitly

Model-driven routing is probabilistic. When a skill *must* run, say so:

```markdown
Use the <skill name> skill.
```

The general principle, which extends past skills to any behavior that depends on the model
choosing correctly:

> Behavior that must be reliable belongs in code or explicit instruction, not in a
> description hoping to win a routing decision.

A description competes for a routing decision it can lose — against another skill, against
the model deciding it can handle the task directly, against context pressure. If losing
that decision is unacceptable, the description was never the right mechanism. Same
distinction as mechanism-versus-expectation in [[Agent Deployment Anti-Patterns]].

## Skills plus network access is an exfiltration path

The security consequence that is easy to gloss over and hard to fix later:

> Skills make procedures more capable. Network access makes exfiltration possible.
> Together they form a data-exfiltration path — a skill body is instructions the agent
> follows, and a compromised or injected instruction with network reach can move data out.

The mechanism deserves stating plainly: **a skill body is executable instruction, not
data.** Anything that can influence a skill body — or inject into the context that a skill
body acts on — has authored agent behavior. Add an egress path and it has authored
exfiltration.

Defensible default posture:

| Capability | Default |
|---|---|
| Skills | **Allowed** |
| Shell | **Allowed** |
| Network | **Enabled only with a minimal allowlist**, per request, for narrowly scoped tasks |

Note what this posture is *not*: it does not restrict skills or shell, the two capabilities
that sound most dangerous. It restricts network, because network is what converts a local
compromise into a data loss. Assume tool output is untrusted. Avoid combining open internet
access with powerful procedures in consumer-facing flows where users expect strong
confirmation controls.

See [[Prompt Injection]] for the injection half and [[Agent Security Risk Taxonomy]] —
this is R3 and R8 with an egress path attached.

## See Also
- [[SKILL.md Pattern]] — extends (the format and loading strategies this builds on)
- [[Context Anatomy]] — depends-on (progressive disclosure, the mechanism skills rely on)
- [[Tool Design as Harness Surface]] — complements (tools face the same description-as-routing problem)
- [[Agent Deployment Anti-Patterns]] — complements (knowledge belongs in skills, not system prompts)
- [[Agent Security Risk Taxonomy]] — complements (the exfiltration path, as a risk class)
- [[Long-Horizon Execution]] — implements (checkpointing for skills that run long)
