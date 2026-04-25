# Spec: Context Compaction

## Problem

Billy sessions can grow long. Each tool call, agent transfer, and model response
is stored as an event in the session. As the event history grows, every request
to the model includes the full transcript — slowing responses and consuming
tokens unnecessarily.

Context compaction solves this by periodically summarizing older events into a
compact representation, discarding the raw transcript while preserving the
essential context the model needs.

## Solution

Wrap `root_agent` in an ADK `App` and configure `EventsCompactionConfig`.

ADK's `Runner` detects the config and triggers compaction automatically in the
background each time the session reaches the configured interval.

**Requires ADK Python v1.16.0 or later.**

---

## New File: `app.py`

Add `agents/billy_assistant/app.py`:

```python
"""ADK App for Billy — wraps root_agent with context compaction."""

from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

from .agent import root_agent

_summarizer = LlmEventSummarizer(llm=Gemini(model="gemini-2.5-flash"))

app = App(
    name="billy_assistant",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
        summarizer=_summarizer,
    ),
)
```

### Configuration rationale

| Parameter | Value | Reason |
| --- | --- | --- |
| `compaction_interval` | `10` | Billy tasks typically resolve in 2–5 tool calls. 10 events gives roughly 2 full exchanges before the first compaction, keeping early context intact. |
| `overlap_size` | `2` | Carries the last 2 events from the previous window into the next compaction, preserving continuity across the boundary. |
| `summarizer` | `gemini-2.5-flash` | Faster and cheaper than the main agent model for summarization; well-suited for condensing accounting tool output. |

### How compaction fires

With `compaction_interval=10` and `overlap_size=2`:

- After event 10: events 1–10 are summarized into a single summary event.
- After event 20: events 9–20 (overlap of 2) are summarized.
- After event 30: events 19–30 are summarized.
- And so on.

---

## Update `__init__.py`

Export `app` alongside `root_agent` so both entry points are available:

```python
from .agent import root_agent
from .app import app

__all__ = ["root_agent", "app"]
```

`root_agent` stays as the primary ADK entry point. `app` is exposed for
runners and tests that need the full App configuration.

---

## Tests

Add `agents/billy_assistant/tests/test_app.py`:

```python
"""Tests for App configuration including context compaction."""

from agents.billy_assistant.app import app
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer


def test_app_name():
    assert app.name == "billy_assistant"


def test_app_root_agent():
    assert app.root_agent.name == "billy_assistant"


def test_compaction_config_present():
    assert app.events_compaction_config is not None


def test_compaction_interval():
    assert app.events_compaction_config.compaction_interval == 10


def test_overlap_size():
    assert app.events_compaction_config.overlap_size == 2


def test_custom_summarizer():
    assert isinstance(app.events_compaction_config.summarizer, LlmEventSummarizer)
```

---

## Implementation Notes

**No changes to existing agent files.** `agent.py`, all subagents, and all
tools remain unchanged. Compaction is a Runner-level concern — agents do not
need to know about it.

**`app.py` uses relative imports** (`.agent`) consistent with the rest of the
package. See the Implementation Notes in SPEC.md for the module-namespace
rationale.

**`root_agent` entry point is preserved.** ADK's web server looks for
`root_agent` in `agent.py`. Adding `app` in a separate file does not break
this. If ADK gains support for an `app` entry point in a future version, the
`__init__.py` export will already be in place.

---

## Out of Scope

- Changing compaction parameters per-agent or per-session.
- Custom summarizer prompt tuning.
- Disabling compaction for specific session types.
