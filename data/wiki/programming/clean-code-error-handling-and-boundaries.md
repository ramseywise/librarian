---
title: "Clean Code: Error Handling and Boundaries"
tags: [programming, pattern]
summary: "Feathers and Grenning's chapters in Martin's Clean Code: keep error handling out of the main logic, wrap third-party code behind an interface you control, and pin outside behaviour with learning tests."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-17-martin-clean-code-ch07-error-handling.md
  - data/raw/papers/2026-11-17-martin-clean-code-ch08-boundaries.md
---

# Clean Code: Error Handling and Boundaries

Two guest chapters in Martin's *Clean Code* (Java, 2008) deal with the edges of a module: what happens when something fails, and where your code meets code you do not control. Both argue by Java example only. The line-level rules are on [[Clean Code: Names, Functions and Comments]]; the Python mechanics of exceptions are on [[Python Exceptions and Context Managers]].

## Error handling (chapter 7, Michael Feathers)

The chapter's premise is that error handling which obscures the logic is wrong, and that it should be a separate concern. Feathers advises:

- Raise exceptions instead of handing back error codes or flags, which crowd the caller and can be silently left unchecked. His listings contrast a nested `if`/`else` on status with a `try`/`catch` around one call.
- Treat a `try` block like a transaction: whichever way it aborts, the `catch` has to leave the program in a consistent state. He suggests starting from the `try-catch-finally` skeleton and writing a test that provokes the failure.
- Avoid checked exceptions in general application code, because a low-level `throws` clause forces signature changes up the call chain. He concedes they can help in a critical library, and notes Python has none.
- Attach context to each exception, naming the operation that failed and the kind of failure, because a stack trace cannot show what the operation was trying to do.
- Shape exception classes around the way callers will catch them. Wrap a third-party API so that it raises a single local exception type (his `LocalPort` translates three vendor exceptions into `PortDeviceFailure`); this removes duplicated catch blocks, limits vendor dependence and eases mocking.
- Special Case Pattern: hand back an object that represents the unusual case (a per-diem expense object, an empty list) so callers need no separate branch for it. The chapter credits it to Fowler.
- Do not return `null`, because every caller then needs a check and one missed check breaks the application; do not pass `null` either, since neither an assert nor an exception gives the handler a good action.

## Boundaries (chapter 8, James Grenning)

The chapter advises:

- Do not pass a broad boundary interface such as `java.util.Map` around the system. Keep it inside the class that uses it (a `Sensors` class with `getById`), so the cast, the generics choice and any business rules live in one place. The chapter does not suggest wrapping every `Map`.
- Write learning tests: tests that call a third-party API the way the application will use it, rerun against each new release to spot behaviour changes. The chapter says they cost almost nothing extra, since the API had to be learned regardless.
- For code that does not exist yet, write down the interface you would like to have (`Transmitter.transmit`), test clients against a `FakeTransmitter` at that seam, and bridge to the real API later with an Adapter.
- Let very few places refer to third-party code, so that you depend on something you control instead of something you do not.

## Limits

- Java only, pre-generics `Map` and log4j 1.x; no data, every result is the author's assertion.
- The null and checked-exception guidance does not transfer one-to-one to Python, where `None` is idiomatic for "absent" and there are no checked exceptions. The chapter leaves out context managers, try-with-resources, log levels, retries and async code.
- No criteria are given for skipping a wrapper, and the chapter does not weigh the price of a translation layer (vendor features lost). The Special Case Pattern has no reference entry in the bibliography.
- Both chapters are bylined by guest authors inside a book credited to Martin.

## See Also
- [[Python Exceptions and Context Managers]] — prerequisite-for
- [[Clean Code: Names, Functions and Comments]] — related
- [[Clean Code: Tests and Refactoring Discipline]] — related (learning tests and test seams)
- [[Clean Code: Objects, Classes and Systems]] — related (dependency injection and Adapter at the system level)
