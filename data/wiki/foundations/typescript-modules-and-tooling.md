---
title: TypeScript Modules and Tooling
tags: [foundations, reference]
summary: "Most 'TypeScript is hard' pain is module and config pain: use ESM with named exports and explicit `import type`, one strict tsconfig (nodenext, verbatimModuleSyntax, erasableSyntaxOnly, noEmit), run with Node type stripping and check with tsc separately, and use .d.ts files and module augmentation for untyped or extended libraries."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--07-modules-and-tooling.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--01-js-for-python-devs.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# TypeScript Modules and Tooling

Most "TypeScript is hard" pain is really module and config pain. Use one modern setup and stick
with it.

## ES modules

```ts
// math.ts
export function add(a: number, b: number) { return a + b; }
export default class Calculator {}
export type { Shape } from './shapes.ts';

// main.ts
import Calculator, { add } from './math.ts';
import type { Shape } from './shapes.ts';     // type-only: erased completely
import * as path from 'node:path';             // node: prefix for built-ins
```

- `"type": "module"` in `package.json` makes `.js`/`.ts` files ES modules. CommonJS (`require`,
  `module.exports`) is legacy but still appears in older packages.
- **Prefer named exports** — they rename consistently and auto-import better.
- **`import type` is load-bearing under type stripping.** It says nothing exists at runtime. A plain
  `import { Shape }` of a type-only export fails *when the code runs* under Node's stripping.
  `verbatimModuleSyntax` makes the checker enforce the distinction.
- In ESM `__dirname` does not exist; use `import.meta.dirname` (Node 20.11+).

## A modern `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target": "es2023",
    "module": "nodenext",              // or "preserve" + "moduleResolution": "bundler" with a bundler
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "verbatimModuleSyntax": true,      // import type must be explicit
    "erasableSyntaxOnly": true,        // no enums or namespaces: only what Node can strip
    "skipLibCheck": true,
    "noEmit": true                     // type-check only; something else runs the code
  }
}
```

`strict` from day one — retrofitting it later is painful. `erasableSyntaxOnly` exists because
enums and namespaces generate runtime code and so cannot simply be stripped.

## Running vs checking are separate steps

| Tool | Use |
|---|---|
| `node file.ts` (22.18+) | Runs scripts with no build step. Strips types and **does not type-check** |
| `tsc --noEmit` | Type-check in CI and editor. TS 7 is the native Go port, about 10x faster |
| `tsx`, `bun`, `deno` | Run TS directly with broader syntax support |
| Vite / esbuild / tsup | Bundle for the browser or publish a library |
| ESLint + `typescript-eslint` | Bugs types cannot catch, such as floating promises |
| Prettier or Biome | Formatting |
| `node --test` / Vitest | Testing |

The trap: a script that runs under `node file.ts` has proven nothing about its types. CI must run
`tsc --noEmit` separately. The lint layer is where `no-explicit-any` and `no-floating-promises`
live — see [[TypeScript any Escapes]] and [[TypeScript Async Patterns]].

## Declaration files (`.d.ts`)

Untyped JS packages need declarations:

1. Check DefinitelyTyped first: `npm i -D @types/lodash`.
2. Otherwise write your own:

```ts
// types/str-utils.d.ts
declare module 'str-utils' {
  export function strReverse(s: string): string;
}
```

A `.d.ts` file contains types only; it declares what exists at runtime somewhere else. Like `as`,
it is an unchecked claim about the runtime.

## Module augmentation

To add members to a library's types (for example a plugin that attaches methods):

```ts
import 'date-wizard';
declare module 'date-wizard' {
  interface DateDetails { hours: number }    // merges with the library's interface
}
```

Interfaces merge and type aliases do not — the main practical reason libraries expose interfaces.

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript for Python Developers]] — prerequisite-for
- [[TypeScript any Escapes]] — related (the lint rules this toolchain runs)
- [[TypeScript Async Patterns]] — related (no-floating-promises is a tooling-level async guard)
- [[Triage Casts by Mechanical Probe]] — related (generated type files as a boundary contract that drifts when not regenerated)
