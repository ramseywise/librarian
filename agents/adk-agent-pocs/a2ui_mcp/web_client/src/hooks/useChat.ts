import { useCallback, useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { createEventSource, postChat } from "../api/agent";
import type { AgentTiming, ChatMessage, SSEEvent, ToolRow } from "../types";

export function useChat(
  sessionId: string,
  agentName: string,
  onA2UIMessages: (messages: unknown[]) => void
) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);

  // Accumulate streaming text per request_id until "done"
  const pendingText = useRef<Map<string, string>>(new Map());
  // Accumulate tool rows per request_id
  const pendingRows = useRef<Map<string, ToolRow[]>>(new Map());
  const esRef = useRef<EventSource | null>(null);

  // Open SSE stream once on mount (or when sessionId/agentName changes)
  useEffect(() => {
    const es = createEventSource(sessionId, agentName);
    esRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    es.onmessage = (event: MessageEvent<string>) => {
      let data: SSEEvent;
      try {
        data = JSON.parse(event.data) as SSEEvent;
      } catch {
        return;
      }

      if (data.type === "connected") {
        setConnected(true);
        return;
      }

      if (data.type === "tool_calls") {
        const rows = pendingRows.current.get(data.request_id) ?? [];
        const newRow: ToolRow = { step: data.step, kind: "calls", items: data.calls };
        const updated = [...rows, newRow];
        pendingRows.current.set(data.request_id, updated);
        setMessages((prev) => upsertAgent(prev, data.request_id, { toolRows: updated }));
        return;
      }

      if (data.type === "tool_results") {
        const rows = pendingRows.current.get(data.request_id) ?? [];
        const newRow: ToolRow = { step: data.step, kind: "results", items: data.results };
        const updated = [...rows, newRow];
        pendingRows.current.set(data.request_id, updated);
        setMessages((prev) => upsertAgent(prev, data.request_id, { toolRows: updated }));
        return;
      }

      if (data.type === "text_chunk") {
        const current = pendingText.current.get(data.request_id) ?? "";
        const newText = current + data.text;
        pendingText.current.set(data.request_id, newText);
        setMessages((prev) => upsertAgent(prev, data.request_id, { text: newText }));
        return;
      }

      if (data.type === "timing") {
        const timing: AgentTiming = {
          total_ms: data.total_ms,
          first_token_ms: data.first_token_ms,
          steps: data.steps,
        };
        setMessages((prev) =>
          prev.map((m) => (m.id === data.request_id ? { ...m, timing } : m))
        );
        return;
      }

      if (data.type === "a2ui") {
        onA2UIMessages(data.messages);
        return;
      }

      if (data.type === "done") {
        pendingText.current.delete(data.request_id);
        pendingRows.current.delete(data.request_id);
        setLoading(false);
        return;
      }

      if (data.type === "error") {
        console.error("Agent error:", data.message);
        setMessages((prev) => [
          ...prev,
          { id: data.request_id, role: "agent", text: `Error: ${data.message}` },
        ]);
        setLoading(false);
      }
    };

    return () => {
      es.close();
      setConnected(false);
    };
  }, [sessionId, agentName, onA2UIMessages]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return;

      const requestId = uuidv4();

      setMessages((prev) => [
        ...prev,
        { id: requestId + "-user", role: "user", text },
      ]);
      setLoading(true);

      try {
        await postChat(sessionId, requestId, text, agentName);
      } catch (err) {
        console.error("POST /chat failed:", err);
        setLoading(false);
      }
    },
    [sessionId, agentName, loading]
  );

  // Send a message silently — no user bubble in the chat thread.
  // Used for the initial dashboard trigger on page load.
  const sendSilentMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      const requestId = uuidv4();
      setLoading(true);
      try {
        await postChat(sessionId, requestId, text, agentName);
      } catch (err) {
        console.error("POST /chat (silent) failed:", err);
        setLoading(false);
      }
    },
    [sessionId, agentName]
  );

  /** Inject a user bubble without calling the LLM. */
  const addUserMessage = useCallback((text: string) => {
    const id = uuidv4();
    setMessages((prev) => [...prev, { id: id + "-user", role: "user", text }]);
  }, []);

  /** Inject an agent bubble without calling the LLM. */
  const addAgentMessage = useCallback((text: string) => {
    const id = uuidv4();
    setMessages((prev) => [...prev, { id, role: "agent", text }]);
  }, []);

  return { messages, loading, connected, sendMessage, sendSilentMessage, addUserMessage, addAgentMessage };
}

/**
 * Create or patch an agent message identified by request_id.
 * Spreads the patch so existing fields (toolRows, timing, etc.) are preserved.
 */
function upsertAgent(
  prev: ChatMessage[],
  requestId: string,
  patch: Partial<ChatMessage>
): ChatMessage[] {
  const idx = prev.findIndex((m) => m.id === requestId && m.role === "agent");
  if (idx >= 0) {
    const updated = [...prev];
    updated[idx] = { ...updated[idx], ...patch };
    return updated;
  }
  return [...prev, { id: requestId, role: "agent", text: "", ...patch }];
}
