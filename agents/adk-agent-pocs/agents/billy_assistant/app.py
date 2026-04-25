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

# aws sso login --sso-session admin
