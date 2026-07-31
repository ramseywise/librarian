---
title: ADK JS TypeScript Patterns
tags: [adk, llm, pattern, reference]
summary: Google ADK TypeScript SDK (@google/adk 0.5.0) — LlmAgent, FunctionTool, structured Zod output, streaming NDJSON, and pitfall patterns for Next.js agent integration.
updated: 2026-07-06
sources:
  - raw/claude-docs/playground/docs/tooling/adk-js.md
---

# ADK JS TypeScript Patterns

TypeScript/JavaScript ADK SDK patterns as used in `ts_google_adk/`. Complements the Python ADK patterns documented in [[ADK Context Engineering]].

---

## Key Classes

### `LlmAgent`

The core agent class. Model string lives here only — never in tools or lib:

```ts
import { LlmAgent } from "@google/adk";

const agent = new LlmAgent({
  name: "accounting",
  model: "gemini-2.5-flash",           // model string lives HERE only
  description: "...",
  instruction: systemPromptString,
  tools: [tool1, tool2],
  outputSchema: zodSchema,             // Zod schema for structured output
});
```

### `FunctionTool`

The only tool type in standard use. Defined as singletons at module level in `src/agents/tools/<domain>.ts`:

```ts
import { FunctionTool } from "@google/adk";
import { z } from "zod";

export const myTool = new FunctionTool({
  name: "my_tool",
  description: "What this tool does — the LLM reads this to decide when to call it.",
  parameters: z.object({
    id: z.string().describe("The ID of the thing to look up."),
  }),
  execute: async ({ id }) => {
    // Transform raw API response before returning — agent never sees raw shape
    const raw = await [product]Request(`/v2/things/${id}`);
    return { id: raw.id, name: raw.name };   // only what the agent needs
  },
});
```

**Rules:**
- `parameters` must be a Zod `z.object()` with `.describe()` on every field — the LLM uses these as documentation
- `execute()` must be async
- Catch and handle errors inside `execute()` — ADK swallows tool errors by default (they won't surface to the stream)
- Return only the fields the agent needs — don't leak the raw API shape

### `GoogleGenAI` Client

ADK internally uses `@google/genai`. Factory in `src/lib/genai-client.ts` mirrors ADK env-var convention:

| Env var | Value | Backend |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | `true` | Vertex AI — also needs `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION` |
| `GOOGLE_GENAI_USE_VERTEXAI` | `false` | Gemini API — needs `GOOGLE_GENAI_API_KEY` |

---

## Structured Output

Pass a Zod schema to `outputSchema` in `LlmAgent`. The ADK serializes it to JSON Schema and instructs the model to emit valid JSON. Streaming API emits output as an NDJSON line with `type: "response"`.

**Rules:**
- All fields should be **optional** — required fields break existing sessions that predate the field
- `.describe()` on every field — the LLM treats these as output instructions, not documentation
- If the LLM stops emitting a field: check the raw NDJSON stream — Zod likely rejected the value

---

## Agent Invocation (API Route)

The ADK runner is invoked inside a Next.js API route (`src/app/api/chat/route.ts`) which:
1. Resolves the agent from the registry (`src/agents/index.ts`) by `agentId`
2. Runs the agent with the session context
3. Streams NDJSON lines back to the frontend

---

## Capability Checklist

When adding a new capability:
1. Add `FunctionTool` in `src/agents/tools/<domain>.ts`
2. Import and add to the agent's `tools` array in `src/agents/<agent>/index.ts`
3. Update the system prompt if the tool requires new instructions
4. Add optional field to `outputSchema` if the response needs a new UI element

---

## Pitfalls

| Symptom | Cause |
|---|---|
| Tool silently fails | `execute()` threw — ADK swallows tool errors; log inside execute |
| Agent stops emitting a schema field | Zod validation failed on the raw output; inspect the stream |
| Model string scattered across files | Must live only in the `LlmAgent` definition |
| Tool parameters missing `.describe()` | LLM will guess — often causes wrong invocations |

---

## Relationship to Python ADK

The TypeScript SDK (`@google/adk`) mirrors the Python ADK conceptually but with different API shapes:
- Python: `Agent(name=..., instruction=..., tools=[...])` → TS: `new LlmAgent({name, instruction, tools})`
- Python: `FunctionTool` is a decorator or class — TS: `new FunctionTool({name, parameters, execute})`
- Both: Gemini models, same Vertex AI / Gemini API backend switching
- Both: Structured output via schema (Python: Pydantic, TS: Zod)

See [[ADK vs LangGraph Comparison]] for framework-level trade-offs.

---

## See Also
- [[ADK vs LangGraph Comparison]]
- [[ADK Context Engineering]]
- [[VA Agent Project]]
- [[Multi-Modal Agent Response]]
