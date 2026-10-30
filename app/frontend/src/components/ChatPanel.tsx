import { useRef, useEffect, useState, type KeyboardEvent } from "react";
import type { ChatMessage } from "../hooks/useChatStream";
import { ChatMarkdown } from "./chat/ChatMarkdown";
import { GroundingLine } from "./chat/GroundingLine";

interface Props {
  messages: ChatMessage[];
  streaming: boolean;
  onSend: (query: string) => void;
  onClearHighlights: () => void;
  /** Citation chip click. Chips render inert until the host provides this. */
  onOpenPage?: (id: string) => void;
  /** Abort the in-flight reply. The stop button is hidden without it. */
  onStop?: () => void;
  /** Empty the conversation. The clear button is hidden without it. */
  onClear?: () => void;
}

export function ChatPanel({
  messages,
  streaming,
  onSend,
  onClearHighlights,
  onOpenPage,
  onStop,
  onClear,
}: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Instant while tokens arrive: smooth scrolling restarts on every token and lags.
    bottomRef.current?.scrollIntoView({ behavior: streaming ? "auto" : "smooth", block: "end" });
  }, [messages, streaming]);

  function handleSend() {
    const q = input.trim();
    if (!q || streaming) return;
    setInput("");
    onClearHighlights();
    onSend(q);
  }

  function handleKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleClear() {
    onClearHighlights();
    onClear?.();
  }

  const showStop = streaming && !!onStop;
  const sendDisabled = streaming || !input.trim();

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span>Wiki Agent</span>
        <span className="chat-header-meta">
          <span className="chat-hint">ask about the KB</span>
          {onClear && (
            <button
              type="button"
              onClick={handleClear}
              disabled={messages.length === 0}
              aria-label="Clear conversation"
              title="Clear conversation"
              className="chat-clear-btn"
            >
              clear
            </button>
          )}
        </span>
      </div>

      <div className="chat-log" role="log" aria-live="polite" aria-label="Conversation">
        {messages.length === 0 && (
          <div className="chat-empty">
            Ask a question about agent design, RAG, LangGraph, ADK…
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`chat-msg chat-msg--${m.role === "user" ? "user" : "assistant"}`}>
            <div className="chat-msg-role">
              {m.role === "user" ? "you" : "agent"}
            </div>
            {m.role === "user" ? (
              <div className="chat-user-text">{m.content}</div>
            ) : (
              <>
                {m.content && (
                  <ChatMarkdown
                    content={m.content}
                    ungrounded={m.grounding?.ungrounded}
                    onOpenPage={onOpenPage}
                  />
                )}
                {m.streaming && <span className="chat-cursor" aria-hidden="true">▋</span>}
              </>
            )}
            {m.note && (
              <div
                className={`chat-note ${m.stopped ? "chat-note--stopped" : "chat-note--error"}`}
                role={m.stopped ? undefined : "alert"}
              >
                {m.note}
              </div>
            )}
            {m.grounding && !m.streaming && (
              <GroundingLine grounding={m.grounding} onOpenPage={onOpenPage} />
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about the wiki…  (Enter to send)"
          aria-label="Ask the wiki agent"
          disabled={streaming}
          className="chat-textarea"
          rows={2}
        />
        {showStop ? (
          <button
            type="button"
            onClick={onStop}
            aria-label="Stop generating"
            title="Stop generating"
            className="chat-send-btn chat-send-btn--stop"
          >
            ■
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSend}
            disabled={sendDisabled}
            aria-label={streaming ? "Waiting for reply" : "Send"}
            title="Send"
            className="chat-send-btn"
          >
            {streaming ? "…" : "→"}
          </button>
        )}
      </div>
    </div>
  );
}
