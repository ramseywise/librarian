---
name: nextjs
description: >
  Architecture and coding rules for Next.js App Router applications with TypeScript, Tailwind CSS,
  Zod, and Google ADK JS. Use when building or extending Next.js pages, API routes, React
  components, custom hooks, ADK agents/tools, or streaming endpoints in this codebase. Also
  triggers when working on: component state with hooks, structured agent output schemas,
  FunctionTool definitions, NDJSON streaming, Tailwind dark mode, forwardRef forms, or
  postMessage iframe communication. Use for any work in ts_google_adk/ or librarian/app/ui/.
  Triggers on: "add a UI component", "new agent tool", "new route", "output schema change",
  "streaming endpoint", "MCP API call", "dark mode", "iframe navigation".
---

# Next.js + React + ADK JS

Rules for the `ts_google_adk` application: Next.js 16 App Router, React 19, TypeScript 5 strict,
Tailwind CSS 4, Zod 4, Google ADK JS (`@google/adk`), MikroORM + PostgreSQL.

## Before You Build

Answer these before writing component or API code. A short design note here prevents schema breakage and avoids client/server boundary mistakes.

**Routing & layout**
- New page/route, or extending an existing one? Does it affect `layout.tsx`? (Layout changes hit all child routes.)
- Where does the `"use client"` boundary go? Push it as far down the tree as possible — never on layouts or pages that can stay server components.

**Data & streaming**
- Fetched server-side (RSC) or client-side (hook in `src/app/types/`)?
- Does it stream? → NDJSON via `/api/...` route + `use-chat.ts` pattern. Or SSE? (Use NDJSON — it's the project standard.)
- What are the loading and error states? Are they already handled in the hook, or does this need new state?

**Agent output schema** (`src/agents/accounting-schema.ts`)
- Does this add a new UI element? → New **optional** field on `accountingOutputSchema`. Never add required fields — they break existing sessions.
- Does it need a new `FunctionTool`? → One file per domain in `src/agents/tools/`. Add tool → register in agent → update system prompt → update schema.
- Does the schema change need an end-to-end test? (LLM must emit valid JSON matching the new shape.)

**Component design**
- New hook slice in `src/app/types/`, or composing existing ones? (No prop drilling past 2 levels.)
- Does it need an imperative ref? (Table row → form pre-fill → `forwardRef` pattern.)
- Where does it render in `AssistantMessage`? Conditional on the new schema field?

**MCP API Integration**
- What endpoints does this use? Does `mcpRequest<T>()` support the needed options?
- Any sideloading required? (`include: "invoice.lines,invoice.contact"`)

---

## File layout

```
src/
├── app/
│   ├── page.tsx              # Root chat UI — thin composition root ("use client")
│   ├── layout.tsx            # App Router layout + theme handling
│   ├── globals.css           # Tailwind imports only
│   ├── translations.ts       # i18n strings
│   ├── types/                # Hooks + shared UI types (Message, SessionInfo…)
│   │   ├── chat.ts           # Message interface
│   │   ├── use-chat.ts       # Streaming chat logic
│   │   ├── use-sessions.ts   # Session CRUD + history
│   │   └── use-bootstrap.ts  # Locale, theme, init
│   └── components/
│       ├── chat/             # Chat UI components
│       └── forms/            # forwardRef forms (imperative pre-fill from table rows)
├── agents/
│   ├── index.ts              # Agent registry
│   ├── accounting-ts         # LlmAgent definition + system prompt
│   ├── accounting-schema.ts  # Output schema (Zod) — the agent↔UI contract
│   └── tools/                # One FunctionTool file per domain
├── lib/                      # MCP client, session-service, navigation, genai-client
└── types/                    # Domain interfaces (Invoice, Product, Quote…) — plain TS, not Zod
```

## TypeScript

- Strict mode is on — trust the compiler, don't cast with `as` to silence errors
- Domain models in `src/types/` are plain interfaces, not Zod schemas
- Infer types from Zod with `z.infer<typeof schema>` — never duplicate a type by hand
- Use `unknown` and narrow instead of `any`

## React + components

- `"use client"` only at the leaf that actually uses browser APIs or hooks — never on layouts
- `page.tsx` is a thin composition root: compose hooks, pass props, render nothing complex
- State lives in hook slices in `src/app/types/` — one hook per concern (chat, sessions, bootstrap)
- `forwardRef` for forms that need imperative methods (e.g., table row click pre-fills a field)
- No prop drilling past 2 levels — add a hook slice instead

## Styling

- Tailwind utility classes only — no inline styles, no CSS modules
- Dark mode uses `dark:` prefix; the theme class is on `<html>`, not `<body>` (set by middleware)
- No magic pixel values — use Tailwind spacing scale

## ADK Agents + Tools

- Each tool is a `FunctionTool` **singleton at module level** in `src/agents/tools/<domain>.ts`
- Tool parameters: Zod `z.object({...})` with `.describe()` on every field — the LLM reads these as documentation
- Tool `execute()`: async, transforms the raw API response before returning — agent never sees raw API shape
- Model string lives in the `LlmAgent` definition only — never in tools or lib code
- When adding a capability: add tool → register in agent → update system prompt → update output schema if new UI needed

## Structured output (output schema)

`src/agents/accounting-schema.ts` is the contract between agent and UI. Every optional field maps to a UI component in `AssistantMessage`.

- Add new UI as a new **optional** field — never add required fields (breaks existing sessions)
- Use Zod `.describe()` on every field — the LLM treats these as output instructions
- After changing the schema, test end-to-end: the LLM must emit valid JSON matching the new shape

Adding a UI element checklist:
1. Add optional field to `accountingOutputSchema`
2. Add field to `Message` interface in `src/app/types/chat.ts`
3. Map field in `use-chat.ts` where stream lines are assembled into `Message`
4. Render conditionally in `assistant-message.tsx`

## Streaming (NDJSON)

- API routes stream one JSON object per line (`\n`-delimited, not `\n\n` SSE)
- `type: "response"` for agent output, `type: "error"` for failures
- Frontend accumulates bytes in a string buffer, splits on `\n`, parses each non-empty line
- Never buffer the full response — emit and parse incrementally as chunks arrive
- See `src/app/types/use-chat.ts` for the canonical streaming loop

## MCP Backend client

- All MCP calls go through `mcpRequest<T>()` in `src/lib/mcp-client.ts`
- Use `include` param for sideloading: `include: "invoice.lines,invoice.contact"`
- Don't introduce a second HTTP client — extend `mcpRequest` options if needed
- Auth (Bearer token) is injected automatically from env or per-request override header

## iframe + postMessage

- Navigate within the parent: `navigateParent(route, id?, documentType?)` from `src/lib/navigation.ts`
- Receive context (theme, parentUrl): listen via `window.addEventListener("message", ...)` in `page.tsx`
- Never use `window.location.href` — all cross-frame navigation is postMessage

## Common pitfalls

| Symptom | Likely cause |
|---|---|
| Agent stops emitting a field | Zod rejected the value — check raw NDJSON stream for the actual output |
| Dark mode classes not applying | Theme class on wrong element — must be on `<html>` |
| `formRef.current` is null | Ref not attached yet — null-check before calling imperative methods |
| Stream parsing drops lines | Splitting on `\n\n` instead of `\n`, or not flushing the tail buffer |
| Tool silently fails | `execute()` threw but wasn't caught — ADK swallows tool errors by default; log inside execute |
