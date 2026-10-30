---
title: Runtime Validation with Zod
tags: [foundations, pattern]
summary: "Types are erased, so env vars, JSON bodies, files, tool inputs and LLM output are really `unknown`: parse them once at the boundary with a zod schema that yields both the runtime check and the static type (`z.infer`), then trust the typed value everywhere after — parse, don't validate."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--08-runtime-validation-zod.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# Runtime Validation with Zod

Types are erased at runtime, so any data from outside the program — JSON bodies, env vars, files,
LLM output — is really `unknown`. Parse it into a typed value at the boundary, once, and trust it
everywhere after that. Zod is the TypeScript equivalent of Pydantic.

## The problem: `as` is "trust me"

```ts
const user = (await res.json()) as User;   // compiles. Checks nothing.
user.email.toLowerCase();                  // crashes at runtime if the API sent { mail: … }
```

The fix is a schema that validates at runtime **and** produces the static type, so the two cannot
drift apart.

## Zod basics (v4)

```ts
import { z } from 'zod';

const User = z.object({
  id: z.number().int().positive(),
  email: z.email(),
  name: z.string().min(1),
  role: z.enum(['user', 'admin']).default('user'),
  tags: z.array(z.string()).optional(),
});
type User = z.infer<typeof User>;   // static type derived from the schema

User.parse(data);                    // a User, or throws ZodError
const r = User.safeParse(data);      // { success: true, data } | { success: false, error }
if (!r.success) console.log(r.error.issues);   // [{ path: ['email'], message: … }, …]
```

`safeParse` returns a discriminated union — narrow on `success` exactly as in
[[TypeScript Discriminated Unions and Narrowing]].

| Need | Zod |
|---|---|
| Optional / nullable | `.optional()`, `.nullable()`, `.nullish()` |
| Defaults | `.default(v)` — input may omit the field; output always has it |
| Strings to numbers/booleans | `z.coerce.number()` |
| Clean up while parsing | `.trim()`, `.toLowerCase()`, `.transform(fn)` |
| Custom rules | `.refine((v) => …, 'message')` |
| Tagged unions | `z.discriminatedUnion('type', [A, B])` |
| Reject unknown keys | `z.strictObject({…})` |
| Update payloads | `User.partial()`, `.pick({…})`, `.omit({…})` |

**Env-flag trap:** `z.coerce.boolean()` treats the string `"false"` as `true` (any non-empty string
is truthy). For env flags use `z.enum(['true', 'false'])` instead.

## Parse, don't validate

Turn `unknown` into a precise type at the edge, then pass the typed value around. Do not keep
re-checking deep inside the code (Alexis King's "Parse, don't validate").

| Boundary | Example |
|---|---|
| Config | `const config = Config.parse(process.env)` at startup, so a bad deploy fails fast |
| HTTP | Parse request bodies in the handler, and API responses in the client |
| Files | `Schema.parse(JSON.parse(text))` |
| LLM output | Use structured output so the model is constrained to the schema, **and still parse the result** |
| Tool inputs | Parse model-supplied tool arguments before running anything |

The LLM rows are the important ones for agent work: constrained decoding narrows what the model can
emit, but the parse is still the check your code relies on (see [[Structured Output]] — a schema
guarantees shape, not truth).

## One schema, many uses

A zod schema also produces JSON Schema (`z.toJSONSchema(User)`). That is how SDKs turn a zod object
into an LLM tool definition or structured-output format: write the shape once and get the static
type, the runtime validation, and the schema the model sees. Because the model reads that schema,
field names and descriptions are prompt text ([[Tool Definitions as Prompts]]). The same
zod-as-tool-parameters idiom appears in [[ADK JS TypeScript Patterns]], and the SDK-level version
in [[TypeScript for AI Apps]].

Named zod adapters are also one of the three outcomes when triaging a population of unchecked
casts — see [[Triage Casts by Mechanical Probe]].

## Alternatives

Valibot (tiny bundles), ArkType (TS-like syntax, fast) and TypeBox (JSON Schema first) solve the
same problem. Pick one per codebase. Zod has the largest ecosystem, and the Anthropic SDK ships zod
helpers.

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript for Python Developers]] — prerequisite-for
- [[TypeScript any Escapes]] — prerequisite-for (`unknown` is the type a schema parse starts from)
- [[Python Type Hints and Dataclasses]] — alternative-to (Pydantic plays the same role in Python)
- [[TypeScript for AI Apps]] — extends
- [[Structured Output]] — related (the model-side constraint; zod is the code-side parse)
- [[ADK JS TypeScript Patterns]] — instance-of
- [[Triage Casts by Mechanical Probe]] — related (zod adapters replace double casts at a boundary)
