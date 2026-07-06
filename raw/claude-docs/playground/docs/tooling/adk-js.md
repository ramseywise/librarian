# Google ADK JS (`@google/adk` 0.5.0)

Research on the TypeScript/JavaScript ADK SDK as used in `ts_google_adk/`.

## Key classes

### `LlmAgent`

The core agent class. Takes a config object:

```ts
import { LlmAgent } from "@google/adk";

const agent = new LlmAgent({
  name: "accounting",
  model: "gemini-2.5-flash",           // model string lives HERE only — never in tools or lib
  description: "...",
  instruction: systemPromptString,
  tools: [tool1, tool2],
  outputSchema: zodSchema,             // Zod schema for structured output
});
```

### `FunctionTool`

The only tool type in use. Defined as singletons at module level in `src/agents/tools/<domain>.ts`:

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
    const raw = await billyRequest(`/v2/things/${id}`);
    return { id: raw.id, name: raw.name };   // only what the agent needs
  },
});
```

Rules:
- `parameters` must be a Zod `z.object()` with `.describe()` on every field — the LLM uses these as documentation
- `execute()` must be async
- Catch and handle errors inside `execute()` — ADK swallows tool errors by default (they won't surface to the stream)
- Return only the fields the agent needs — don't leak the raw API shape

### `GoogleGenAI` client

ADK internally uses `@google/genai`. The project exposes a factory in `src/lib/genai-client.ts` that mirrors the ADK env-var convention:

| Env var | Value | Backend |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | `true` | Vertex AI — also needs `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION` |
| `GOOGLE_GENAI_USE_VERTEXAI` | `false` | Gemini API — needs `GOOGLE_GENAI_API_KEY` |

## Structured output

Pass a Zod schema to `outputSchema` in `LlmAgent`. The ADK serializes it to JSON Schema and instructs the model to emit valid JSON. The streaming API emits the output as an NDJSON line with `type: "response"`.

Rules:
- All fields should be **optional** — required fields break existing sessions that predate the field
- `.describe()` on every field — the LLM treats these as output instructions, not documentation
- If the LLM stops emitting a field: check the raw NDJSON stream — Zod likely rejected the value

## Agent invocation (API route)

The ADK runner is invoked inside a Next.js API route (`src/app/api/chat/route.ts`) which:
1. Resolves the agent from the registry (`src/agents/index.ts`) by `agentId`
2. Runs the agent with the session context
3. Streams NDJSON lines back to the frontend

## Capability checklist

When adding a new capability:
1. Add `FunctionTool` in `src/agents/tools/<domain>.ts`
2. Import and add to the agent's `tools` array in `src/agents/accounting-ts/index.ts`
3. Update the system prompt if the tool requires new instructions
4. Add optional field to `accountingOutputSchema` if the response needs a new UI element
5. Follow the UI element checklist in the `nextjs` skill

## Pitfalls

| Symptom | Cause |
|---|---|
| Tool silently fails | `execute()` threw — ADK swallows tool errors; log inside execute |
| Agent stops emitting a schema field | Zod validation failed on the raw output; inspect the stream |
| Model string scattered across files | Must live only in the `LlmAgent` definition |
| Tool parameters missing `.describe()` | LLM will guess — often causes wrong invocations |
