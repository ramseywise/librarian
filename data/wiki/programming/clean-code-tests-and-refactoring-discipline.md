---
title: "Clean Code: Tests and Refactoring Discipline"
tags: [programming, pattern]
summary: "Martin's guidance that tests are held to the same cleanliness as production code and that messy first drafts are cleaned in many tiny test-protected steps, with the case studies (Args, ComparisonCompactor, SerialDate) as single-author worked examples."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-17-martin-clean-code-ch09-unit-tests.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch12-emergence.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch14-successive-refinement.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch15-junit-internals.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch16-refactoring-serialdate.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch17-smells-heuristics.md
---

# Clean Code: Tests and Refactoring Discipline

In Martin's *Clean Code* the tests are what make cleaning possible: he advises writing a rough draft under a test suite and then refining it. Line-level rules are on [[Clean Code: Names, Functions and Comments]]; class and system design is on [[Clean Code: Objects, Classes and Systems]].

## Tests (chapter 9)

Martin advises:

- The three laws of TDD: write production code only to satisfy a failing test, write only enough of a test to make it fail, and write only enough production code to make it pass.
- Keep test code as clean as production code. His anecdote is of a coached team whose dirty tests became a liability and were discarded, after which defects rose (one anecdote, no data). Tests enable change, so higher coverage means less fear of change.
- Structure a test as build, operate, check, and let a domain-specific testing language emerge from refactoring tests rather than designing it beforehand. The worked example refactors a FitNesse `SerializedPageResponderTest`.
- A dual standard applies: tests can cost more memory or CPU than production code, but must be just as clean.
- A single assert per test is a fair guideline, though he prefers testing one concept per test; splitting a `SerialDate` `addMonths` test into three concepts revealed a missing 28 February case.
- The F.I.R.S.T. acronym for good tests stands for Fast, Independent, Repeatable, Self-validating and Timely.

Chapter 17 adds test heuristics T1-T9: use a coverage tool, do not skip trivial tests, treat an ignored test as a recorded question about requirements, test boundaries and exhaustively near bugs, read patterns of failure and of coverage, and keep tests fast because slow tests get dropped. E1-E2 add that the build and the full test run should each be one command.

## Simple design (chapter 12, Jeff Langr)

Langr lists Beck's four rules of Simple Design, highest priority first: run all the tests, no duplication, express intent, minimise classes and methods. The chapter argues that making a system testable leads to small classes with one purpose and less coupling, calls duplication the primary enemy of good design (including duplicated implementation such as `isEmpty()` defined as `0 == size()`), and uses Template Method to remove higher-level duplication in a `VacationPolicy` example. The fourth rule is argued briefly as a guard against dogma such as an interface for every class.

## Refactoring as practice (chapters 14-16)

All three chapters are Java case studies by one author on one module each.

- **Successive refinement (Args parser).** Martin's thesis is that clean code is written dirty first and then cleaned. The module festered as argument types were added; he stopped adding features and refactored when two more types would have made the mess unfixable. Duplication in three places per type (schema parse, command-line parse, getter) triggered the `ArgumentMarshaler` abstraction.
  - He worked in a long run of minute edits with the program runnable after each, and fixed any test a step broke before touching anything else. Unit tests passed while a separate FitNesse acceptance suite caught an uncovered behaviour, so he added a unit test that runs the acceptance tests.
  - The migration added a new map beside the old ones, moved callers one at a time, then deleted the old maps; the chapter calls this a parallel-change pattern at small scale (compare [[Expand, Migrate, Contract]]). Replacing a type-case with polymorphism took ten tiny steps and moving exceptions into one `ArgsException` took about 30. He judged the first pass disappointing, and compares refactoring to a Rubik's cube, where steps add structure that a later step removes.
- **JUnit's `ComparisonCompactor`.** Martin advises reading the tests first, checking coverage before refactoring (the original tests gave 100 percent coverage; the chapter does not name the tool), and rerunning after each change. Commenting out two guards left the tests passing, so he deleted them. He merged two functions with a hidden temporal coupling rather than pass a dummy argument, renamed a function to name its side effect, and preferred positive conditionals. He expects to reverse earlier refactoring decisions.
- **`SerialDate` (JCommon).** Using Clover, the original tests covered about half the executable statements; Martin's own suite raised that to 92 percent. A test for expected behaviour exposed a boundary bug in `getFollowingDayOfWeek`, and an unrun branch showed `getNearestDayOfWeek` was wrong. After refactoring, coverage fell to 84.9 percent (45 of 53 statements) because the class shrank. Replacing int month constants with an enum took about an hour by his estimate. The order is: make it work, then make it right.

The ethos running through these chapters is the Boy Scout Rule and Martin's claim that working code is not enough.

## Limits

- Assertion and anecdote: no measurement of effort, defects or time beyond the step counts and coverage figures quoted above; each case study is one author on one small module.
- The Args chapter relies on a pre-existing unit and acceptance suite and does not show how to put tests on untested code; intermediate listings are partial and some transformations are left as an exercise.
- The unit-tests chapter says it only scratches the surface and predates mocking-framework critiques, test sizes, flakiness, coverage targets and mutation testing. Its one-assert school cites a 2005 blog.
- The Emergence chapter is silent on YAGNI, on the wrong abstraction and on cases where duplication is fine, and offers no yardstick for "too many" classes.
- Java 2008 idioms (JUnit 3 and 4, Clover, `StringBuffer`) have dated. Martin concedes reviewers disagreed with some `SerialDate` choices and that his naming may not suit every reader. Chapter 17's heuristic codes are cited by chapters 14-16 but the catalogue is one author's list, stated to be incomplete.

## See Also
- [[Clean Code: Names, Functions and Comments]] — prerequisite-for
- [[Expand, Migrate, Contract]] — related (parallel change at database scale)
- [[Clean Code: Objects, Classes and Systems]] — related
- [[Clean Code: Error Handling and Boundaries]] — related (learning tests)
- [[Programming Curriculum]] — related (course map)
