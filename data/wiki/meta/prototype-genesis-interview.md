---
title: Prototype Genesis Interview
tags: [meta, foundations, pattern]
summary: A gated prototyping interview that routes AI-shaped vs ML-shaped work before loading any spec (and says out loud which specs it skipped), forbids reading the data until the framing conversation ends, runs demo and automated modes with opposite defaults, and ends with a mandatory "what did I not know how to do" gate that writes gaps back to the strongest enforcement layer.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/prototype-genesis/SKILL.md
---

# Prototype Genesis Interview

`/prototype-genesis` in galactus is the entry interview for a new prototype. Its gates
(seven on the ML branch, five on the AI branch) carry several rules that apply to any
interview-driven skill.

## Route before loading anything

Gate 0 asks one question: **is there a labelled outcome column in a frame you already
have?** If yes, it is ML, even if an LLM shows up later. A system that reasons over text
with no target column is AI. When a project is both (a fraud model with an LLM narrative
layer), pick the branch that owns the *risk*, note the other as a downstream consumer, and
never walk both branches in one session. The branches' specs contradict each other on
purpose.

Branching decides which specs load. The AI branch loads the `agent-*` specs. The ML branch
loads none of them, because ten agent specs read for a tabular problem burn the context the
data work needs. **Say which specs you are skipping and why.** Silent routing cannot be
told apart from no routing.

## Do not read the data before the framing ends

> An agent that arrives at the framing conversation already holding the findings has
> replaced the interview with a review of its own homework.

The operator's domain knowledge is the one thing the frame cannot supply, and it never gets
asked for if the agent has already profiled the data. The skill flags this as the
constraint most likely to be violated, "because the tools to violate it are right there."
Two related rules: never name a model before the problem/target pair is confirmed ("a model
named first is a preference searching for a justification"), and leave leakage to the
feature gate, decided with the operator (see [[Tabular ML Leakage Taxonomy]]).

## Demo mode and automated mode have opposite defaults

| | Demo / first run | Automated |
|---|---|---|
| Posture | assume nothing, ask everything | pre-compute what is derivable, surface only open questions |
| Data access before framing | none | profile up front |
| Leakage | discovered with the operator | candidates ranked, operator ratifies |
| Pace | one gate per exchange | batched; uncontested gates collapse |

The pre-emptive behaviour that is right for automation is exactly wrong in a demo, because
the point of a demo is the conversation. State which mode is running at the start.

Where a gate offers genuine alternatives (three candidate models, a temporal vs grouped
split), **fan out the delivery and keep the interview**. One agent per option produces a
runnable result, while the gate stays a conversation in the main session.

## The last gate improves the tool

The final gate asks, "What did I get wrong, ask badly, or not have a template for?" It then
writes each gap back where it belongs: a question to the skill file, logic to the EDA
module, a pipeline capability upstream to the template, and a convention that should be
enforced into a hook, linter rule or test. "If a gate above can be skipped with no
consequence, it is documentation." A walkthrough that teaches the skill nothing "was a
transcript, not a session."

## See Also
- [[Profile Then Select]] — alternative-to (the automated-mode counterpart: profile first, then refuse to pick early)
- [[Project Discovery Conversation]] — extends (the same interview stance on the AI branch)
- [[Tabular ML Leakage Taxonomy]] — extends
- [[Scope-POC Design Interview]] — extends (the AI branch's design stage)
