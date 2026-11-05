---
generated_by: tools/slides/flashcards.py
decks:
- programming/software-design/slides/deck.yaml
cards:
- front: What do you do when you spot a code smell?
  back: A smell is a reason to look, never a verdict. Refactor a file because you keep having to change it, not because it smells.
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: What does one step of refactoring look like?
  back: Refactoring changes structure and not observable behaviour, in small steps that keep the system working. On red, revert and take a smaller step.
  lesson: programming/software-design/notes/02-refactoring
- front: How do you pin code you don't understand yet?
  back: A characterization test records what the code does now, not what it should do. Start with a test named `x`, then paste in the actual value.
  lesson: programming/software-design/notes/02-refactoring
- front: Did the refactor make the next feature's diff smaller?
  back: 'No: the diff came out about the same. The gains were a worst McCabe of 6 against 26, pricing testable alone, and small bug fixes later.'
  lesson: programming/software-design/notes/02-refactoring
- front: How do you change something other people depend on?
  back: You can't change callers you don't control in one commit. Add the new beside the old, move callers gradually, then remove the old.
  lesson: programming/software-design/notes/02-refactoring
- front: What should a module keep secret?
  back: Give each module a design decision to hide and an interface that reveals little. Every promise, even an accidental one, is something you can't change later.
  lesson: programming/software-design/notes/03-design-principles
- front: Is duplication always bad?
  back: No. Remove the same fact stated twice, but leave code that changes for different reasons alone, even if it looks alike.
  lesson: programming/software-design/notes/03-design-principles
- front: What does each SOLID principle ask of you?
  back: 'S: one group of people. O: extend without editing. L: keep the behaviour. I: ask only for what you use. D: pass it in. Each is a question about what change it makes harder.'
  lesson: programming/software-design/notes/03-design-principles
- front: How much does polymorphism really cost?
  back: Same direction, very different size. A table beat virtual calls about 10x in C++ and about 2x in this CPython run, so measure in your own context.
  lesson: programming/software-design/notes/03-design-principles
- front: Which patterns does Python make smaller?
  back: Ask what varies, then start with a function, a table or a module-level object. Move to the class form only when it earns its keep.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: How do you reject illegal state transitions?
  back: Use an enum and a transition table. A move through `to()` that isn't in the table is rejected, and you can test the whole table.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Which test double should you reach for first?
  back: Real object first, then a fake, then a stub, and interaction checks only when the call itself is the behaviour.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Why can 100% coverage prove almost nothing?
  back: Coverage tells you what ran, not what was checked. A surviving mutant asks whether a behaviour is unspecified, so run it on the code you're changing.
  lesson: programming/software-design/notes/05-testing-strategy
- front: How do you test code around a model?
  back: Script the model for your logic, record vendor replies for parsing, keep a few live smoke tests, and use evals for quality.
  lesson: programming/software-design/notes/05-testing-strategy
- front: How do you debug without guessing?
  back: Stabilise first, then write down a prediction, test one thing at a time, and ask what changed. A failed prediction still tells you something.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: Which profiler answers which question?
  back: Profile before you optimise. Use `cProfile` for call counts on a local run and a sampler for live services. An on-CPU profile won't show time spent waiting.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: What does Git actually store?
  back: Blobs, trees and commits, addressed by content hash. History is immutable and what moves is pointers, so a bad reset can be undone from the reflog.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: How do you find the commit that broke something?
  back: '`git bisect run` binary-searches history with a check script: 0 is good, 125 skips, any other code up to 127 is bad. It needs commits that can each be tested.'
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What is a code reviewer for?
  back: Approve once a change improves code health, read for design first, and answer within a business day. Keep refactoring separate from features.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: Which record do you write, and when?
  back: Write a design doc when the solution is ambiguous, and an ADR at a significant decision, with its bad consequences and what would change your mind.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: When should you refactor, and what do you do first?
  back: Refactor when you're about to change the code, and pin behaviour with tests before you change structure.
  lesson: programming/software-design/notes/02-refactoring
- front: What should you do next?
  back: Do the lab next, a real smelly module refactored under tests, with every step one commit that passes.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
---
