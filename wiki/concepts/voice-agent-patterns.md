---
title: Voice Agent Patterns
tags: [voice, adk, langgraph, context-management, pattern]
summary: Patterns for real-time voice agents — hard latency constraints, BIDI streaming session management, ADK Strategy C preloading, LangGraph flat tool node, and mandatory history pruning.
updated: 2026-04-25
sources:
  - raw/agent-skills/voice-agents/SKILL.md
---

# Voice Agent Patterns

## Hard Real-Time Constraints

Voice agents operate under constraints that don't apply to text agents:

- **Latency budget:** first audio token must arrive in <400ms or the user perceives lag
- **Interruption handling:** VAD (voice activity detection) can interrupt mid-generation — agents must be interruptible at any point
- **No multi-step tool chains:** a `load_skill → domain_tool` two-hop chain is not viable during live audio — all tools must be single-turn callable
- **Compaction is mandatory:** accumulated tool history causes context overflow in long sessions (see [[Summarization Node]])

## ADK: Use Strategy C (All-Preloaded)

For voice agents using ADK, do NOT use Strategy A (proxy/dynamic loading). Load everything at session start:

```python
# Strategy C — all tools and instructions loaded at session start
agent = LlmAgent(
    model="gemini-2.0-flash-live",
    static_instruction=Path("prompts/system.txt").read_text(),
    tools=[*preloaded_toolset, *voice_tools],
)
```

Dynamic loading requires tool calls to read SKILL.md files — that two-hop overhead is unacceptable under a 400ms latency budget.

See [[ADK Context Engineering]] for the full three-strategy comparison.

## LangGraph: Flat Tool Node, No Lazy Loading

All tool schemas must be bound at graph compile time. No dynamic expansion:

```python
graph = StateGraph(VoiceState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(all_tools))  # all tools bound at compile, no lazy loading
```

Add history pruning as a `before_node` callback to truncate tool history before each LLM call — keep only user messages, agent text, and the current turn's tool calls.

## Multimodal RAG (Audio Input)

Audio queries need a separate embedding path:

1. Audio → transcript (Whisper or Gemini transcription) → text embedding pipeline
2. OR: audio → audio embedding directly (if model supports it)

Reranking must handle mixed modality — text chunks vs. audio-derived chunks.

## Session State Management

Voice sessions accumulate state faster than text. Key patterns:
- Summarise every 8 turns (Haiku — cost-effective); keep 4-turn overlap (see [[Summarization Node]])
- Prune tool call history before each LLM call — prior tool results are context bloat
- Warm up the agent cache before the session opens to avoid cold-start latency (see [[Embedder Warmup]], [[Prefix Caching]])

## See Also
- [[ADK Context Engineering]]
- [[Summarization Node]]
- [[Prefix Caching]]
- [[Embedder Warmup]]
- [[LangGraph Advanced Patterns]]
