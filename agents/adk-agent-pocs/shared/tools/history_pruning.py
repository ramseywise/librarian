from __future__ import annotations

from google.adk.agents.callback_context import CallbackContext
from google.adk.events.event import Event
from google.adk.flows.llm_flows.contents import (
    _add_instructions_to_user_content,
    _get_contents,
    _get_current_turn_contents,
)
from google.adk.flows.llm_flows.instructions import _build_instructions
from google.adk.models.llm_request import LlmRequest


def prune_historic_tool_response_events(
    events: list[Event],
    *,
    current_invocation_id: str,
    tool_names: set[str],
) -> list[Event]:
    """Return a view of events with prior-invocation tool payloads cleared.

    The current invocation must retain full tool payloads so the model can use
    them for same-turn synthesis. Older invocations can be safely slimmed down
    for future turns.
    """
    pruned_events: list[Event] = []

    for event in events:
        if event.invocation_id == current_invocation_id:
            pruned_events.append(event)
            continue

        if not (event.content and event.content.parts):
            pruned_events.append(event)
            continue

        event_copy: Event | None = None
        for index, part in enumerate(event.content.parts):
            if (
                part.function_response is None
                or part.function_response.name not in tool_names
            ):
                continue

            if event_copy is None:
                event_copy = event.model_copy(deep=True)

            event_copy.content.parts[index].function_response.response = {}

        pruned_events.append(event_copy or event)

    return pruned_events


def make_history_prune_callback(tool_names: list[str]):
    """Build a before_model_callback that redacts stale tool-response payloads.

    Current-turn tool results stay intact so the model can synthesize an
    answer. Older invocations are rebuilt with targeted function responses
    cleared, which keeps future prompts lean without mutating session storage.
    """
    tool_name_set = set(tool_names)

    async def _prune(
        callback_context: CallbackContext,
        llm_request: LlmRequest,
    ) -> None:
        invocation_context = callback_context._invocation_context

        pruned_events = prune_historic_tool_response_events(
            callback_context.session.events,
            current_invocation_id=callback_context.invocation_id,
            tool_names=tool_name_set,
        )

        if invocation_context.agent.include_contents == "default":
            llm_request.contents = _get_contents(
                invocation_context.branch,
                pruned_events,
                invocation_context.agent.name,
            )
        else:
            llm_request.contents = _get_current_turn_contents(
                invocation_context.branch,
                pruned_events,
                invocation_context.agent.name,
            )

        instruction_request = LlmRequest()
        await _build_instructions(invocation_context, instruction_request)
        await _add_instructions_to_user_content(
            invocation_context,
            llm_request,
            instruction_request.contents,
        )

    return _prune
