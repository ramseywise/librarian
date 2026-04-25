"""Tests for App configuration including context compaction."""

from playground.agent_poc.agents.billy_assistant.app import app
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
