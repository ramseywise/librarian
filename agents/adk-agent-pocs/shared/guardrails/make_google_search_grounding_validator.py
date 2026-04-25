from __future__ import annotations

import logging
from typing import Callable, Iterable, Optional
from urllib.parse import urlparse

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse

logger = logging.getLogger(__name__)


def _get_attr(obj, *names, default=None):
    """Try multiple attribute names (snake_case vs camelCase)."""
    for n in names:
        if obj is None:
            return default
        if hasattr(obj, n):
            v = getattr(obj, n)
            if v is not None:
                return v
    return default


def _hostname(url: str) -> str:
    try:
        host = (urlparse(url).hostname or "").lower()
        return host
    except Exception:
        return ""


def make_google_search_grounding_validator(
    *,
    untrusted_domains: Iterable[str],
    state_flag_key: str = "untrusted_source_flag",
    state_urls_key: str = "untrusted_source_urls",
) -> Callable[[CallbackContext, LlmResponse], Optional[LlmResponse]]:
    """
    Factory that returns an after_model_callback which:
      - runs only when Google Search grounding appears to be used
      - flags/captures any sources from untrusted domains
    """
    untrusted = {d.lower().lstrip(".") for d in untrusted_domains}

    def after_model_callback(
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> Optional[LlmResponse]:
        gm = _get_attr(llm_response, "grounding_metadata", "groundingMetadata")
        if not gm:
            return llm_response

        # If searchEntryPoint exists, this is very likely Google Search grounding.  [oai_citation:0‡GitHub](https://raw.githubusercontent.com/google/adk-docs/main/docs/grounding/google_search_grounding.md)
        search_entry_point = _get_attr(gm, "search_entry_point", "searchEntryPoint")
        if not search_entry_point:
            return llm_response

        chunks = _get_attr(gm, "grounding_chunks", "groundingChunks", default=[]) or []
        bad_urls: list[str] = []

        for chunk in chunks:
            web = _get_attr(chunk, "web", default=None)
            uri = _get_attr(web, "uri", "URI", default="") if web else ""
            url = (uri or "").strip()
            host = _hostname(url)

            if not host:
                continue

            # match exact domain or subdomain of an untrusted domain
            if any(host == d or host.endswith("." + d) for d in untrusted):
                bad_urls.append(url)

        if bad_urls:
            logger.warning(
                "Untrusted grounding sources detected for agent=%s: %s",
                callback_context.agent_name,
                bad_urls,
            )
            callback_context.state[state_flag_key] = True
            # keep a list for debugging / UI display
            callback_context.state[state_urls_key] = sorted(set(bad_urls))

        return llm_response

    return after_model_callback


"""
from google.adk.agents import Agent
from google.adk.tools import google_search

_UNTRUSTED_DOMAINS = {
    "pinterest.com",
    "quora.com",
    "medium.com",   # up to you
    "reddit.com",   # up to you
}

grounding_guard = make_google_search_grounding_validator(
    untrusted_domains=_UNTRUSTED_DOMAINS,
)

search_grounded_agent = Agent(
    name="web_search_expert",
    model="gemini-2.5-flash",
    instruction="Use Google Search when needed. Always cite sources.",
    tools=[google_search],
    after_model_callback=grounding_guard,  # ✅ only this agent gets the callback
)
"""
