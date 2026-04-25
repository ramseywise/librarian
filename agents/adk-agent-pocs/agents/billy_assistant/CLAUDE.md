# Billy Accounting Assistant — Developer Guide

Read [SPEC.md](SPEC.md) first. It is the source of truth for agent design,
instruction text, tool mapping, and data model.

## Structure

```text
agent.py                        # root agent (billy_assistant)
sub_agents/                     # one file per domain expert
sub_agents/shared_tools.py      # report_out_of_domain() — included in every subagent
tools/                          # pure tool functions (no ADK dependency)
tests/                          # pytest tests for tools only
```

## Key Rules

**Put stable policy in `static_instruction`.** All agents in this system use it.
Use:

```python
Agent(
    model="gemini-3-flash-preview",
    static_instruction=types.Content(
        role="user", parts=[types.Part(text=INSTRUCTION_TEXT)]
    ),
    tools=[...],
)
```

When dynamic content is needed, add `instruction=` alongside `static_instruction`.
Two forms are supported:

- **Template string** — placeholders resolved from `session.state` before the model call:

  ```python
  instruction="Current user: {user_name}, language: {lang}"
  ```

- **Callable** — receives `ReadonlyContext`, returns a string:

  ```python
  def provide_instruction(ctx: ReadonlyContext) -> str:
      lang = ctx._invocation_context.session.state.get("lang", "en")
      return f"Reply in {lang}."
  ```

In both cases `static_instruction` holds stable policy and `instruction`
provides the dynamic tail (sent as a `user` content turn, not system instruction).

**One subagent per tool file.** The domain mapping is 1:1 — do not merge
subagents or give a subagent tools from another domain.

**Tools have no ADK dependency.** Keep `tools/` as plain Python functions.
Do not import from `google.adk` in tool files.

## Running Tests

Tests cover tool functions only — run from the repo root:

```bash
uv run pytest agents/billy_assistant/tests/
```

Each test resets all mock state via the `autouse` fixture in `conftest.py`,
so test order does not matter.

## Running Evals

```bash
# All suites
make -C agents/billy_assistant eval

# Individual suites
make -C agents/billy_assistant eval-routing
make -C agents/billy_assistant eval-response
make -C agents/billy_assistant eval-behavior
make -C agents/billy_assistant eval-error

# Single case (use eval_id from the evalset)
make -C agents/billy_assistant eval-routing CASES=my_case_id
make -C agents/billy_assistant eval-routing CASES=case1,case2
```

### Development loop

Always run targeted cases first — do NOT run the full suite until they pass:

**Step 1 — run only the directly affected or newly added cases:**

```bash
make -C agents/billy_assistant eval-routing CASES=my_new_case
```

**Step 2 — only after targeted cases pass, run the full suite:**

```bash
make -C agents/billy_assistant test   # unit tests
make -C agents/billy_assistant eval   # all eval suites
```

### When to run which eval

| Change made | Eval targets to run |
| --- | --- |
| Any `prompts/*.txt` change | `eval-routing` + `eval-response` + `eval-behavior` |
| Cases added to `routing_evalset.json` | `eval-routing` |
| Cases added to `response_evalset.json` | `eval-response` |
| Cases added to `behavior_evalset.json` | `eval-behavior` |
| Cases added to `error_evalset.json` | `eval-error` |

### Adding new eval cases

See `eval/README.md` for the evalset entry schema and step-by-step instructions.
After adding a case, update the table in `eval/README.md`.

## Context Caching

`static_instruction` enables implicit prefix caching by Gemini — no extra
config needed for that. Explicit caching (pinning a specific cache entry)
requires `context_cache_config` at the `App` level and is out of scope here.

`static_instruction` does not work with the Live API.
