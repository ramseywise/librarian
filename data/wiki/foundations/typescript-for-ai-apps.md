---
title: TypeScript for AI Apps
tags: [foundations, pattern]
summary: "Treat an LLM API as an untyped, slow, occasionally failing remote call: narrow content blocks by `type` (never assume `content[0]` is text), drive the tool loop from an exhaustive `stop_reason` switch, stream long requests, validate tool inputs and structured output with zod, and keep parsing and loop logic pure so it tests offline."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--typescript--notes--09-typescript-for-ai-apps.md
  - data/raw/repos/learn-ai-engineering/programming--typescript--README.md
---

# TypeScript for AI Apps

An LLM API is an untyped, slow and occasionally failing remote call. Everything in the TypeScript
track applies: discriminated unions for content blocks, async for streaming, zod for tool inputs
and structured output. The source uses the Anthropic TypeScript SDK; the shapes below are that
SDK's.

## A request

```ts
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();   // reads ANTHROPIC_API_KEY
const message = await client.messages.create({
  model: 'claude-opus-5-5',
  max_tokens: 16000,
  thinking: { type: 'adaptive' },             // the model decides how much to think
  messages: [{ role: 'user', content: 'Explain structural typing in one paragraph.' }],
});
```

The SDK exports types for everything (`Anthropic.MessageParam`, `Anthropic.Message`,
`Anthropic.Tool`). Use them rather than redefining the shapes.

## Content blocks are a discriminated union

`message.content` is an array of `text`, `thinking`, `tool_use` and other blocks. Narrow by `type`
with a type predicate ([[TypeScript Discriminated Unions and Narrowing]]):

```ts
const text = message.content
  .filter((b): b is Anthropic.TextBlock => b.type === 'text')
  .map((b) => b.text)
  .join('\n');
```

**Never assume `content[0]` is text.** With thinking enabled, the first block often is not.

## `stop_reason` drives the loop

| `stop_reason` | Meaning | Your loop |
|---|---|---|
| `end_turn` | Finished | Done |
| `tool_use` | Wants tools run | Run them; reply with `tool_result` blocks |
| `max_tokens` | Cut off | Raise `max_tokens` or continue. Do not trust a truncated tool call |
| `pause_turn` | A server tool paused a long turn | Send the turn back to continue |
| `refusal` | Declined by a safety classifier | Handle before reading `content` |

Write it as an exhaustive `switch` **with a real `default` branch**: the API adds new values over
time, so a compile-time `never` check alone is not enough at this boundary.

## Tool use

A tool is a name, a description and a JSON Schema for its input. The model returns `tool_use`
blocks, your code runs them, and you reply with `tool_result` blocks carrying the same
`tool_use_id`, repeating until `stop_reason` is `end_turn` (the ReAct shape — [[ReAct Pattern]]).
Tool errors become `is_error` results rather than exceptions that kill the loop.

The SDK's **tool runner** runs that loop, and `betaZodTool` validates each input against a zod
schema before `run` sees it:

```ts
import { betaZodTool } from '@anthropic-ai/sdk/helpers/beta/zod';

const getStock = betaZodTool({
  name: 'get_stock',
  description: 'Units in stock for a product SKU.',
  inputSchema: z.object({ sku: z.string() }),
  run: async ({ sku }) => JSON.stringify(await db.stock(sku)),   // sku already validated
});
const final = await client.beta.messages.toolRunner({ model: 'claude-opus-5-5', max_tokens: 16000, tools: [getStock], messages });
```

**Tool inputs are model output, which makes them untrusted.** Validate them, confine file paths,
and gate anything destructive ([[Runtime Validation with Zod]], [[Tool Definitions as Prompts]]).
Write a manual loop only when you need control the runner does not give.

## Streaming

```ts
const stream = client.messages.stream({ model: 'claude-opus-5-5', max_tokens: 16000, messages });
stream.on('text', (delta) => process.stdout.write(delta));
const final = await stream.finalMessage();   // complete Message, same type as create()
```

Stream any request with long input or output: it shows progress and avoids HTTP timeouts.
`finalMessage()` handles completion, errors and aborts — do not wrap the events in your own
`new Promise`. The underlying shape is async iteration ([[TypeScript Async Patterns]]).

## Structured output

```ts
import { betaZodOutputFormat } from '@anthropic-ai/sdk/helpers/beta/zod';

const res = await client.beta.messages.parse({
  model: 'claude-opus-5-5', max_tokens: 16000, messages,
  output_config: { format: betaZodOutputFormat(Review) },
});
res.parsed_output;   // z.infer<typeof Review> | null
```

The response is constrained to the schema, but still check `parsed_output` for `null` and check for
`stop_reason: 'refusal'` ([[Structured Output]]).

## Errors, retries, refusals

- The SDK retries connection errors, 429s and 5xx itself (`maxRetries`, default 2). Catch the typed
  errors: `Anthropic.RateLimitError`, `Anthropic.APIError` (with `.status`).
- Timeouts are in **milliseconds**: `new Anthropic({ timeout: 60_000 })`. Pass an `AbortSignal` to
  cancel a request.
- **Refusal fallback.** Safety classifiers occasionally decline benign requests. Opting into
  `fallbacks: 'default'` (beta header `server-side-fallback-2026-07-01`) re-runs a declined request
  on the recommended fallback model inside the same call, so a false positive does not become an
  outage.

## Rules of thumb

- Keep prompt-building, block parsing and loop logic as **pure functions** testable without the
  API (the course tests `textOf`, `toolUses`, `runToolCalls` and `nextStep` offline against fake
  responses). Only a thin layer makes network calls.
- Log `usage` (input and output tokens) on every response — cost bugs are invisible otherwise.
- Pin the model ID in one config value, not scattered through the code.

## See Also
- [[Programming Curriculum]] — related (course map)
- [[TypeScript Discriminated Unions and Narrowing]] — prerequisite-for
- [[TypeScript Async Patterns]] — prerequisite-for
- [[Runtime Validation with Zod]] — prerequisite-for
- [[ADK JS TypeScript Patterns]] — alternative-to (the same tool-plus-zod-schema shape in another vendor's TS agent SDK)
- [[ReAct Pattern]] — related (the general loop that stop_reason dispatch implements)
- [[Tool Definitions as Prompts]] — related (tool names and descriptions are prompt text)
- [[Structured Output]] — related (the constrain rung, from the prompting side)
- [[Agent Retry Taxonomy]] — related (which failures to retry beyond the SDK's built-in retries)
