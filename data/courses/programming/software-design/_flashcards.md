---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- programming/software-design/slides/deck.yaml
cards:
- front: What are the three parts of this lecture, in order?
  back: The lecture moves from writing code that can change, to knowing that it works, to keeping the reasons behind it.
  lesson: programming/software-design/readme
- front: Name three things this lecture teaches you to do with a codebase.
  back: You will be able to change code in small safe steps, show that it still works, and leave the reasons where the team can find them.
  lesson: programming/software-design/readme
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
- front: Name four Git habits that go wrong, with the symptom of each.
  back: Stage explicit paths, rebase only what nobody has built on, and keep a bisect check reliable and outside the repository.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: When should you refactor, and what do you do first?
  back: Refactor when you're about to change the code, and pin behaviour with tests before you change structure.
  lesson: programming/software-design/notes/02-refactoring
- front: What should you do next?
  back: Do the lab next, a real smelly module refactored under tests, with every step one commit that passes.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What is a code smell?
  back: 'Fowler: a surface indication that usually corresponds to a deeper problem. Quick to spot, and not always a problem.'
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: Does refactoring smells reduce maintenance effort?
  back: Sjøberg et al. found no significant effect for 12 smells after adjusting for file size and changes, in a controlled study of six developers and four Java systems. One study, but it argues for prioritising by change frequency.
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: How long should a function be?
  back: 'There''s no consensus. Google: think hard past about 40 lines. Martin: very short. Ousterhout: as long as the interface stays much simpler than the implementation. What matters is whether a reader can skip the body.'
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: What is a deep module?
  back: 'Ousterhout''s term: lots of functionality behind a simple interface. A shallow one exposes nearly as much as it hides.'
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: When should you write a comment?
  back: 'For what the code can''t say: why, units, invariants, what callers must guarantee. Not to restate the code.'
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: What is cyclomatic complexity good for?
  back: Finding places to look. It counts branches, so it misses coupling and overrates flat dispatch. Don't make it a target.
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: What's wrong with flag arguments?
  back: The call site is unreadable, and they usually mean one function doing several jobs. Use keyword-only arguments or separate functions.
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: Why is global mutable state so costly?
  back: No single function's text tells you its behaviour. A second call can behave differently, as the lab shows.
  lesson: programming/software-design/notes/01-readable-code-and-smells
- front: What is refactoring?
  back: A behaviour-preserving change to internal structure, in small steps that leave the system working. It's not a synonym for rewriting or cleaning up.
  lesson: programming/software-design/notes/02-refactoring
- front: What's a characterization test?
  back: 'A test that records what code does now, without claiming it''s right. Feathers: start with a test named `x` and copy in the actual value.'
  lesson: programming/software-design/notes/02-refactoring
- front: How do you check your tests protect a refactor?
  back: Introduce a deliberate error and confirm that something fails. Coverage alone doesn't tell you.
  lesson: programming/software-design/notes/02-refactoring
- front: What's preparatory refactoring?
  back: 'Reshaping code first so the feature becomes easy: "make the change easy, then make the easy change".'
  lesson: programming/software-design/notes/02-refactoring
- front: When isn't refactoring worthwhile?
  back: Code that isn't changing, or when no tests are possible at a reasonable cost, or when a rewrite is the honest description.
  lesson: programming/software-design/notes/02-refactoring
- front: Does refactoring always make the next change smaller?
  back: No. In this course's lab the feature diff came out about the same. The gains were complexity, testability and later fixes.
  lesson: programming/software-design/notes/02-refactoring
- front: 'Replace conditional with polymorphism: always?'
  back: Only when branches differ in behaviour and recur. If only data differs, a table is simpler.
  lesson: programming/software-design/notes/02-refactoring
- front: How do you change an interface with callers you don't control?
  back: 'Parallel change: expand, migrate, contract, with usage measured so you know when to delete.'
  lesson: programming/software-design/notes/02-refactoring
- front: Branch by Abstraction versus feature branch?
  back: Work on mainline behind an abstraction, moving clients gradually, so nothing waits on a long merge. It costs a temporary layer.
  lesson: programming/software-design/notes/02-refactoring
- front: What's a strangler fig?
  back: Replacing a system gradually by diverting flows through a seam to new code, accepting transitional architecture.
  lesson: programming/software-design/notes/02-refactoring
- front: What did Kim et al. find?
  back: Engineers define refactoring loosely, 46% not mentioning behaviour; they see real cost and risk; refactored Windows 7 binaries showed more defect reduction. Correlational, one product.
  lesson: programming/software-design/notes/02-refactoring
- front: What is information hiding?
  back: 'Parnas: each module hides a design decision from the others, with an interface revealing as little as possible. Don''t decompose by flowchart step.'
  lesson: programming/software-design/notes/03-design-principles
- front: Coupling vs cohesion?
  back: 'Cohesion: things in a module belong together, changing for the same reasons. Coupling: how much a change in one thing forces change in another.'
  lesson: programming/software-design/notes/03-design-principles
- front: What's a deep module?
  back: 'Ousterhout: a simple interface over lots of functionality. Shallow ones add interface without hiding anything.'
  lesson: programming/software-design/notes/03-design-principles
- front: What does YAGNI not cover?
  back: Refactoring and malleability, and future-friendly choices that add no complexity. It's about presumptive features.
  lesson: programming/software-design/notes/03-design-principles
- front: What are Beck's four rules?
  back: Passes the tests, reveals intention, no duplication, fewest elements, in that order (Fowler's wording).
  lesson: programming/software-design/notes/03-design-principles
- front: Explain SRP.
  back: 'Martin: a module has one reason to change, meaning one group of people asking. It isn''t "does one thing". North''s critique: it can create artificial seams when content and format change together.'
  lesson: programming/software-design/notes/03-design-principles
- front: Explain LSP in Python terms.
  back: 'A duck type or protocol implementation must keep the behaviour callers rely on, not only the signature. Liskov and Wing: provable properties of the supertype hold for the subtype. Type checkers can''t verify it, so use contract tests.'
  lesson: programming/software-design/notes/03-design-principles
- front: Does ISP apply in Python?
  back: 'Weakly: Martin says dynamic languages are less affected. It survives as "ask for only what you use", via `Protocol`.'
  lesson: programming/software-design/notes/03-design-principles
- front: How do you do dependency inversion in Python?
  back: Pass a function or protocol object into high-level logic and wire the real one at the edge. No framework needed.
  lesson: programming/software-design/notes/03-design-principles
- front: What's the best critique of SOLID?
  back: 'Pick one and state it fairly: North on rules vs properties, Ousterhout on shallow pieces, Metz on premature abstraction, Muratori on measured runtime cost. Then give the reply.'
  lesson: programming/software-design/notes/03-design-principles
- front: Is polymorphism slow?
  back: Muratori measured 1.5x to about 15x in C++, and 20 to 25x with AVX. In CPython my run shows a much smaller gap, since the interpreter dominates. Measure in your own context.
  lesson: programming/software-design/notes/03-design-principles
- front: Essential vs accidental complexity?
  back: 'Brooks: inherent difficulty versus representation difficulty. Moseley and Marks: avoid or separate accidental state and control.'
  lesson: programming/software-design/notes/03-design-principles
- front: Why are many Gang of Four patterns less common in Python?
  back: First-class functions and types make them small or invisible. Norvig counted 16 of 23 as simpler in Lisp or Dylan, for at least some uses.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Strategy in Python?
  back: Pass a function. Use a class only for inspectable state or several related methods.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Adapter vs gateway?
  back: An adapter fits one existing interface to another existing one. Fowler's gateway wraps an external system behind an interface you design as you wrap it, with only translation logic inside.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Decorator pattern vs `@decorator`?
  back: The pattern wraps an object at runtime behind the same interface. `@` is syntax for rebinding a name to a function's result. Rhodes treats them as unrelated.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: How do you write a singleton in Python?
  back: 'Usually don''t: use a module-level object, or `functools.cache` for laziness. It lets tests make separate instances.'
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: What's wrong with mutable globals?
  back: Distant code becomes coupled, and tests can't run independently or in parallel. Easiest to justify for process-wide resources like `os.environ`.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: When is a repository worth it?
  back: Around a real domain with a stable, small query surface. It costs you visibility of queries and doesn't map to transactions or analytics well.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: What's the risk with observers?
  back: Hidden control flow, order dependence, slow or failing listeners. Decide whether listener errors propagate.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Why use a transition table?
  back: Illegal transitions raise an error through `to()`, and you can test the whole table. It doesn't make them unrepresentable, since direct assignment to `state` bypasses it.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: Inheritance or composition for two axes of variation?
  back: Composition. Inheritance gives you one subclass per combination.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: What does indirection cost?
  back: Tens of nanoseconds per layer in CPython on my machine, which rarely matters on a request path. The reader's cost is usually larger.
  lesson: programming/software-design/notes/04-patterns-worth-knowing
- front: What makes a good test?
  back: It fails when behaviour breaks, stays quiet otherwise, runs fast and deterministically, and tests through the public API.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Size vs scope?
  back: Size is resources (process, machine, network). Scope is how much code is validated. Size predicts speed and flakiness.
  lesson: programming/software-design/notes/05-testing-strategy
- front: What's the pyramid's rationale?
  back: Broad tests are slow, flaky and hard to diagnose, so most tests should be narrow. It's a rule of thumb that depends on that assumption being true for you.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Fake vs stub vs mock?
  back: A fake is a working lightweight implementation. A stub returns set values. A mock, in Fowler's sense, verifies calls.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Which do you prefer?
  back: Real if fast and deterministic, then fake, then stub, and interaction checks only when the call is the behaviour.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Classical vs mockist?
  back: Classical uses real objects where practical and verifies state. Mockist mocks collaborators and verifies calls. The risk with mockist style is tests coupled to implementation.
  lesson: programming/software-design/notes/05-testing-strategy
- front: Is 100% coverage good?
  back: It says everything ran, not that anything was checked. An assertion-free suite can hit it. Use coverage to find forgotten code.
  lesson: programming/software-design/notes/05-testing-strategy
- front: What's mutation testing?
  back: 'Inject small faults and see if tests fail. It finds weak assertions but is expensive and noisy: Google restricts it to changed lines and suppresses unproductive mutants.'
  lesson: programming/software-design/notes/05-testing-strategy
- front: What's a contract test for?
  back: Running the same behavioural checks against each implementation of an interface, including fakes, or between consumer and provider.
  lesson: programming/software-design/notes/05-testing-strategy
- front: What's a property test?
  back: It asserts an invariant over generated inputs and shrinks failures. Look for round trips and conservation laws.
  lesson: programming/software-design/notes/05-testing-strategy
- front: How do you handle flakes?
  back: Quarantine, find the nondeterminism, and inject it. Rerunning only postpones the fix, and past about 1% a suite loses trust.
  lesson: programming/software-design/notes/05-testing-strategy
- front: How do you test LLM code?
  back: Script the model for logic tests, record vendor responses for parsing, keep a few live smoke tests, and use evals for quality.
  lesson: programming/software-design/notes/05-testing-strategy
- front: How do you approach a bug you don't understand?
  back: Reproduce it, form a hypothesis with a prediction, test one thing at a time, ask what changed, and keep a test afterwards.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: First step in an outage?
  back: 'Stabilise: roll back or shed load. Diagnosis comes after.'
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: What's post-mortem debugging?
  back: Inspecting frames after an uncaught exception, via `python -m pdb` or `pdb.pm()`, with state intact.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: '`tottime` vs `cumtime`?'
  back: Time in the function alone vs including callees.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: Deterministic vs sampling profiler?
  back: Deterministic hooks every call, and so gives exact counts with per-call overhead. Sampling looks at stacks periodically, with lower, fixed overhead and statistical results.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: How do you read a flame graph?
  back: Width is share of samples, y is stack depth, the x order is alphabetical and isn't time. Look for wide plateaus on top.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: Why might a profile look fine while requests are slow?
  back: It may count on-CPU time only, and the request is waiting on a network or lock.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: How do you profile a production Python process?
  back: A sampling profiler such as py-spy attaching from outside, with suitable permissions.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: What's `faulthandler` for?
  back: Python tracebacks on segfaults, after a timeout, or on a signal, even when the interpreter is badly broken.
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: What's new for debugging in 3.14?
  back: 'PEP 768: `python -m pdb -p <pid>` and `sys.remote_exec`, using safe points in the interpreter.'
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: How would you diagnose a hang?
  back: 'Dump every thread''s stack: `py-spy dump` or `faulthandler`. Look for threads waiting on each other''s locks.'
  lesson: programming/software-design/notes/06-debugging-and-profiling
- front: What are Git's main object types?
  back: Blob (file bytes), tree (names to blobs and trees), commit (a tree, parents, author and message). All addressed by content hash.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What's a branch?
  back: 'A movable reference: a small file holding a commit hash. `HEAD` points to the current branch.'
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: Why does rebase change hashes?
  back: The hash covers the parent, so a replayed commit is a new commit even with an identical patch.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: When shouldn't you rebase?
  back: When commits exist outside your repository and others may have based work on them.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: How do you recover from a bad `reset --hard`?
  back: Find the old tip in `git reflog` and reset to it. Commits survive, uncommitted edits don't. It's local, and entries expire.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What does `git bisect` need to work well?
  back: A reliable automated check, one good and one bad commit, and history whose commits can each be tested.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What do the exit codes in `bisect run` mean?
  back: 0 is good, 1 to 127 is bad except 125, which skips. Anything else aborts.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What's `range-diff` for?
  back: Comparing two versions of a commit series, for example between review rounds after a rebase.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What does a good commit message contain?
  back: A short imperative subject, then the reason, and what you considered and rejected.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: Why keep changes small, and what does it cost?
  back: Faster and better review, easier rollback and bisect. The cost is that the overall direction is harder to see, so link a design doc.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What's Google's standard for approving a change?
  back: It definitely improves overall code health, even if it isn't perfect.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What should a reviewer look at first?
  back: Design, before functionality, complexity and tests. Automate style.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What's trunk-based development, and what does it need?
  back: Small batches merged to trunk at least daily. It needs fast tests, the habit of small changes, and quick review.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: When is a design doc worth it?
  back: When the solution is ambiguous. If it has no trade-offs, it's an implementation manual and you should write the code.
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
- front: What's an ADR?
  back: 'A short numbered record of one decision: context, decision, status, and all consequences. Superseded rather than deleted.'
  lesson: programming/software-design/notes/07-git-code-review-and-design-docs
---
