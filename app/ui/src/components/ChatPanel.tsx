import { useRef, useEffect, useState, type KeyboardEvent } from "react";
import type { ChatMessage } from "../hooks/useChatStream";

interface Props {
  messages: ChatMessage[];
  streaming: boolean;
  onSend: (query: string) => void;
  onClearHighlights: () => void;
}

export function ChatPanel({ messages, streaming, onSend, onClearHighlights }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <span>Wiki Agent</span>
        <span style={{ fontSize: 10, color: "#555" }}>ask about the KB</span>
      </div>

      <div style={messagesStyle}>
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
            <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>
              {m.content}
              {m.streaming && <span style={{ color: "#555" }}>▋</span>}
            </div>
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
          disabled={streaming}
          style={textareaStyle}
          rows={2}
        />
        <button
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          style={{
            ...sendBtnStyle,
            opacity: streaming || !input.trim() ? 0.4 : 1,
            cursor: streaming || !input.trim() ? "default" : "pointer",
          }}
        >
          {streaming ? "…" : "→"}
        </button>
      </div>
    </div>
  );
}

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
