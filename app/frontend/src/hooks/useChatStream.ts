import { useState, useCallback } from "react";

export interface Grounding {
  cited: string[];
  pagesRead: string[];
  ungrounded: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming: boolean;
  error?: boolean;
  grounding?: Grounding;
}

interface HistoryTurn {
  role: "user" | "assistant";
  content: string;
}

// Prior turns sent with each query. Only completed user→assistant pairs go out: an
// errored or empty reply drops its pair, so the transcript alternates and ends on
// "assistant" — the shape POST /api/chat/stream validates. The backend trims to its
// own turn/char bounds, so no cap is applied here.
function toHistory(messages: ChatMessage[]): HistoryTurn[] {
  const turns: HistoryTurn[] = [];
  for (let i = 0; i + 1 < messages.length; i++) {
    const u = messages[i];
    const a = messages[i + 1];
    if (u.role !== "user" || a.role !== "assistant") continue;
    if (a.error || a.streaming || !a.content.trim() || !u.content.trim()) continue;
    turns.push({ role: "user", content: u.content }, { role: "assistant", content: a.content });
    i++;
  }
  return turns;
}

export function useChatStream(onHighlight: (pages: string[]) => void) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);

  const sendQuery = useCallback(
    async (query: string) => {
      if (streaming) return;

      const userMsg: ChatMessage = {
        id: `u-${Date.now()}`,
        role: "user",
        content: query,
        streaming: false,
      };
      const assistantId = `a-${Date.now()}`;
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        streaming: true,
      };

      const history = toHistory(messages);
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setStreaming(true);

      try {
        const resp = await fetch("/api/chat/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, history }),
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        if (!resp.body) throw new Error("No response body");

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let receivedDone = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6)) as Record<string, unknown>;
              if (event.type === "token") {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: m.content + (event.content as string) }
                      : m
                  )
                );
              } else if (event.type === "grounding") {
                const grounding: Grounding = {
                  cited: event.cited as string[],
                  pagesRead: event.pages_read as string[],
                  ungrounded: event.ungrounded as string[],
                };
                setMessages((prev) =>
                  prev.map((m) => (m.id === assistantId ? { ...m, grounding } : m))
                );
              } else if (event.type === "highlight") {
                onHighlight(event.pages as string[]);
              } else if (event.type === "done") {
                receivedDone = true;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...m, streaming: false } : m
                  )
                );
                setStreaming(false);
              }
            } catch {
              // ignore malformed SSE lines
            }
          }
        }
        // Only clean up if the backend closed the stream without sending a done event
        if (!receivedDone) {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, streaming: false } : m))
          );
          setStreaming(false);
        }
      } catch (err) {
        console.error("chat stream error:", err);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: "[Error: could not reach API]", streaming: false, error: true }
              : m
          )
        );
        setStreaming(false);
      }
    },
    [streaming, onHighlight, messages]
  );

  return { messages, streaming, sendQuery };
}
