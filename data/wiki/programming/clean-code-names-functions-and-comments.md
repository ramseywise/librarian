---
title: "Clean Code: Names, Functions and Comments"
tags: [programming, concept]
summary: "Martin's guidance on how to name things, size functions and when to write comments, with the Java-era caveats and the fact that it rests on one author's experience rather than measurement."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-17-martin-clean-code-ch01-clean-code.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch02-meaningful-names.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch03-functions.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch04-comments.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch17-smells-heuristics.md
---

# Clean Code: Names, Functions and Comments

Robert C. Martin's *Clean Code* (2008) asks why code quality matters and what makes code clean. This page covers the line-level advice: names, functions and comments. Class design is on [[Clean Code: Objects, Classes and Systems]], error handling on [[Clean Code: Error Handling and Boundaries]] and tests and refactoring on [[Clean Code: Tests and Refactoring Discipline]]. Every rule below is one author's guidance (see Limits).

## Why it matters, and the framing

- Martin asserts that reading code takes well over ten times as long as writing it, based on memory of replaying his editor sessions; no study is cited. Because of this he advises favouring readability, even where it makes writing slower.
- He advises keeping code clean at all times ("Later equals never") and applying the Boy Scout Rule: leave code a little cleaner than found, through small changes such as a rename or an extracted function.
- Several people define clean code in the chapter: Stroustrup (elegant, does one thing well), Booch (reads like prose), Thomas (tested, readable by others), Feathers (the work of someone who cares), Jeffries (free of duplication, expressive, built from tiny abstractions) and Cunningham (each routine is about what you expected).

## Names (chapter 2, bylined Tim Ottinger)

The chapter advises:

- A name should tell the reader the reason a thing exists, its job and its usage. Its example renames `getThem()` on a minesweeper board to `getFlaggedCells()`, then hides the magic `4` behind a `Cell.isFlagged()` method.
- Avoid false clues (`accountList` for something that is not a list) and distinctions made only by number series or noise words (`Info`, `Data`).
- Use pronounceable and searchable names, and let name length grow with scope: single letters only as locals in short methods, loop counters `i`, `j`, `k` excepted.
- Drop Hungarian Notation, `m_` prefixes and interface `I` prefixes; if one thing must be encoded, encode the implementation.
- Class names are nouns, method names are verbs, and named static factory methods are preferred to overloaded constructors.
- Use a single word for each concept, not `fetch`, `retrieve` and `get` side by side, and never let one word carry two meanings (punning).
- Take names from computer-science vocabulary first and from the problem domain second. Supply context through an enclosing class rather than prefixes, and add no gratuitous context.
- Rename without fear when a better name appears.

The chapter 17 catalogue restates these as N1-N6 and adds N7: names should describe side effects (`createOrReturnOos` rather than `getOos`).

## Functions (chapter 3)

Martin advises:

- Keep functions very small, "hardly ever" 20 lines, with one-line blocks in `if`/`while` and an indent level of one or two. He concedes he has no research showing small functions are better; the basis is the function sizes he has written over about four decades.
- By his definition a function does one thing when all its steps sit one abstraction level under its name; a second test is whether anything could still be extracted under a name that says more than the code does. One level of abstraction per function, ordered by the stepdown rule so a file reads top-down.
- Prefer zero, then one, then two arguments; avoid three, and justify more. Avoid output arguments and boolean flag arguments (a flag says the function does two things, so split it).
- Avoid side effects: his example is a `checkPassword` that also initialises a session, which hides a temporal coupling. Separate commands from queries.
- Prefer exceptions to returned error codes (see [[Clean Code: Error Handling and Boundaries]]), and remove duplication.
- He sees little value in single-entry single-exit for tiny functions.
- His own process is a long, rough first draft covered by unit tests, refactored afterwards into the shape these rules describe.

The running example refactors the FitNesse `testableHtml` function (Java) into small methods; the chapter asks the reader to judge readability, and no measurement is made.

## Comments (chapter 4)

Martin's position is that a comment is there to make up for code that failed to state its intent, that they are a necessary evil, and that an inaccurate comment is worse than none because the code is the only reliable truth. He advises:

- Try a better name or function first (`employee.isEligibleForFullBenefits()` replaces a flag test plus a comment).
- Worth keeping are legal headers, statements of intent or rationale, warnings about consequences, amplification of something easy to miss, TODOs and docs for a public API. In his refactored prime generator he keeps two, one being the rationale for a square-root limit that no name could express.
- Delete commented-out code, journal and byline comments (source control records them), closing-brace comments, noise comments and mandated per-function javadoc. Do not put system-wide facts in a local comment.

Chapter 17 compresses this to C1-C5 and F1-F4 and G-series items on the same points, for example G25 (named constants instead of magic numbers, except self-evident ones such as `2*PI`), G28 (encapsulate conditionals), G29 (avoid negative conditionals) and G31 (hide temporal coupling by passing each result to the next call).

## Limits

- Opinion and anecdote throughout; no measurement. Martin describes the advice as one school of thought and calls many recommendations controversial.
- The ten-to-one reading ratio and the story of a company that failed from messy code are unsupported by data.
- Written for Java and C++ in 2008, so the Hungarian Notation, `m_` prefix, javabean accessor and IDE-completion points reflect that tooling; PEP 8 conventions for Python differ. Several function rules (switch via polymorphism, `this` as an output argument) depend on the Java setting. Chapter 17's J1 wildcard-import advice conflicts with modern Python style.
- "One thing" is admitted to be hard to define, and no test is given for over-decomposition; the flag-argument rule is applied unevenly (Martin keeps one flag in his own listing).
- Ousterhout disputes some later positions (function size, comments); the extractions do not contain that exchange. Some comment advice has dated (IDE TODO search, `@Ignore`).
- The chapter 17 list is the author's judgement from his own refactorings and is stated to be incomplete. Chapters 2 and 11 are bylined Ottinger and Wampler inside a book credited to Martin.

## See Also
- [[Python Data Model and Idioms]] — related (Python naming and idioms differ from the Java-era rules)
- [[Python Type Hints and Dataclasses]] — related (types as the checked alternative to encoded names)
- [[Clean Code: Tests and Refactoring Discipline]] — related (the safety net behind the refactor-later advice)
- [[Clean Code: Error Handling and Boundaries]] — related
- [[Clean Code: Objects, Classes and Systems]] — related
- [[Programming Curriculum]] — related (course map)
