import { useRef, useEffect, useMemo, useState, type KeyboardEvent } from "react";
import "./chat/chat.css";
import type { ChatMessage } from "../hooks/useChatStream";
import { useDictation, type DictationEnd } from "../hooks/useSpeech";
import { DICTATION_BLOCKED_NOTICE } from "../voice/policy";
import { MicButton } from "./voice/MicButton";
import { staleFor, useCitationStatus, type StaleMap } from "../hooks/useCitationStatus";
import { ChatMarkdown } from "./chat/ChatMarkdown";
import { AnswerRating } from "./feedback/AnswerRating";
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
  /** Whether the mic may be offered on the page beside this panel (see voice/policy.ts). */
  dictationAllowed?: boolean;
}

const joinText = (a: string, b: string) => (a.trim() ? `${a.trimEnd()} ${b}` : b);

export function ChatPanel({
  messages,
  streaming,
  onSend,
  onClearHighlights,
  onOpenPage,
  onStop,
  onClear,
  dictationAllowed = true,
}: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  // Cited pages that changed after their answer, per message id. Rebuilt only when a check
  // returns, so the memoised markdown does not re-render on every token.
  const citationStates = useCitationStatus(messages);
  const staleByMessage = useMemo(() => {
    const byId: Record<string, StaleMap> = {};
    for (const m of messages) {
      const stale = staleFor(m.grounding?.sources, citationStates);
      if (Object.keys(stale).length > 0) byId[m.id] = stale;
    }
    return byId;
    // Sources arrive once, with the grounding event; the states are what change after that.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [citationStates]);

  useEffect(() => {
    // Instant while tokens arrive: smooth scrolling restarts on every token and lags.
    bottomRef.current?.scrollIntoView({ behavior: streaming ? "auto" : "smooth", block: "end" });
  }, [messages, streaming]);

  function send(q: string) {
    setInput("");
    onClearHighlights();
    onSend(q);
  }

  function handleSend() {
    const q = input.trim();
    if (!q || streaming) return;
    send(q);
  }

  // Releasing the mic sends. Anything else that ended it leaves the words in the box to review.
  const dictation = useDictation((heard: string, how: DictationEnd) => {
    const said = joinText(input, heard);
    if (how === "released" && !streaming) send(said);
    else setInput(said);
  });
  const { cancel: cancelDictation } = dictation;
  useEffect(() => {
    if (!dictationAllowed) cancelDictation();
  }, [dictationAllowed, cancelDictation]);

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

  // Minimized, the chat is a header bar and Reading takes the column.
  const [minimized, setMinimized] = useState(false);
  const showStop = streaming && !!onStop;
  const sendDisabled = streaming || !input.trim();

  return (
    <div className={`chat-panel${minimized ? " chat-panel--min" : ""}`}>
      <div className="chat-header">
        <button
          type="button"
          className="chat-min-btn"
          onClick={() => setMinimized((m) => !m)}
          aria-expanded={!minimized}
          title={minimized ? "Show the chat" : "Minimize the chat to read more"}
        >
          <span aria-hidden="true">{minimized ? "▸" : "▾"}</span> Ask the Librarian
        </button>
        <span className="chat-header-meta">
          {!minimized && <span className="chat-hint">ask about the KB</span>}
          {onClear && !minimized && (
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

      {!minimized && (
      <>
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
                    stale={staleByMessage[m.id]}
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
              <GroundingLine
                grounding={m.grounding}
                stale={staleByMessage[m.id]}
                onOpenPage={onOpenPage}
              />
            )}
            {m.role === "assistant" && m.answerId && !m.streaming && !m.error && (
              <AnswerRating answerId={m.answerId} />
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          value={dictation.listening && dictation.transcript ? joinText(input, dictation.transcript) : input}
          readOnly={dictation.listening}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about the wiki…  (Enter to send)"
          aria-label="Ask the librarian"
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
        {dictation.supported && (
          <div className="chat-mic-row">
            {dictationAllowed ? (
              <MicButton dictation={dictation} disabled={streaming} label="Hold to talk, release to send" />
            ) : (
              <span className="voice-notice">{DICTATION_BLOCKED_NOTICE}</span>
            )}
            {dictation.error && <span role="alert" className="voice-error">{dictation.error}</span>}
          </div>
        )}
      </div>
      </>
      )}
    </div>
  );
}
