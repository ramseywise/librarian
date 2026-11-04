---
imported_hash: 1c66681a0602c6e8
decks:
- learn-ai-engineering/programming/typescript/slides/deck.yaml
cards:
- front: Which command checks types, and which runs code?
  back: '`node file.ts` strips types without checking them, so `tsc --noEmit` is a separate step you must run.'
  lesson: programming/typescript/notes/01-js-for-python-devs
- front: Which JavaScript behaviours catch Python developers?
  back: '`[]` is truthy, `sort()` compares strings, `===` compares references, and `const` doesn''t stop mutation.'
  lesson: programming/typescript/notes/01-js-for-python-devs
- front: What is the difference between any and unknown?
  back: '`any` turns checking off and spreads. `unknown` forces you to narrow first, so use it for outside data.'
  lesson: programming/typescript/notes/02-everyday-types
- front: Does TypeScript check a type's name or its shape?
  back: TypeScript checks shape, not name. Annotate parameters, returns and exports, and let inference do the rest.
  lesson: programming/typescript/notes/02-everyday-types
- front: How does narrowing work?
  back: On a union you can use only what every member has. Each branch removes members until one type is left.
  lesson: programming/typescript/notes/03-unions-and-narrowing
- front: How do you make a switch exhaustive?
  back: Give each member a literal `kind` and assign the `default` branch to `never`, so a new member becomes a compile error.
  lesson: programming/typescript/notes/03-unions-and-narrowing
- front: How do you type a safe property getter?
  back: '`keyof T` is the union of keys and `T[K]` is that property''s type. A type parameter should appear at least twice.'
  lesson: programming/typescript/notes/04-generics
- front: Which utility types do you use weekly?
  back: Derive payload and wrapper types with `Partial`, `Pick`, `Omit` and `ReturnType` rather than repeating fields.
  lesson: programming/typescript/notes/05-type-transformations
- front: How does a mapped type build a new type?
  back: A mapped type loops over keys to build a new object type. `Required` and `Readonly` are built this way.
  lesson: programming/typescript/notes/05-type-transformations
- front: What do infer and distribution do in a conditional type?
  back: '`infer` captures part of a type. A bare type parameter distributes over a union, unless both sides are in brackets.'
  lesson: programming/typescript/notes/05-type-transformations
- front: In what order do sync code, promises and timers run?
  back: Sync code finishes first, then all microtasks, then the next timer or I/O callback, so a timer of 0 still waits.
  lesson: programming/typescript/notes/06-async
- front: How do you run two async calls in parallel?
  back: A promise starts when created, so `Promise.all` runs calls in parallel. It fails fast, and `allSettled` doesn't.
  lesson: programming/typescript/notes/06-async
- front: What goes wrong with `forEach` and `race` in async code, and what do you use instead?
  back: '`forEach` doesn''t await its callbacks and `race` doesn''t cancel the loser, so use `for…of` and `AbortSignal`.'
  lesson: programming/typescript/notes/06-async
- front: What does a modern TypeScript setup need?
  back: Use ES modules, `strict` and `import type`, and run `tsc --noEmit` in CI. Most TypeScript pain is config pain.
  lesson: programming/typescript/notes/07-modules-and-tooling
- front: How do you get a type and a runtime check from one definition?
  back: Parse, don't validate. Turn `unknown` into a precise type once at the edge, and trust it everywhere after that.
  lesson: programming/typescript/notes/08-runtime-validation-zod
- front: What should your loop do for each stop_reason?
  back: Handle `stop_reason` in an exhaustive `switch` with a `default`, because the API adds new values over time.
  lesson: programming/typescript/notes/09-typescript-for-ai-apps
- front: Why must you never assume content[0] is text?
  back: Content is a discriminated union of blocks, and with thinking on the first often isn't text, so narrow on `type`.
  lesson: programming/typescript/notes/09-typescript-for-ai-apps
- front: How do you treat `strict`, `any`, unions and outside data?
  back: Turn on `strict`, avoid `any` and `as`, make unions exhaustive, and parse outside data once at the edge.
  lesson: programming/typescript/notes/03-unions-and-narrowing
- front: Where do you go after TypeScript?
  back: Next is the AI engineering pillars, after finishing Python 03 and TypeScript 09, then the type challenges for practice.
  lesson: programming/typescript/notes/09-typescript-for-ai-apps
---
