---
title: "Out of the Tar Pit: Essential and Accidental Complexity"
tags: [programming, concept]
summary: "Moseley and Marks's 2006 position paper argues that most software complexity is accidental, that mutable state is its largest cause, and proposes Avoid and Separate plus a hypothetical Functional Relational Programming architecture."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-moseley-2006-out-tar-pit.md
---

# Out of the Tar Pit: Essential and Accidental Complexity

Ben Moseley and Peter Marks (preprint dated 6 February 2006) ask what causes the complexity that makes large systems hard to understand and how it can be avoided or contained. It is a position paper: there is no experiment, and every claim below is argued from reasoning by the authors.

## Essential and accidental complexity

The paper redefines both terms relative to the users' problem. Essential complexity belongs to the problem itself as the users see it. Accidental complexity is everything else: complexity the team would not have to deal with in an ideal world. This adopts Brooks's vocabulary but contradicts his view that most complexity is essential: the authors hypothesise that most complexity in contemporary systems is accidental.

The authors claim:

- Of all the difficulties in building large systems, complexity is the biggest, and mutable state is the largest cause still left. Control and code volume are also on their list of causes.
- Neither testing nor informal reasoning keeps up as state grows: every extra bit of state doubles the count of possible states.
- Accidental complexity divides into a useful part (state and control kept for performance or ease of expression, to be separated) and a useless part (to be avoided).
- Essential state is limited to data the users supply that may be consulted later; derived data is accidental state, since it can be recomputed.

## Avoid and Separate

The recommended approach is to avoid state and explicit control where they are not truly essential, and to divide what remains into three parts: the essential state, the essential logic, and the accidental state and control.

- References run one way. Essential state refers to nothing, logic refers only to state, and the accidental parts refer to both. Altering an accidental part should never force a change to logic, and removing the accidental-but-useful parts should leave a system that is still correct, if slower.
- Derived data is not stored; it is re-derived, and a cache is declared as a performance hint for infrastructure to maintain.
- Integrity rules are written as declarative constraints, not triggers or methods. The paper claims their complexity grows only linearly because they cannot interact with each other.
- Performance is not the first design goal: speeding up a simple but slow system is, the authors argue, easier than simplifying a fast complex one. Performance concerns live in a separate accidental component.
- Data abstraction that is not needed is avoided, because how data is grouped is subjective and the grouping hides it from callers.
- Where an existing system cannot be separated, the fallback advice is three-fold: less state, less explicit control, less code.

## Functional Relational Programming

Functional Relational Programming (FRP) is the paper's outline architecture. Essential state is held as relations (the paper uses Date's term relvar: a variable that holds a relation value at any time) and essential logic is relational algebra plus pure user-defined functions. Accidental state and control are supplied separately as hints, plus feeders and observers. It builds on Codd's relational model and Date's terminology, and the authors treat logic/control separation (Kowalski) as close to the heart of the recommendation.

- A function is referentially transparent when the same arguments always give the same result. The paper's code example shows a counter function returning `(newCounter, result)`.
- Worked example (an estate-agency system): six base relations, three accidental-state hints, and thirteen derived relations, ten internal and three external.
- The authors built a token prototype of the essential state and logic infrastructure in about 1500 lines of Scheme, supporting relational algebra and some temporal extensions (self-reported).
- The authors state that FRP is hypothetical and unproven in practice.

## Limits

- Nothing is measured: every claim is an argument, and the paper itself labels FRP purely hypothetical and unproven (Sec 9).
- The authors admit the line between essential and accidental is blurry, pointing to executable specifications as a blurred case (Sec 7.2.1), and that a degree of accidental complexity is required for performance and expressiveness (Sec 7.2.3).
- They also grant that functional programming copes poorly with systems that must hold state, and that arguments from monads and modularity have not brought adoption (Sec 5.2.4).
- The relational model is distinguished from the SQL of the day, DBMS physical/logical mapping was limited in 2006 (footnote 15), and the infrastructure FRP needs did not exist.
- Dated: written before event sourcing, streaming, immutable data structures and infrastructure-as-declaration became common, and its critique of object-oriented programming targets the mainstream of 2006. The cost-of-software-problems figure it cites for the US economy is reported, not checked.

## See Also
- [[Clean Code: Objects, Classes and Systems]] — related (the object-oriented design advice of the same era; the paper critiques mainstream 2006 OOP)
- [[Python Data Model and Idioms]] — related (mutability and aliasing in Python)
- [[Expand, Migrate, Contract]] — related (a rollout practice that deals with live state)
- [[Programming Curriculum]] — related (course map)
