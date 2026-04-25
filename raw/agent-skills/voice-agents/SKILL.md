---
name: voice-agents
description: >
  Voice and multimodal agent patterns — BIDI streaming, session state management,
  real-time latency constraints, Gemini Live integration, audio embedding.
  Use when building or modifying any voice-capable agent or live session handler.
metadata:
  domains: [voice, adk, context-management]
---

# Voice Agents

Patterns for building agents that handle real-time audio, bidirectional streaming, and multimodal (voice + text) interaction.

## Core Constraints

Voice agents operate under hard real-time constraints that don't apply to text agents:
- **Latency budget:** first audio token must arrive in <400ms or the user perceives lag
- **Interruption handling:** VAD (voice activity detection) can interrupt mid-generation — agents must be interruptible at any point
- **No multi-step tool chains:** a `load_skill → domain_tool` two-hop chain is not viable during live audio; all tools must be single-turn
- **Compaction:** history pruning is mandatory — accumulated tool history causes context overflow in long sessions

## ADK Skill-Loading Strategy for Voice

Use Strategy C (all-preloaded) for voice agents. Do NOT use Strategy A (proxy/dynamic):

```python
# Strategy C — all tools and instructions loaded at session start
agent = LlmAgent(
    model="gemini-2.0-flash-live",
    static_instruction=Path("prompts/system.txt").read_text(),
    tools=[*preloaded_toolset, *voice_tools],
)
```

See `references/bidi-streaming.md` for the WebSocket session lifecycle.

## LangGraph for Voice

Voice requires pre-loading all tool schemas. Use a flat tool node with no lazy-loading:

```python
# All tools bound at graph compile time
graph = StateGraph(VoiceState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(all_tools))  # no dynamic expansion
```

History pruning is essential — add `before_node` callback to truncate tool history before each LLM call.

## Multimodal RAG

Audio queries require a separate embedding path from text queries:
- Audio → transcript (Whisper or Gemini transcription) → text embedding pipeline
- OR: audio → audio embedding (direct, if model supports it)
- Reranking must handle mixed modality (text chunks vs. audio-derived chunks)

## Session State

Voice sessions accumulate state faster than text sessions. Key patterns:
- Summarise every N turns (8-turn trigger works well; use Haiku for cost)
- Prune tool call history before each LLM call — keep only current turn's tool results
- Warm up the agent cache before the session opens to avoid cold-start latency

## References

| File | Contents |
|------|----------|
| `references/bidi-streaming.md` | WebSocket session lifecycle, PCM format, interruption handling |
| `references/gemini-live.md` | Gemini Live API patterns, audio format specs |

> **References not yet populated.** These will be filled from wiki pages after the first ingest run covering `raw/claude-docs/listen-wiseer/` and voice-related session transcripts.
