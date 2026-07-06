# Next.js 16 App Router

Research on Next.js 16 App Router patterns as used in `ts_google_adk/`.

## App Router fundamentals

All routing is file-system based under `src/app/`. Key files:

| File | Role |
|---|---|
| `src/app/layout.tsx` | Root layout — wraps all pages. Never `"use client"`. Handles theme class on `<html>`. |
| `src/app/page.tsx` | Root page — thin composition root. Imports hooks, composes components, no complex render logic. |
| `src/app/globals.css` | Tailwind imports only — no custom CSS here. |
| `src/middleware.ts` | Runs before every request — sets theme cookie, injects locale. |

## Server vs Client components

The App Router defaults to **Server Components**. Rules for this project:

- `"use client"` goes **only at the leaf** that uses browser APIs, event handlers, or hooks
- Never put `"use client"` on `layout.tsx` — it disables SSR for the entire subtree (the `ts_quality.sh` hook blocks this)
- API routes (`src/app/api/`) are always server-side — never import client-only code there

## State and hooks

State lives in hook slices, not in `page.tsx`. One hook per concern:

| Hook | Concern |
|---|---|
| `useChat` | Message send/receive, NDJSON streaming loop, confirm/discard |
| `useSessions` | Session CRUD, history list |
| `useBootstrap` | Locale, theme, iframe init via postMessage |

Rules:
- No prop drilling past 2 levels — add a hook slice instead
- `page.tsx` only composes hooks and passes props — no business logic

## Forms with `forwardRef`

Forms that need to be pre-filled imperatively (e.g. from a table row click) use `forwardRef` to expose an imperative handle:

```tsx
const MyForm = forwardRef<MyFormHandle, Props>((props, ref) => {
  useImperativeHandle(ref, () => ({
    prefill: (data) => { /* ... */ },
  }));
  return <form>...</form>;
});
```

Guard all `ref.current` calls — the ref may not be attached yet:
```ts
formRef.current?.prefill(data);   // ✅ null-check
formRef.current.prefill(data);    // ✗ will throw on first render
```

## NDJSON streaming (API routes)

The chat API route streams one JSON object per line (`\n`-delimited, **not** SSE `\n\n`). Pattern:

```ts
// API route
const stream = new TransformStream();
const writer = stream.writable.getWriter();
// ...
await writer.write(encoder.encode(JSON.stringify({ type: "response", ...data }) + "\n"));
```

Frontend streaming loop (canonical — see `src/app/types/use-chat.ts`):

```ts
const reader = res.body?.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");
  buffer = lines.pop() ?? "";       // keep incomplete tail

  for (const line of lines) {
    if (!line.trim()) continue;
    const data = JSON.parse(line);
    // handle data.type === "response" | "error"
  }
}
```

Pitfalls:
- Splitting on `\n\n` instead of `\n` drops lines
- Not preserving the tail buffer (`lines.pop()`) drops the last partial line
- Never buffer the full response — emit and parse incrementally

## Tailwind CSS 4

- Utility classes only — no inline styles, no CSS modules
- Dark mode uses `dark:` prefix; theme class (`dark`) is set on `<html>` by middleware, not `<body>`
- Spacing uses the Tailwind scale — no magic pixel values

## TypeScript config (`tsconfig.json`)

Key settings in this project:

```json
{
  "strict": true,           // all strict flags on — trust the compiler
  "noEmit": true,           // type-check only, bundler handles emit
  "incremental": true,      // .tsbuildinfo cache for faster re-checks
  "moduleResolution": "bundler",
  "paths": { "@/*": ["./src/*"] }
}
```

`skipLibCheck: true` skips checking `.d.ts` files in `node_modules` — necessary because some transitive deps have type errors.

## PostCSS / Tailwind setup

Tailwind 4 uses `@tailwindcss/postcss` as the PostCSS plugin (not `tailwindcss/nesting` etc from v3). No `tailwind.config.js` needed — config lives in `globals.css` via `@import "tailwindcss"`.
