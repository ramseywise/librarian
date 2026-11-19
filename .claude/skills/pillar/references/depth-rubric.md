# Tier and depth rubric

Course content is classified on two axes. The intake quiz places a learner, and the syllabus chooses
what to show, from both, so a wrong tag sends someone to the wrong material.
Code: `src/librarian/courses/depth.py`. Plans: `.claude/docs/plans/2026-11-18-two-axis-tier-depth.md`
and `.claude/docs/plans/2026-11-17-intake-placement-syllabus.md`.

| Axis | Set on | Values | Question it answers | Set by |
|---|---|---|---|---|
| **Tier** | a note as a whole | `foundations`, `practitioner`, `specialist` | Who should meet this topic at all? | the curriculum steward, through `/curriculum` |
| **Depth** | each section of a note; each quiz question; each flashcard | `intro`, `core`, `deep` | How far does this passage take the reader? | the depth classifier, then review |

The two are independent. Tier is about the topic, depth about the treatment. A `specialist` note
(kernel methods) still opens with an `intro` section, and a `foundations` note (what a DataFrame is)
can close with a `deep` one. A note has no depth of its own.

Neither is a "level". Level names the three study formats of one topic (multiple choice, flashcards,
worked problems).

Tier uses the same three names as a learner's placement, on purpose: a learner placed at Practitioner
in a subject gets its `foundations` and `practitioner` notes, and `specialist` notes are offered, not
assigned. Inside each note, depth decides which sections start open.

Rubric version: 4, written 2026-11-18, approved 2026-11-19, not yet measured. The gold set records the version it was tagged
against; a change to the rules below is a new version. Version 4 changed four things, each marked
"(v4)": the tier axis is new, a note no longer has a depth, a note is written in depth order, and
`intro` may assume the note's stated prerequisites. The section rules of version 3 are unchanged.

## Tier: the note as a whole (v4)

Tier is decided by the topic and where it sits in the subject, never by how the note happens to be
written.

| Tier | The topic is | Example |
|---|---|---|
| `foundations` | vocabulary and mental models that everyone in the subject needs, including someone who will never build the thing | What a DataFrame is; what a token is |
| `practitioner` | what doing the work or passing the interview takes | Building a retrieval pipeline; choosing a metric |
| `specialist` | met only by someone who owns the result, or works at research or senior depth | Kernel methods; the foundations of reinforcement learning; running a multi-agent system |

- Ask who needs the topic, not how hard the note is. A long, demanding tutorial on a routine task is
  `practitioner`. A short note on a topic most practitioners never touch is `specialist`.
- A note is never at a lower tier than a note it requires in the same subject.
- Position is not tier. The first note of a module is not `foundations` because it comes first, and a
  "b" note is not `specialist` because it is a second pass.
- A module's intro unit (below) is `foundations`.
- When a note covers two topics at different tiers, report it for structural review: it may be two
  notes. Tag it at the lower tier until that is decided.
- Never tier a note for an audience you wish it had.

The steward proposes a tier for every note of a module, with a one-line reason each, and the session
running `/curriculum` writes them. A tier is reviewed by module, by exception.

## Depth: the principle

Classify what the reader is expected to do or understand, not how difficult, long, mathematical or
technical the material looks. Difficulty is not depth: implementing five sorting algorithms is
`core`, and a short explanation of why quicksort degrades on sorted input is `deep`.

None of these decides depth by itself: mathematical notation, the amount of code, the number of
prerequisites, the number of headings. The reader's task comes first.

## The three depths

| Depth | What the section gives | The reader's task | Example |
|---|---|---|---|
| `intro` | The main concepts, easy to understand | Understand the terms and the mental model, with no applied work | What a cache is and why you would want one |
| `core` | More information, for a practitioner | Apply, implement, configure, diagnose or decide, using established methods | Build a caching layer |
| `deep` | The research or the maths a senior or staff engineer would know or want to know | Understand, derive, justify or critically evaluate the mechanisms, assumptions, evidence or trade-offs behind a method | Why a cache makes tail latency worse under one access pattern |

**`intro`** says what the thing is, what it is for and how to picture it. It can be followed without
the rest of the note and asks the reader to build or compute nothing. (v4) It may assume the
prerequisites the note states: the `intro` section of a `specialist` note is easy for that note's
reader, not for a newcomer to the subject.

**`core`** includes:

- implementing algorithms and techniques;
- building and configuring systems;
- following engineering procedures;
- applying established analytical methods;
- making design decisions from stated constraints and rules;
- using a mathematical method without deriving it.

How complicated the implementation is does not make material `deep`.

**`deep`** includes:

- deriving a mathematical result or working out what it implies;
- explaining why a method works or fails;
- critically evaluating research and competing approaches;
- system internals and architectural mechanisms;
- justifying a trade-off beyond applying a stated decision procedure.

Conceptual difficulty alone does not make material `deep`.

## How a note is written (v4)

A note is written in depth order, so that a reader can stop at the end of any band and have a whole
answer at that depth.

1. **Hook**, as the chapter standard already requires.
2. **`intro` sections**: the main concepts. At least one.
3. **`core` sections**: the working knowledge. One heading per concept, each with its worked example.
4. **`deep` sections**: the mechanism, the derivation, the evidence. Each names the concept it goes
   deeper on. Optional: a note has a `deep` band only when there is sourced material to put in it.
   Never write one to fill the slot.
5. Pitfalls, Try it, Interview checklist, Next, as now. They carry no depth.

Rules that follow:

- Content sections never step back down: no `intro` after `core`, no `core` after `deep`.
  `librarian courses check curriculum issues --kind depth_order` lists the sections of a tagged note
  that do. It is information, not a failure: the list is the note's rebuild list.
- A section is at one depth. A section that is half mechanism and half usable rule is split: the rule
  stays in the `core` band and the mechanism moves to the `deep` band under its own heading. It is
  not tagged by which half is longer.
- A `core` section may point forward to its `deep` counterpart in one sentence. It never depends on it.
- The exercise-driven Python, SQL and TypeScript notes under `programming/` (exempt from the chapter
  shape) are tagged but not rebuilt.

A note that is not yet in this shape is tagged as it stands, and the tags that break the order are its
rebuild list.

## Tagging sections

Tag every content heading. Leave out exercises, pitfalls, interview checklists, reading lists and
navigation headings (Pitfalls, Try it, Labs, Interview checklist, Reading, Practice, Next).

- Tag the smallest meaningful subsection whose depth differs. Do not mark a parent heading just to
  cover one child.
- Applying stated rules to design or configure something is `core`. Comparing evidence and explaining
  the trade-offs underneath is `deep`. A section does not become `deep` because it needs judgement.
- A section that explains why something fails and also gives the fix: take the explanation out and
  ask whether the section still does its job. If the reader leaves with a rule to apply and the
  explanation is the motivation for it, the section is `core`. If the body is the mechanism or the
  derivation and the fix is its closing line, the section is `deep`.
- Reporting what a critic or a paper argues takes the depth of the section it sits in. Weighing the
  evidence (what was run, how often, against what) is `deep`.
- (v4) Material at another depth inside a section is reported under `mixed`, with the heading and its
  first few words, when it is a full paragraph or more and the material around it does not depend on
  it. A paragraph that defines something the next code or section uses is never reported. Every
  reported passage is an instruction for the rebuild (move it or give it a heading), not a label.

## Tie-breaks for depth

- **Length and difficulty are not depth.** A long step-by-step tutorial is `core`. A short section on
  why an estimator is biased is `deep`.
- **Code does not make a section `core`.** A short illustration the reader need not run can sit in an
  `intro` section. Code the reader must write or change is `core` or deeper.
- **Maths does not make a section `deep`.** If the reader uses a formula, `core`. If the reader must
  derive or justify it, `deep`.
- **Vocabulary the later sections apply is not automatically `intro`.** Definitions with no applied
  work are `intro`; a section that sets up a method by using it is `core`.
- **Senior practice is `deep`, even when it is taught as a method.** `core` is what doing the task and
  passing the interview take. What a practitioner needs only once they own the result (service levels
  and error budgets for a data product, an unbiased final score after a search) is `deep`, though the
  section walks through a procedure. The line is between setting the policy and working under it:
  choosing the target, the budget or the evaluation protocol is `deep`; following an alerting rule, a
  runbook or a checklist someone else set is `core`.
- **A decision reference** ("which store", "which index") that gives a procedure for choosing is
  `core`. One that argues the trade-offs without a procedure is `deep`.

## Where `intro` comes from

Two places.

- Every note's `intro` band (above).
- A module's **intro unit**: the basic concepts a reader wants before starting the module, a few good
  outside videos and sources, and pointers to where our own notes, labs, drills and wiki concepts go
  further. It is a `foundations` note. Every module gets one, including advanced modules. It is
  specified in the intake plan and written in a later phase.

A module with no `foundations` note shows as a gap until its intro unit is written.

## Where the tags go

Note frontmatter, authored in the source repo and kept by the importer:

```yaml
---
origin: synthesis
tier: practitioner           # foundations | practitioner | specialist, for the note as a whole
depth: core                  # the depth of every section not listed below; not a judgement on the note
depth_sections:              # the sections at another depth
  "The idea in one picture": intro
  "Why the estimator is biased": deep
---
```

- `depth` is a default, written so that most sections need no entry. It is `core` unless the note has
  no `core` section. Nothing reads it as a property of the note.
- A key is the heading's text exactly as it is written in the note, without the `#` marks and with
  any markup it has (backticks, bold, a trailing colon).
- A section's depth covers its subsections. A subsection with its own entry overrides that.
- Do not list a section at the depth it already has.
- Only a heading can be marked.

`librarian courses check chapters` fails a tier or depth that is not one of the three, a heading that
does not exist and an entry that repeats the depth its section already has.

Other material:

| Material | Classified by |
|---|---|
| Quiz question (`_quiz.md`) | its own `depth`; plus `subject` when it tests a course other than the one it is filed under, and a free `topic` |
| Flashcard | both axes: its note's tier, read from the note and never written on the card, and a `depth` of its own (below) |
| Drill | `difficulty`: easy and medium are `core`, hard is `deep` |
| Lab | `depth` in `practice/manifest.yaml` (not read yet) |
| Interviewing | not tagged; offered whole to Practitioner and Specialist |

## Flashcards

A card has two answers and says where they come from.

| Part | What it is | Where it is authored |
|---|---|---|
| Front | the question | slide `recall` (else `title`); checklist column 1 |
| Short answer | what a good answer says, in a sentence or two | slide `answer` (else `takeaway`); checklist column 2 |
| In depth | the explanation behind the short answer: the mechanism, the derivation, the evidence or the trade-off | slide `more`; checklist column `More` or `In depth` |
| Depth | the depth of the question and its short answer, by the rules for questions below | slide `depth`; checklist column `Depth` |
| Sources | what the answers rest on: the paper, the book and chapter, the documentation page | slide `refs`; checklist column `Sources`, separated by `;` |
| Tier | the tier of the card's note | nowhere: it is read from the note |

- The short answer stands on its own. The in-depth answer adds to it and never corrects it.
- The in-depth answer is one step deeper than the card: on an `intro` or `core` card it is the `deep`
  material a senior reader would want; on a `deep` card it is the derivation or the evidence in full.
- Write an in-depth answer only from the note or from a source that was read, and name that source.
  A card with nothing deeper to say has none. Never write one to fill the slot.
- A source is a citation in the form the note's own `sources` use, or a link. The note the card
  belongs to is already shown with the card and is not repeated as a source.
- Never change a card's front to add any of this: a card's schedule is keyed on its front.

## Questions

A question's depth is the depth of the knowledge it takes to answer, not of the lesson it is filed under.

- `intro`: recognise what a thing is or what it is for. No calculation, no code reading.
- `core`: apply it: read code, pick the right method, compute a value, spot the standard pitfall.
- `deep`: reason about a trade-off, a failure at scale, an internal mechanism or a result from the literature.

A question that turns on a trick of wording has no depth; fix or drop it.
