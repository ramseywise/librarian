---
title: TypeScript for Python Developers
tags: [foundations, reference]
summary: "TypeScript is JavaScript with a checker that runs and then disappears, so learn the runtime traps first (`==` coercion, string-comparing `sort()`, truthy `[]`, reference equality), then annotate boundaries, prefer `unknown` over `any`, and turn on `strict` from day one."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--01-js-for-python-devs.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--02-everyday-types.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# TypeScript for Python Developers

TypeScript is JavaScript with a type checker in front. The checker runs and then disappears;
what executes is JavaScript. So the runtime has to be learned first, and the type system second.

## How TS runs

| Step | What happens |
|---|---|
| `tsc --noEmit` | Type-checks only. Nothing runs |
| `node file.ts` (22.18+) | **Strips** the types and runs the rest. No checking at all |
| `tsc` / bundler | Emits `.js` for production |

There are **no runtime types**. `x as User` checks nothing, and an `interface` produces no code.
Anything from outside the program must be parsed with a schema — see [[Runtime Validation with Zod]].
Tooling details are in [[TypeScript Modules and Tooling]].

## Python to JavaScript: the traps

| Python | JS / TS | Watch out |
|---|---|---|
| `x = 1` | `const x = 1` (`let` if reassigned) | Never use `var` |
| `None` | `null` **and** `undefined` | `x == null` catches both; otherwise always `===` |
| `list.sort()` | `xs.sort()` | Sorts **in place, comparing as strings** by default. Use `sort((a, b) => a - b)` |
| `dict` with arbitrary keys | `Map` | Plain-object keys are always strings and inherit prototype keys |
| `set` | `Set` | Compares objects by reference |
| `for x in xs` | `for (const x of xs)` | `for…in` iterates **keys** — never on arrays |
| `d.get(k, 0)` | `d.get(k) ?? 0` | `??` treats only `null`/`undefined` as missing; `\|\|` also replaces `0` and `""` |
| `a and a.b` | `a?.b` | Optional chaining |
| `try/except` | `try/catch` | The caught value is `unknown` — narrow with `instanceof Error` |
| `a, *rest = xs` | `const [a, ...rest] = xs` | Objects destructure too: `const { id, ...others } = user` |

## Truthiness and equality

- Falsy: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. **`[]` and `{}` are truthy** —
  the opposite of Python.
- `==` coerces (`"1" == 1` is true). Always use `===`; the one useful exception is `x == null`.
- `===` compares objects and arrays **by reference**: `[1] === [1]` is false.
- Numbers are 64-bit floats: `0.1 + 0.2 !== 0.3`; integers are exact only to 2^53 (use `bigint` beyond).

## References and copies

```ts
const a = { tags: ['x'] };
const b = { ...a };              // shallow copy, like dict(a)
b.tags.push('y');                // a.tags changes too: the inner array is shared
const c = structuredClone(a);    // deep copy, like copy.deepcopy
```

`const` stops **reassignment**, not **mutation**. For immutability use `readonly` types or
`Object.freeze`. Classes exist (`#count` is truly runtime-private, unlike Python's `_name`), but
most TS code favours plain objects, functions and union types over class hierarchies.

## Everyday types

| Type | Meaning |
|---|---|
| `string`, `number`, `boolean`, `bigint`, `symbol` | Primitives — lowercase (`String` is the wrapper object) |
| `null`, `undefined` | Separate types under `strict`; a `string` cannot be `null` unless written `string \| null` |
| `unknown` | Could be anything; you must narrow before use. The safe top type |
| `any` | Turns the checker off, and spreads to everything it touches |
| `never` | A value that cannot exist: an always-throwing function, an exhausted union |
| `void` | A function that returns nothing useful |

`const name = 'Ada'` infers the **literal** type `'Ada'`; `as const` makes a whole object
readonly with literal property types. Tuples (`[string, number]`) fix length and per-position types.

**`interface` vs `type`.** Use `interface` for object shapes, especially ones you will extend; use
`type` for everything else — only `type` can name unions, tuples and primitives. Interfaces merge
(the reason libraries expose them for augmentation); type aliases do not.

**Structural typing.** TS checks shape, not name — any object with `x: number; y: number` *is* a
`Point`, much like a Python `Protocol`. The exception is the **excess property check**: an object
*literal* with extra properties is an error, because that is usually a typo.

## Rules of thumb

- Types are erased. `as` checks nothing, so parse anything from outside with a schema.
- Annotate function signatures and exports; let inference handle the rest. An exported function's
  signature is its contract, and the annotation catches accidental changes.
- Use `unknown` instead of `any`, and narrow before use (the three escapes from `any` are in
  [[TypeScript any Escapes]]).
- Model "one of these" as a discriminated union and end the `switch` with a `never` check
  ([[TypeScript Discriminated Unions and Narrowing]]).
- Always `await` or return a promise; `Promise.all` for independent work, a limit for large
  fan-outs ([[TypeScript Async Patterns]]).
- Turn on `strict` from day one — it enables `strictNullChecks` and `noImplicitAny`; turning it on
  later is painful. Consider `noUncheckedIndexedAccess`, which makes `xs[i]` type `T | undefined`.

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript any Escapes]] — extends
- [[TypeScript Discriminated Unions and Narrowing]] — extends
- [[TypeScript Generics and Type Transformations]] — extends
- [[TypeScript Modules and Tooling]] — related (the build/run side of the same runtime facts)
- [[Runtime Validation with Zod]] — extends
