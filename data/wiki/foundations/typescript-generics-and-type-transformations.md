---
title: TypeScript Generics and Type Transformations
tags: [foundations, concept]
summary: "Generics keep the caller's type through a function (a type parameter should appear at least twice); keyof/T[K], overloads, utility, mapped, conditional and template-literal types derive new types from one source — and type-level code is real code, so stop before infer goes three levels deep."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--04-generics.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--05-type-transformations.md
---

# TypeScript Generics and Type Transformations

A generic is a type parameter: one function works for many types *without forgetting which type it
was given*. Type transformations go one step further — write a type once and derive the rest.

## Generics

```ts
function first(xs: any[]): any { return xs[0]; }          // the type is lost
function first<T>(xs: T[]): T | undefined { return xs[0]; } // first([1, 2]): number | undefined
```

`T` is inferred from the arguments, so callers rarely write `first<number>(…)`. It is Python's
`TypeVar` (`def first(xs: list[T]) -> T`).

**Constraints.** `T extends { length: number }` means "must be assignable to" — a bound on what
callers may pass. `longest('ab', 'abc')` compiles; `longest(10, 20)` does not.

**`keyof` and indexed access.**

```ts
function get<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }
get({ id: 1, name: 'Ada' }, 'name');   // string
get({ id: 1, name: 'Ada' }, 'nope');   // error
```

| Syntax | Meaning |
|---|---|
| `keyof T` | Union of `T`'s keys |
| `T[K]` | Type of property `K` on `T` |
| `T[number]` | Element type of an array or tuple |
| `typeof value` | The type of a *value*, in type position |

**Generics plus discriminated unions.** `interface ApiResponse<T> { status; data?: T; error? }`
lets `data` be absent on success. Better:

```ts
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
```

so `value` exists exactly when `ok` is true (see [[TypeScript Discriminated Unions and Narrowing]]).

**Overloads.** When the return type depends on an argument *value* (`kind: 'user'` returns
`User[]`, `kind: 'admin'` returns `Admin[]`), one generic signature is not enough. List the call
shapes as overload signatures; the implementation signature is never visible to callers.

### Rules of thumb

- **A type parameter should appear at least twice** — linking an input to an output. Used once, it
  is a disguised `any`/`unknown`; write the concrete type or `unknown` instead.
- Let `T` be inferred rather than making callers write it.
- Constrain as loosely as the body allows.

This is the third escape from `any` in [[TypeScript any Escapes]]: a function that only *moves* a
value needs a type parameter, not `unknown`.

## Building types from types

**Utility types** (weekly use):

| Utility | Typical use |
|---|---|
| `Partial<T>` / `Required<T>` | Update payloads / after defaults are applied |
| `Readonly<T>` | Config, frozen state |
| `Pick<T, K>` / `Omit<T, K>` | View models / create payloads without a server ID |
| `Record<K, V>` | Lookup tables: `Record<Status, string>` |
| `Exclude<U, X>` / `Extract<U, X>` | Remove or keep union members |
| `NonNullable<T>` | Strip `null`/`undefined` |
| `ReturnType<F>` / `Parameters<F>` | Typing wrappers |
| `Awaited<T>` | `Awaited<ReturnType<typeof fetchUser>>` |

**Intersections.** `A & B` has every property of both — combine types without repeating fields:
`Omit<User, 'type'> & Omit<Admin, 'type'> & { type: 'powerUser' }`.

**Mapped types** loop over keys — this is how the utilities are built:

```ts
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
```

`-readonly` / `-?` remove modifiers (that is `Required`); `as` remaps or filters keys; mapping a key
to `never` drops it.

**Conditional types.**

```ts
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;     // infer destructures a type
type MyAwaited<T> = T extends PromiseLike<infer V> ? MyAwaited<V> : T;  // recursion allowed
```

**Distribution trap:** when `T` is a bare type parameter and receives a union, the conditional
applies to each member separately — `IsString<string | number>` is `boolean`, not `false`. Wrap
both sides (`[T] extends [string]`) to turn distribution off.

**Template literal types:** `` `on${Capitalize<'click' | 'focus'>}` `` is `'onClick' | 'onFocus'`;
combined with `infer` they parse strings at the type level (`TrimLeft`).

## When to stop

Type-level code is real code: hard to read, hard to debug, slow to compile. Use utility types
freely, mapped types sometimes, and deep conditional recursion only in libraries. If an application
type needs `infer` three levels deep, a simpler runtime design is usually better.

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript for Python Developers]] — prerequisite-for
- [[TypeScript Discriminated Unions and Narrowing]] — prerequisite-for
- [[TypeScript any Escapes]] — related (the generic escape from `any`)
- [[Runtime Validation with Zod]] — related (`z.infer` derives the static type from a schema instead of by type transformation)
