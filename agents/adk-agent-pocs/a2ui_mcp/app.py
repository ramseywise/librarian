"""ADK App for a2ui_mcp — wraps root_agent with context compaction."""

import pathlib

from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

from .agent import root_agent

_PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"

_summarizer = LlmEventSummarizer(
    llm=Gemini(model="gemini-3-flash-preview"),
    prompt_template=(_PROMPTS_DIR / "summarizer.txt").read_text(encoding="utf-8"),
)

# NOTE: ContextCacheConfig requires the GCP org policy
# constraints/gcp.resourceLocations to allow caching in your project's region.
# If you see a 400 FAILED_PRECONDITION warning, contact your platform team to
# enable it. Once enabled, this will significantly reduce token costs at scale.
app = App(
    name="a2ui_mcp",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=5,
    ),
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=8,
        overlap_size=2,
        summarizer=_summarizer,
    ),
)
