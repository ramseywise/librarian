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
    <div style={panelStyle}>
      <div style={headerStyle}>
        <span>Wiki Agent</span>
        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 10, color: "#555", fontWeight: 400 }}>ask about the KB</span>
          {onClear && (
            <button
              type="button"
              onClick={handleClear}
              disabled={messages.length === 0}
              aria-label="Clear conversation"
              title="Clear conversation"
              style={{
                ...clearBtnStyle,
                opacity: messages.length === 0 ? 0.35 : 1,
                cursor: messages.length === 0 ? "default" : "pointer",
              }}
            >
              clear
            </button>
          )}
        </span>
      </div>

      <div style={messagesStyle} role="log" aria-live="polite" aria-label="Conversation">
        {messages.length === 0 && (
          <div style={{ color: "#444", fontSize: 12, padding: "16px 0", textAlign: "center" }}>
            Ask a question about agent design, RAG, LangGraph, ADK…
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} style={m.role === "user" ? userMsgStyle : assistantMsgStyle}>
            <div style={{ fontSize: 10, color: "#555", marginBottom: 4 }}>
              {m.role === "user" ? "you" : "agent"}
            </div>
            {m.role === "user" ? (
              <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{m.content}</div>
            ) : (
              <>
                {m.content && (
                  <ChatMarkdown
                    content={m.content}
                    ungrounded={m.grounding?.ungrounded}
                    onOpenPage={onOpenPage}
                  />
                )}
                {m.streaming && <span style={{ color: "#555" }} aria-hidden="true">▋</span>}
              </>
            )}
            {m.note && (
              <div
                style={m.stopped ? stoppedNoteStyle : errorNoteStyle}
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

      <div style={inputAreaStyle}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about the wiki…  (Enter to send)"
          aria-label="Ask the wiki agent"
          disabled={streaming}
          style={textareaStyle}
          rows={2}
        />
        {showStop ? (
          <button
            type="button"
            onClick={onStop}
            aria-label="Stop generating"
            title="Stop generating"
            style={{ ...sendBtnStyle, ...stopBtnStyle, cursor: "pointer" }}
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
            style={{
              ...sendBtnStyle,
              opacity: sendDisabled ? 0.4 : 1,
              cursor: sendDisabled ? "default" : "pointer",
            }}
          >
            {streaming ? "…" : "→"}
          </button>
        )}
      </div>
    </div>
  );
}

const noteBase: React.CSSProperties = { marginTop: 6, fontSize: 10, fontStyle: "italic" };
const stoppedNoteStyle: React.CSSProperties = { ...noteBase, color: "#666" };
const errorNoteStyle: React.CSSProperties = { ...noteBase, color: "#d0756a" };

const clearBtnStyle: React.CSSProperties = {
  background: "none",
  border: "1px solid #333",
  borderRadius: 4,
  color: "#999",
  fontSize: 10,
  padding: "1px 6px",
  fontWeight: 400,
};

const stopBtnStyle: React.CSSProperties = {
  background: "#5a2a2a",
  fontSize: 12,
};

const panelStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  height: "100%",
  background: "#111",
  fontSize: 13,
  color: "#d0d0d0",
};

const headerStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderBottom: "1px solid #222",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  fontWeight: 600,
  color: "#e0e0e0",
  flexShrink: 0,
};

const messagesStyle: React.CSSProperties = {
  flex: 1,
  overflowY: "auto",
  padding: "12px",
  display: "flex",
  flexDirection: "column",
  gap: 12,
};

const userMsgStyle: React.CSSProperties = {
  background: "#1a1a2e",
  border: "1px solid #2a2a4a",
  borderRadius: 8,
  padding: "8px 12px",
  alignSelf: "flex-end",
  maxWidth: "85%",
  fontSize: 12,
};

const assistantMsgStyle: React.CSSProperties = {
  background: "#1a1a1a",
  border: "1px solid #2a2a2a",
  borderRadius: 8,
  padding: "8px 12px",
  alignSelf: "flex-start",
  maxWidth: "95%",
  fontSize: 12,
};

const inputAreaStyle: React.CSSProperties = {
  padding: "10px",
  borderTop: "1px solid #222",
  display: "flex",
  gap: 8,
  flexShrink: 0,
};

const textareaStyle: React.CSSProperties = {
  flex: 1,
  background: "#1a1a1a",
  border: "1px solid #333",
  borderRadius: 6,
  color: "#d0d0d0",
  padding: "6px 10px",
  fontSize: 12,
  resize: "none",
  fontFamily: "inherit",
  outline: "none",
};

const sendBtnStyle: React.CSSProperties = {
  background: "#2a5298",
  border: "none",
  borderRadius: 6,
  color: "#e0e0e0",
  padding: "6px 16px",
  fontSize: 16,
  alignSelf: "flex-end",
};
