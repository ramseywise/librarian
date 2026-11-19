---
title: "Clean Code: Objects, Classes and Systems"
tags: [programming, concept]
summary: "Martin and his guest authors on design above the function: objects versus data structures, size classes by responsibility, and keep construction separate from use in systems."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-17-martin-clean-code-ch06-objects-data-structures.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch10-classes.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch11-systems.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch17-smells-heuristics.md
---

# Clean Code: Objects, Classes and Systems

This page covers the structural chapters of Martin's *Clean Code* (Java, 2008): objects and data structures (chapter 6), classes (chapter 10, with Jeff Langr) and systems (chapter 11, by Kevin Dean Wampler). The rules are argued from Java listings, not measured. Line-level advice is on [[Clean Code: Names, Functions and Comments]].

## Objects and data structures (chapter 6)

- Martin's anti-symmetry: objects hide data behind abstractions and expose functions; data structures expose data and have no meaningful functions. Procedural code makes new functions easy and new data types hard; object code makes new types easy and new functions hard. Pick objects where you expect to add types and data structures where you expect to add functions.
- Martin says a layer of getters and setters does not hide implementation; an abstraction does, such as exposing "percent fuel remaining" where the storage is gallons.
- Law of Demeter: a method should call only methods of its own class, objects it creates, its arguments and its instance variables. Chains such as `ctxt.getOptions().getScratchDir().getAbsolutePath()` ("train wrecks") are a violation only if the links are objects; plain data structures are exempt. The fix for objects is to tell the object to do what the caller wanted the internals for.
- Avoid hybrids (half object, half data structure), which make both kinds of change hard. Treat DTOs and Active Records as data, with business rules in separate objects. The chapter calls "everything is an object" a myth.

## Classes (chapter 10)

Martin and Langr advise:

- Size a class by counting responsibilities, not lines. The heuristic is that the class should be describable in roughly 25 words that avoid "if", "and", "or" and "but"; a name containing `Processor`, `Manager` or `Super` is a warning sign. Their `SuperDashboard` has only five public methods yet is still judged too big, because it has two reasons to change.
- Single Responsibility Principle: one reason to change. Open-Closed: add features by extension (their `Sql` class split into per-statement subclasses so adding `UpdateSql` changes no existing class), but act only on actual change.
- Dependency Inversion: depend on abstractions, injected through the constructor, so a test can supply a stub. Their `Portfolio` takes a `StockExchange` interface and a stub fixing one price makes the test deterministic.
- Cohesion is how many instance variables each method uses; an instance variable that only some methods use hints at a class waiting to be extracted. Splitting Knuth's `PrintPrimes` into three classes, under a test suite and in many tiny steps, stretched the listing from just over one page to nearly three.
- Keep variables and utilities private; widening access so a test can reach them is a last resort.

Chapter 17 restates several of these as heuristics: G6 and G7 (keep levels separate; base classes should not know their derivatives), G14 (feature envy: methods belong with the data they use), G18 (prefer non-static methods), G23 (prefer polymorphism to `if`/`switch`; the ONE SWITCH rule allows a single switch per kind of selection), G27 (enforce design decisions with structure over convention), G34 and G36 (one level of abstraction; no transitive navigation).

## Systems (chapter 11)

Wampler argues:

- Separate startup (construction and wiring) from runtime logic. Separation of Main puts all construction in `main` with dependencies pointing away from it; an Abstract Factory fits when the application must control creation time. Lazy initialisation hard-codes a dependency and he calls it perhaps premature optimisation.
- Dependency Injection is Inversion of Control applied to dependencies: the class stays passive and takes them through a constructor or setter.
- Systems cannot be got right the first time; implement today's stories and refactor, which works if concerns are separated. Big Design Up Front is harmful, and decisions should be postponed to the last possible moment.
- In Wampler's account, EJB2 tied business logic to its container, which hampered unit testing and reuse. Cross-cutting concerns (persistence, transactions, security) are restored to modularity by aspect-oriented programming; Wampler's unsourced estimate is that pure-Java AOP covers most uses.
- The proposed architecture is plain domain objects (POJOs) plus minimally invasive aspects, test-driven like code. He also advises adopting a standard only where it demonstrably pays, using domain-specific languages to bring code closer to the domain, and settling for the simplest design that could work.

## Limits

- Tied to Java tooling of 2008 (EJB, Spring, JDK proxies, AspectJ), much of which has dated; the recompilation and package-scope arguments do not apply to Python. The data-structure chapter does not mention records, dataclasses or dynamic languages.
- Claims are argued by analogy and anecdote with no measurements. The chapter 11 estimate for pure-Java AOP is unsourced.
- The class rules are not presented as absolute: the authors say they are not fanatic about privacy and that a maximally cohesive class is neither advisable nor possible. SRP appears here as "one reason to change"; later framings are not in the chapter. Footnote 1 of chapter 6 concedes Visitor works around the new-function cost but returns the structure to a procedural one.
- Chapters 10 and 11 carry guest bylines inside a book credited to Martin; chapter 17 is the author's own incomplete list.

## See Also
- [[Python Type Hints and Dataclasses]] — related (dataclasses as the plain-data side of the object/data split)
- [[Clean Code: Names, Functions and Comments]] — prerequisite-for
- [[Clean Code: Tests and Refactoring Discipline]] — related
- [[Clean Code: Error Handling and Boundaries]] — related
- [[Out of the Tar Pit: Essential and Accidental Complexity]] — related (a different account of where complexity comes from)
