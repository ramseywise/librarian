---
title: TypeScript Discriminated Unions and Narrowing
tags: [foundations, pattern]
summary: "Model 'one of these' as a union with a literal `kind` field, narrow by control flow, and end the `switch` with `const x: never = s` so adding a member without handling it is a compile error; type predicates package a check but are trusted, not verified."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--03-unions-and-narrowing.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# TypeScript Discriminated Unions and Narrowing

A union says "one of these"; narrowing is how you find out which one. Discriminated unions with
an exhaustive `switch` are TypeScript's most useful pattern. It plays the role of Python's tagged
unions with `match`.

## Unions only expose what every member has

```ts
type ID = number | string;
function show(id: ID): string {
  return id.toUpperCase();   // error: toUpperCase doesn't exist on number
}
```

To use more than the common members, narrow first.

## Narrowing by control flow

The checker follows control flow and narrows the type inside each branch:

| Check | Narrows | Example |
|---|---|---|
| `typeof x === 'string'` | Primitives | `if (typeof id === 'string') id.toUpperCase()` |
| `x instanceof Date` | Class instances | `catch (e) { if (e instanceof Error) e.message }` |
| `'role' in x` | Object shapes, by property | `if ('role' in person) person.role` |
| `x === null`, `x == null`, `if (x)` | Nullability | `if (!user) return;` then `user` is non-null |
| `x.kind === 'circle'` | Discriminated unions | below |
| `Array.isArray(x)` | Arrays | |

Narrowing also holds after an early `return` or `throw`, which is why **guard clauses** at the top
of a function are the idiomatic form.

## The pattern: discriminant plus exhaustive `never`

Give each member a literal `type` (or `kind`) field. Checking that field narrows to the member:

```ts
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rect'; width: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case 'circle':
      return Math.PI * s.radius ** 2;       // s is the circle member here
    case 'rect':
      return s.width * s.height;
    default: {
      const unreachable: never = s;          // compile error if a member is added and not handled
      throw new Error(`unhandled: ${JSON.stringify(unreachable)}`);
    }
  }
}
```

The `never` assignment is the mechanism: once every case is handled, `s` has been narrowed to
`never` in `default`, so the assignment compiles. Add a member without a case and `s` is that
member there, so the assignment fails — the checker finds every switch you forgot to update.
The runtime `throw` remains for values that arrive from outside the type system.

Where it applies:

- API results: `{ ok: true; data } | { ok: false; error }` (combined with generics as
  `Result<T, E>` in [[TypeScript Generics and Type Transformations]]).
- Redux-style actions.
- LLM content blocks (`block.type === 'text'`) and `stop_reason` dispatch — see
  [[TypeScript for AI Apps]]. There the API adds new values over time, so the `default` branch must
  handle the unknown case at runtime rather than only assert `never`.
- Zod mirrors it at runtime with `z.discriminatedUnion('type', [A, B])` ([[Runtime Validation with Zod]]).

## Type predicates

A function returning `x is T` packages a check for reuse:

```ts
function isAdmin(p: Person): p is Admin {
  return p.type === 'admin';
}
const admins = people.filter(isAdmin);    // Admin[], not Person[]
```

**The predicate is a promise you make, and the checker trusts it without verifying.** A wrong body
silently mis-narrows — it is an `as` cast in a function signature. Since TS 5.5, simple arrows like
`(p) => p.type === 'admin'` are inferred as predicates automatically.

## `unknown` at the boundary

```ts
const v: unknown = JSON.parse(input);
if (typeof v === 'object' && v !== null && 'name' in v && typeof v.name === 'string') {
  v.name;   // string
}
```

Narrowing `unknown` by hand works but gets painful quickly; past one or two fields it is the job of
a schema library. The choice between a real type, `unknown` and a generic is laid out in
[[TypeScript any Escapes]].

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript for Python Developers]] — prerequisite-for
- [[TypeScript any Escapes]] — related (unknown plus narrowing is one of its three escapes)
- [[TypeScript Generics and Type Transformations]] — extends
- [[Runtime Validation with Zod]] — extends
- [[TypeScript for AI Apps]] — instance-of
- [[Brand the Funnel's Output]] — related (where a union cannot express provenance, a nominal brand can)
