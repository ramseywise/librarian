import { useState, useCallback, useEffect, useRef } from "react";

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
  /** Reply did not complete (failed, stopped, or cut off); excluded from history. */
  error?: boolean;
  /** The user pressed stop; `note` is not an error in that case. */
  stopped?: boolean;
  /** Status line shown under the reply: why it is incomplete. Kept out of `content`. */
  note?: string;
  grounding?: Grounding;
}

interface HistoryTurn {
  role: "user" | "assistant";
  content: string;
}

// Prior turns sent with each query. Only completed user→assistant pairs go out: an
// errored, stopped or empty reply drops its pair, so the transcript alternates and ends
// on "assistant" — the shape POST /api/chat/stream validates. The backend trims to its
// own turn/char bounds, so no cap is applied here.
export function toHistory(messages: ChatMessage[]): HistoryTurn[] {
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

/**
 * Incremental SSE parser for the `data: <json>` frames the backend emits. Handles
 * frames split across chunks, CRLF line endings, `data:` without the space, and a final
 * line without a trailing newline (call `end()` when the stream closes).
 */
export function createSseParser(onEvent: (event: Record<string, unknown>) => void) {
  let buffer = "";

  function handleLine(raw: string) {
    const line = raw.endsWith("\r") ? raw.slice(0, -1) : raw;
    if (!line.startsWith("data:")) return;
    const payload = line.slice(line.startsWith("data: ") ? 6 : 5);
    let event: unknown;
    try {
      event = JSON.parse(payload);
    } catch {
      return; // malformed frame
    }
    if (event && typeof event === "object") onEvent(event as Record<string, unknown>);
  }

  return {
    push(chunk: string) {
      buffer += chunk;
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      lines.forEach(handleLine);
    },
    end() {
      if (buffer) handleLine(buffer);
      buffer = "";
    },
  };
}

/** User-facing message for a non-OK HTTP response, from the FastAPI `detail` if any. */
export function describeHttpError(status: number, body: unknown): string {
  if (status >= 500) return `Server error (HTTP ${status})`;
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    // 422: a list of pydantic errors; show the first.
    const first = detail[0] as { msg?: unknown; loc?: unknown };
    if (typeof first?.msg === "string") {
      const loc = Array.isArray(first.loc) ? first.loc.filter((p) => p !== "body").join(".") : "";
      return loc ? `${first.msg} (${loc})` : first.msg;
    }
  }
  return `Request failed (HTTP ${status})`;
}

export const NETWORK_ERROR = "Could not reach the API";
export const EARLY_CLOSE = "The response ended early";
export const STOPPED = "stopped";

class HttpError extends Error {}

export function useChatStream(onHighlight: (pages: string[]) => void) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);

  // Read through refs so sendQuery/stop/clear keep one identity for the hook's life
  // instead of changing on every token (which re-rendered App and every handleSend user).
  const messagesRef = useRef(messages);
  const streamingRef = useRef(false);
  const onHighlightRef = useRef(onHighlight);
  const controllerRef = useRef<AbortController | null>(null);
  // Bumped per request and by clear(): a finished or aborted request only touches state
  // while it is still the current one.
  const requestRef = useRef(0);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);
  useEffect(() => {
    onHighlightRef.current = onHighlight;
  }, [onHighlight]);

  const sendQuery = useCallback(async (query: string) => {
    if (streamingRef.current) return;
    streamingRef.current = true;
    const requestId = ++requestRef.current;
    const controller = new AbortController();
    controllerRef.current = controller;

    const now = Date.now();
    const userMsg: ChatMessage = { id: `u-${now}-${requestId}`, role: "user", content: query, streaming: false };
    const assistantId = `a-${now}-${requestId}`;
    const assistantMsg: ChatMessage = { id: assistantId, role: "assistant", content: "", streaming: true };

    const history = toHistory(messagesRef.current);
    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setStreaming(true);

    const patch = (fn: (m: ChatMessage) => ChatMessage) =>
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? fn(m) : m)));

    const finish = (fn: (m: ChatMessage) => ChatMessage) => {
      patch((m) => ({ ...fn(m), streaming: false }));
      if (requestRef.current === requestId) {
        streamingRef.current = false;
        controllerRef.current = null;
        setStreaming(false);
      }
    };

    let receivedDone = false;
    let responded = false;
    try {
      const resp = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, history }),
        signal: controller.signal,
      });
      responded = true;

      if (!resp.ok) {
        const body: unknown = await resp.json().catch(() => null);
        throw new HttpError(describeHttpError(resp.status, body));
      }
      if (!resp.body) throw new HttpError(EARLY_CLOSE);

      const parser = createSseParser((event) => {
        if (event.type === "token" && typeof event.content === "string") {
          const text = event.content;
          patch((m) => ({ ...m, content: m.content + text }));
        } else if (event.type === "grounding") {
          const grounding: Grounding = {
            cited: (event.cited as string[]) ?? [],
            pagesRead: (event.pages_read as string[]) ?? [],
            ungrounded: (event.ungrounded as string[]) ?? [],
          };
          patch((m) => ({ ...m, grounding }));
        } else if (event.type === "highlight") {
          onHighlightRef.current((event.pages as string[]) ?? []);
        } else if (event.type === "done") {
          receivedDone = true;
        }
      });

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        parser.push(decoder.decode(value, { stream: true }));
      }
      parser.push(decoder.decode());
      parser.end();

      if (receivedDone) finish((m) => m);
      else finish((m) => ({ ...m, error: true, note: EARLY_CLOSE }));
    } catch (err) {
      // Partial content is kept in every case; only the status note differs.
      if (controller.signal.aborted) {
        finish((m) => ({ ...m, error: true, stopped: true, note: STOPPED }));
      } else if (err instanceof HttpError) {
        finish((m) => ({ ...m, error: true, note: err.message }));
      } else {
        console.error("chat stream error:", err);
        // A throw before any response is a failure to reach the API; one after it
        // (connection dropped mid-stream) is an early close.
        finish((m) => ({ ...m, error: true, note: responded ? EARLY_CLOSE : NETWORK_ERROR }));
      }
    }
  }, []);

  const stop = useCallback(() => {
    controllerRef.current?.abort();
  }, []);

  const clear = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    requestRef.current++;
    streamingRef.current = false;
    setStreaming(false);
    setMessages([]);
  }, []);

  return { messages, streaming, sendQuery, stop, clear };
}
