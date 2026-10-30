---
imported_hash: 045b3d27985f3797
title: 7 — Modules, tsconfig and Tooling
summary: '// main.ts import Calculator, { add } from ''./math.ts''; import type { Shape } from ''./shapes.ts''; // type-only: erased completely import  as path from ''node:path''; // the node: prefix for built-ins'
order: 8
kind: reading
section: Notes
source: learn-ai-engineering/programming/typescript/notes/07-modules-and-tooling.md
---

# 7 — Modules, `tsconfig` and Tooling

> Most "TypeScript is hard" pain is really module and config pain. Use one modern setup and stick with it.

---

## ES modules

```ts
// math.ts
export function add(a: number, b: number) { return a + b; }
export default class Calculator {}
export type { Shape } from './shapes.ts';

// main.ts
import Calculator, { add } from './math.ts';
import type { Shape } from './shapes.ts';     // type-only: erased completely
import * as path from 'node:path';             // the node: prefix for built-ins
```

- Put `"type": "module"` in `package.json` so that `.js` and `.ts` files are ES modules. CommonJS (`require`, `module.exports`) is legacy, but you'll still see it in older packages.
- **Prefer named exports.** They rename consistently and are easier to auto-import.
- `import type` says that nothing exists at runtime. Node's type stripping needs it: a plain `import { Shape }` of a type-only export fails when the code runs.
- In ESM, `__dirname` doesn't exist. Use `import.meta.dirname` (Node 20.11+).

## A modern `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target": "es2023",
    "module": "nodenext",              // or "preserve" + "moduleResolution": "bundler" with a bundler
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "verbatimModuleSyntax": true,      // import type must be explicit
    "erasableSyntaxOnly": true,        // no enums or namespaces: what Node can strip
    "skipLibCheck": true,
    "noEmit": true                     // type-check only; something else runs the code
  }
}
```

The practice project's [`tsconfig.json`](../practice/tsconfig.json) leaves out the last two strictness options, because the vendored exercises predate them.

## Running TS

| Tool | Use |
|---|---|
| `node file.ts` (22.18+) | Run scripts with no build step. It strips types and **doesn't type-check** |
| `tsc --noEmit` | Type-check (CI, editor). TS 7 is the native Go port, about 10× faster |
| `tsx`, `bun`, `deno` | Alternatives that run TS directly and support more syntax |
| Vite / esbuild / tsup | Bundle for the browser or publish a library |
| ESLint + `typescript-eslint` | Catches bugs types can't, such as floating promises |
| Prettier or Biome | Formatting. Don't argue about style |
| `node --test` / Vitest | Testing ([practice/tests](../practice/tests/)) |

## Declaration files (`.d.ts`)

Untyped JavaScript packages need type declarations:

1. Check DefinitelyTyped first: `npm i -D @types/lodash`.
2. Otherwise, write your own:

```ts
// types/str-utils.d.ts
declare module 'str-utils' {
  export function strReverse(s: string): string;
}
```

A `.d.ts` file contains types only. It declares what exists at runtime somewhere else.

## Module augmentation

To add members to a library's types, for example a plugin that attaches methods:

```ts
import 'date-wizard';
declare module 'date-wizard' {
  interface DateDetails { hours: number }    // merges with the library's interface
}
```

Interfaces merge, and type aliases don't. That is the main practical reason libraries expose interfaces.

---

## Exercises

[`practice/typescript-exercises/11`](../practice/typescript-exercises/11/index.ts) and [`12`](../practice/typescript-exercises/12/index.ts) (write `declarations/*/index.d.ts`), and [`13`](../practice/typescript-exercises/13/index.ts) (module augmentation). From `practice/`, check with `node check.ts exercises/11/` and so on. The upstream fake `node_modules` folders are called `vendor/` here; see [`NOTICE.md`](../practice/typescript-exercises/notice.md).
