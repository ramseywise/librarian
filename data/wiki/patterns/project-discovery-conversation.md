---
title: Project Discovery Conversation
tags: [llm, pattern]
summary: A guided pre-design conversation that turns a volunteer's pain point into a Project Profile — deliberately withholding all technology vocabulary so the artifact commits to outcomes and constraints, not framework choices.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/SKILL.md
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/archetype-selection.md
---

# Project Discovery Conversation

`/project-discovery` is the entry point of the ai-project-template pipeline, running
**before** design. It exists for the "I have an idea but don't know where to start" case —
volunteers starting from a pain point rather than a design.

**Pipeline:** `/project-discovery` → `/scope-poc` → `/project-genesis` → copier

Each stage answers exactly one question:

| Stage | Answers |
|---|---|
| `/project-discovery` | What's worth building? |
| `/scope-poc` | What exactly is it? |
| `/project-genesis` | How do we scaffold it? |

## The six steps

0. **Intake — who's in the room.** Role/background, dev setup and tooling, team working
   rules. This calibrates every later explanation, and feeds forward concretely: tooling
   preferences and team rules become the rendered project's `CLAUDE.md` conventions at
   genesis time; the people named seed the DESIGN.md actor table.
1. **Pain point elicitation.** Opens with *"What's painful for them today?"* The goal is a
   named actor plus a real-world consequence — *"their intake coordinator spends 3 hours
   per new client looking up which programs they qualify for,"* not *"they need better
   data management."*
2. **Archetype matching.** Present the 1–2 best-fitting [[AI Project Archetypes]] as cards
   with trade-offs. If the user is unsure, ask what the 5-minute demo would show — the
   answer usually maps to exactly one archetype.
3. **Complexity budget.** Weekend sprint / multi-sprint / semester, plus hard deadlines.
4. **Must-demonstrate items.** *"Imagine showing this in 5 minutes. What do they need to
   see to say 'yes, this is useful'?"* Push for 3–5 concrete items, reframing vague answers
   into demonstrable features.
5. **Constraints and capacity.** Team composition, hours, tech constraints, and explicit
   **non-goals** — "what's explicitly NOT your problem to solve, even if someone suggests
   it later."
6. **Confirm and write the Project Profile**, after explicit user confirmation.

## Tone as a design constraint

The tone section is functional, not decorative — the target user may never have built an
AI system:

- Plain language: *"the AI finds answers in documents,"* not *"RAG pipeline."*
- Choices as **cards with trade-offs**, not open questions requiring expertise.
- *"Never make them feel like they need to know the 'right answer' — there isn't one."*

This is the same insight as presenting archetypes with explicit "when NOT to use it"
sections: a non-expert can evaluate a trade-off but cannot generate an option space.

## No premature tech choices

The strongest rule: the profile **must not name** LangGraph, ADK, Vercel, or any
framework. *"The profile speaks in outcomes and constraints."* Framework selection belongs
to `/scope-poc` and `/project-genesis`.

Technology does enter, but only as **Copier Hints** — a derived table mapping discovery
answers to scaffold parameters (archetype → `project_type`, complexity →
`deployment_target`, team skills → `primary_backend_language`). These are marked
**"suggested" not "decided"**, and downstream skills may override them.

The separation matters because a framework named during discovery becomes an unexamined
constraint on the design that follows.

## Unknowns are first-class

*"'I don't know' is a valid answer everywhere."* The profile records `unknown` rather than
a guess; `/scope-poc` parks unknowns in DESIGN.md's Open Questions **with a revisit
trigger** and offers a research path to close them. Re-running the skill later fills gaps —
the profile is **updated in place, never started over**, and re-entry skips what's already
answered.

This makes the profile a living document rather than a one-shot form, and it is explicitly
expected to be corrected if the design conversation reveals the initial archetype was wrong.

## Quality constraints

- **Concrete over abstract** — every field must reference something the user actually
  said. *"They track 200 cases in a spreadsheet,"* not *"they have data management
  challenges."*
- **One archetype** — pick the primary, note the secondary as phase-2.
- **Honest complexity** — *"If the team has 2 people and 4 hours/week, don't suggest a
  semester-scope system. Match ambition to capacity."*

## See Also
- [[DESIGN.md Artifact]] <!-- auto-linked -->
- [[AI Project Archetypes]] — extends
- [[Scope-POC Design Interview]] — prerequisite-for (next pipeline stage; consumes the profile)
- [[AI Project Template Scaffold]] — prerequisite-for
- [[NYC-DSSG Project]] — instance-of
- [[Claude Workflow System]] — extends
- [[Integration Pattern Selection]] — extends (how the named external systems get connected)
- [[Skill Pipeline Dryrun Testing]] — extends (regression harness asserting archetype and profile completeness)
- [[Data Pipeline Pattern Selection]] — extends ("where does the data come from" as a discovery question)
- [[Design-Before-Infrastructure Sequencing]] — extends (why discovery, design, and scaffold are three skills)
- [[Human-Participant Skill Test Protocol]] — extends (usability-testing this skill with first-time volunteers)
