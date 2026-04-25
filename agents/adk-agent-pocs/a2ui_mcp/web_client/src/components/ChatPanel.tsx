import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type {
  AgentTiming,
  ChatMessage,
  TimingStep,
  ToolCallItem,
  ToolResultItem,
  ToolRow,
} from "../types";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  onSend: (text: string) => void;
  suggestions?: string[];
}

// ---------------------------------------------------------------------------
// Tool step rows
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// JSON syntax highlighter (no dependency)
// ---------------------------------------------------------------------------

type Token = { type: "key" | "string" | "number" | "boolean" | "null" | "punct"; text: string };

function tokenizeJson(src: string): Token[] {
  const tokens: Token[] = [];
  // Regex that matches JSON tokens in order of priority
  const full =
    /("(?:[^"\\]|\\.)*")\s*:|(\"(?:[^"\\]|\\.)*\")|(true|false)|(null)|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],:])/g;
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = full.exec(src)) !== null) {
    // Any gap between last match and this one is plain punctuation/whitespace
    if (m.index > last) {
      tokens.push({ type: "punct", text: src.slice(last, m.index) });
    }
    if (m[1] !== undefined) {
      // key: push key string + colon together
      const colonIdx = src.indexOf(":", m.index + m[1].length);
      tokens.push({ type: "key", text: m[1] });
      tokens.push({ type: "punct", text: src.slice(m.index + m[1].length, colonIdx + 1) });
    } else if (m[2] !== undefined) {
      tokens.push({ type: "string", text: m[2] });
    } else if (m[3] !== undefined) {
      tokens.push({ type: "boolean", text: m[3] });
    } else if (m[4] !== undefined) {
      tokens.push({ type: "null", text: m[4] });
    } else if (m[5] !== undefined) {
      tokens.push({ type: "number", text: m[5] });
    } else if (m[6] !== undefined) {
      tokens.push({ type: "punct", text: m[6] });
    }
    last = m.index + m[0].length;
  }
  if (last < src.length) tokens.push({ type: "punct", text: src.slice(last) });
  return tokens;
}

const TOKEN_CLASS: Record<Token["type"], string> = {
  key:     "text-sky-300",
  string:  "text-emerald-300",
  number:  "text-amber-300",
  boolean: "text-violet-300",
  null:    "text-violet-300",
  punct:   "text-slate-400",
};

function JsonHighlight({ value }: { value: unknown }) {
  const src = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  const tokens = tokenizeJson(src);
  return (
    <>
      {tokens.map((t, i) => (
        <span key={i} className={TOKEN_CLASS[t.type]}>
          {t.text}
        </span>
      ))}
    </>
  );
}

// ---------------------------------------------------------------------------
// Tool step rows
// ---------------------------------------------------------------------------

function ToolPill({
  name,
  kind,
  payload,
}: {
  name: string;
  kind: "calls" | "results";
  payload: unknown;
}) {
  const [open, setOpen] = useState(false);
  const isPending = kind === "calls";

  return (
    <div className="relative">
      <button
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium border transition-colors select-none ${
          isPending
            ? "bg-amber-50 border-amber-200 text-amber-800 hover:bg-amber-100"
            : "bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100"
        }`}
      >
        <span className="text-[10px]">{isPending ? "⚡" : "✓"}</span>
        <span>{name}</span>
      </button>

      {/* Hover tooltip — shows args for calls, result for results */}
      {open && payload != null && (
        <div className="absolute left-0 bottom-full mb-1.5 z-50 bg-slate-900 text-[11px] font-mono rounded-lg p-2.5 shadow-2xl max-w-xs w-max max-h-52 overflow-auto whitespace-pre border border-slate-700">
          <JsonHighlight value={payload} />
        </div>
      )}
    </div>
  );
}

function ToolStepRow({ row }: { row: ToolRow }) {
  return (
    <div className="flex items-start gap-2 text-xs pl-1">
      <span className="text-slate-400 font-mono mt-0.5 shrink-0 w-5 text-right">
        #{row.step}
      </span>
      <div className="flex flex-wrap gap-1">
        {row.kind === "calls"
          ? (row.items as ToolCallItem[]).map((c) => (
              <ToolPill key={c.id} name={c.name} kind="calls" payload={c.args} />
            ))
          : (row.items as ToolResultItem[]).map((r) => (
              <ToolPill key={r.id} name={r.name} kind="results" payload={r.result} />
            ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Timing panel
// ---------------------------------------------------------------------------

function formatDuration(ms: number): string {
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${ms}ms`;
}

function TimingBar({ step, totalMs }: { step: TimingStep; totalMs: number }) {
  const left = totalMs > 0 ? (step.start_ms / totalMs) * 100 : 0;
  const width = totalMs > 0 ? Math.max(0.5, (step.duration_ms / totalMs) * 100) : 0;

  return (
    <div className="flex items-center gap-2 text-[11px]">
      <span className="text-slate-500 w-3 text-center shrink-0">
        {step.type === "llm" ? "→" : "⚙"}
      </span>
      <span className="text-slate-400 w-24 truncate text-right shrink-0">
        {step.label}
      </span>
      <div className="flex-1 relative h-3.5 bg-slate-800 rounded overflow-hidden">
        <div
          className={`absolute h-full rounded ${
            step.type === "llm" ? "bg-blue-500" : "bg-slate-500"
          }`}
          style={{ left: `${left}%`, width: `${width}%` }}
        />
      </div>
      <span className="text-slate-400 w-10 text-right shrink-0">
        {formatDuration(step.duration_ms)}
      </span>
    </div>
  );
}

function TimingPanel({ timing }: { timing: AgentTiming }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-1 ml-1">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-600 transition-colors"
      >
        <span>⏱</span>
        <span className="font-medium">{formatDuration(timing.total_ms)}</span>
        {timing.first_token_ms != null && (
          <span className="text-slate-300">
            · First token: {formatDuration(timing.first_token_ms)}
          </span>
        )}
        <span className="text-slate-300 text-[10px]">{expanded ? "▲" : "▼"}</span>
      </button>

      {expanded && (
        <div className="mt-2 bg-slate-900 rounded-xl p-3 max-w-sm border border-slate-700">
          <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2.5">
            <span className="font-medium text-slate-300">Response timing</span>
            {timing.first_token_ms != null && (
              <span className="text-blue-400">
                First token: {formatDuration(timing.first_token_ms)}
              </span>
            )}
            <span className="text-slate-200 font-semibold">
              {formatDuration(timing.total_ms)}
            </span>
          </div>
          <div className="flex flex-col gap-1.5">
            {timing.steps.map((step, i) => (
              <TimingBar key={i} step={step} totalMs={timing.total_ms} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Chat panel
// ---------------------------------------------------------------------------

export function ChatPanel({ messages, loading, onSend, suggestions }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message thread */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && !loading && (
          <div className="mt-6 space-y-4">
            <p className="text-slate-400 text-sm text-center">
              Ask Billy anything about your accounting…
            </p>
            {[
              {
                label: "Insights",
                chips: [
                  "Show revenue overview",
                  "Who owes me money?",
                  "Show top customers",
                  "Monthly revenue 2026",
                  "Which products sell best?",
                ],
              },
              {
                label: "Invoices",
                chips: [
                  "List invoices",
                  "Create an invoice for Acme A/S",
                  "Show invoice dashboard",
                ],
              },
              {
                label: "Customers & Products",
                chips: ["List customers", "List products"],
              },
              {
                label: "Help",
                chips: ["Help"],
              },
            ].map(({ label, chips }) => (
              <div key={label}>
                <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wide mb-1.5 px-1">
                  {label}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {chips.map((chip) => (
                    <button
                      key={chip}
                      onClick={() => onSend(chip)}
                      disabled={loading}
                      className="px-3 py-1.5 text-xs rounded-full border border-slate-200 bg-white text-slate-600 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors shadow-sm disabled:opacity-40"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            {/* Tool step rows — rendered above the agent text bubble */}
            {msg.role === "agent" &&
              msg.toolRows &&
              msg.toolRows.length > 0 && (
                <div className="flex flex-col gap-1 mb-1.5">
                  {msg.toolRows.map((row, i) => (
                    <ToolStepRow key={i} row={row} />
                  ))}
                </div>
              )}

            {/* Text bubble — skip empty agent bubbles that only have tool rows */}
            {(msg.text || msg.role === "user") && (
              <div
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm break-words ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white whitespace-pre-wrap"
                      : "bg-white text-slate-800 border border-slate-200 shadow-sm prose prose-sm prose-slate max-w-none"
                  }`}
                >
                  {msg.role === "user" ? (
                    msg.text || (loading ? "…" : "")
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // Intercept links: http(s) URLs open in new tab; everything
                        // else is treated as a chat query and sent on click.
                        a: ({ href, children }) =>
                          href?.startsWith("http") ? (
                            <a href={href} target="_blank" rel="noopener noreferrer">
                              {children}
                            </a>
                          ) : (
                            <button
                              type="button"
                              onClick={() => onSend(decodeURIComponent(href ?? ""))}
                              className="text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer font-medium bg-transparent border-none p-0 text-left"
                            >
                              {children}
                            </button>
                          ),
                      }}
                    >
                      {msg.text || (loading ? "…" : "")}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            )}

            {/* Timing panel — rendered below the agent text bubble */}
            {msg.role === "agent" && msg.timing && (
              <TimingPanel timing={msg.timing} />
            )}
          </div>
        ))}

        {/* Spinner before first event arrives */}
        {loading && messages.filter((m) => m.role === "agent").length === 0 && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl px-4 py-2 text-sm text-slate-400 shadow-sm">
              …
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Persistent suggestion chips above input */}
      {suggestions && suggestions.length > 0 && (
        <div className="flex flex-wrap gap-1.5 px-3 pt-2 pb-1 border-t border-slate-200 bg-white">
          {suggestions.map((chip) => (
            <button
              key={chip}
              onClick={() => onSend(chip)}
              disabled={loading}
              className="px-3 py-1 text-xs rounded-full border border-slate-200 bg-white text-slate-600 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors shadow-sm disabled:opacity-40"
            >
              {chip}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="flex gap-2 p-3 border-t border-slate-200 bg-white"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message…"
          disabled={loading}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-40 transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}
