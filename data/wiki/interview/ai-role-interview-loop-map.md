---
title: AI Role Interview Loop Map
tags: [interview, reference]
summary: "Which rounds an AI engineer, ML engineer, data scientist, or forward-deployed engineer loop actually runs, the six round types a self-made list usually misses (recruiter screen, project deep-dive, customer simulation, debugging, take-home defense, reverse interview), and a role × topic weighting that shows where prep effort pays."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-17-interview-kb-consolidation.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-17-interview-kb-consolidation.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-17-curriculum-pillars.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-17-curriculum-pillars.md
---

# AI Role Interview Loop Map

A map of what the 2026 loops for four roles test, compiled from external prep guides
(medium confidence: prep-industry sources, not hiring-team rubrics) while the
learn-ai-engineering interview KB was being built. Its main use is to stop prep from
following the list of rounds you *remember* instead of the rounds that get run.

## The loops

| Role | Typical sequence | Highest-weight round |
|---|---|---|
| **AI / ML engineer** | recruiter screen → coding (more and more project-style or debugging, AI assistant often allowed) → ML/LLM breadth → ML/LLM/agent system design → project deep-dive → behavioral | System design: RAG, agents, eval, cost/latency trade-offs |
| **Forward-deployed / applied AI engineer** | 5–8 stages, about half of them non-coding: ambiguous customer case study, customer-conversation simulation, business/ROI judgment, plus coding | The customer case study. Prep guides report it has the lowest pass rate and the highest weight. The customer simulation is described as a hidden filter that many candidates who pass coding then fail. |
| **Data scientist** | recruiter → SQL/technical screen → statistics & experimentation (A/B) → product-sense case → behavioral; a 24–48h take-home with a presentation is common | Product-sense and experimentation |

In-person rounds were reported returning in 2025 as a counter to AI-assisted cheating.

**The cross-cutting signal** that every source repeats is the same for all four roles:
narrate trade-offs (cost vs latency, RAG vs fine-tuning, interpretability vs accuracy),
state how you would measure success before anyone asks, think aloud, run a visible
clarify → design → iterate process, and frame the answer in business terms.

"System design is the top round" does not hold for forward-deployed roles. There, the case
study and the customer simulation together outweigh it. Weight prep by role, not by the
generic AIE loop.

## Rounds a self-made list misses

A first-pass list (CTO round, head-of-product round, code review, system design, coding,
behavioral, technical questions, online/offline case study) was checked against the
research. It was missing six round types:

1. **Recruiter screen.** Narrative and logistics. Worth a one-page prep.
2. **Project deep-dive.** Walk through a past system end to end. Standard at senior level.
3. **Customer / stakeholder simulation.** The forward-deployed signature round. It is not
   behavioral. It tests whether you can turn a vague customer problem into a scoped
   engagement while the customer is in the room.
4. **Debugging round.** The 2026 trend: fix unfamiliar broken code rather than write new
   code.
5. **Take-home presentation / defense.** The follow-up to an offline case study, where the
   submission gets cross-examined.
6. **Reverse interview.** Your questions to a CTO, founder, or head of product. Sources treat
   it as an evaluated signal. At a startup it doubles as due diligence (runway, culture,
   growth).

Two naming lessons came out of the check:

- **Organize by what is tested, not by who interviews.** "CTO round" and "head-of-product
  round" are named after the interviewer. A startup CTO round mixes system design, judgment
  alignment, and reverse-interview questions. File prep under the tested skill and keep a
  short per-interviewer angle.
- **Merge rounds that share a skill.** The executed KB used ten round files: coding,
  debugging, and pairing in one; case study and take-home defense in one; CTO, head of
  product, and reverse interview together as "leadership rounds".

## Role × topic weighting

● core · ◐ secondary · ○ awareness

| Topic | AIE | MLE | DS | FDE |
|---|---|---|---|---|
| LLM fundamentals (transformers, fine-tuning/LoRA, RLHF) | ● | ● | ◐ | ● |
| RAG | ● | ◐ | ○ | ● |
| Agents (orchestration, memory, tools/MCP, harness) | ● | ◐ | ○ | ● |
| Evals & observability | ● | ● | ◐ | ● |
| Safety / security (prompt injection, guardrails, PII) | ● | ◐ | ○ | ● |
| Context engineering & cost/latency | ● | ◐ | ○ | ◐ |
| Classical ML + DL theory | ◐ | ● | ● | ○ |
| Stats & experimentation | ○ | ◐ | ● | ○ |
| SQL & analytics | ○ | ◐ | ● | ◐ |
| Data engineering & MLOps | ◐ | ● | ◐ | ◐ |
| Coding patterns (DS&A, debugging) | ◐ | ◐ | ◐ | ◐ |
| System design (classic + ML + LLM/agent) | ● | ● | ◐ | ● |
| Product / business sense, ROI | ◐ | ○ | ● | ● |
| Interview technique (trade-off narration, STAR, reverse interview) | ● | ● | ● | ● |

The table's most useful output is its two blind spots. Stats/experimentation and coding
patterns had **no source material** in either the learning repo or this wiki, yet both are
staples of DS loops. Filling them is authorship, not consolidation, so they were scoped as
a separate milestone instead of being folded into the consolidation work.

## How the KB was layered

The interview KB built from this map uses three layers: **study guides** (one per topic
area, compiled and cited), **round guides** (one per round type, each with a per-role
weighting table), and a **sources tier** (raw notes, readings, and this wiki, left where
they are and referenced). The study guides deliberately duplicate wiki knowledge so a
learner can study from them without the wiki. Drift is caught when the learning repo is
re-scraped and ingested here, because ingest flags conflicts. A pure-pointer guide was
rejected because nobody can study from a list of links.

## See Also
- [[System Design Interview Study Guide]] — extends (the method for the highest-weight AIE round)
- [[Timebox-Scaled Deliverable Bar]] — extends (how the take-home and Work Trial tiers set the bar)
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (round technique is performative material)
- [[AI Engineering Curriculum Structure]] — extends (the ten-pillar interview taxonomy this weighting feeds)
- [[Agents Interview Study Guide]] — instance-of (a study guide for one core AIE/FDE topic)
- [[Behavioral Interview Study Guide]] — extends (method for the universal behavioral round)
- [[Case Study Interview Study Guide]] — extends (method for the FDE/DS signature round)
- [[Code Review Interview Study Guide]] — extends (method for the senior/staff review round)
- [[Coding Challenge Interview Study Guide]] — extends (method for the live coding round)
- [[Multi-Level Implementation Round]] — extends (staged-build coding format reported at frontier labs)
- [[Agent Engineering Question Chains]] — extends (scenario half of the AIE technical round)
- [[Customer Simulation Interview Study Guide]] — extends (method for the FDE role-play round)
- [[Project Deep-Dive Interview Study Guide]] — extends (method for the senior experience-review round)
- [[Leadership Rounds Interview Study Guide]] — extends (method for CTO/HoP/founder rounds and the reverse interview)
- [[Recruiter Screen Playbook]] — extends (method for the universal first-gate round)
- [[Technical Breadth Round Playbook]] — extends (method for the ML/LLM breadth round)
- [[System Design Scored Behaviors]] — extends (in-room behaviours graded in the design round)
