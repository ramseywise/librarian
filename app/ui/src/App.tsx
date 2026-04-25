import { useState, useCallback, useRef } from "react";
import { WikiGraph } from "./components/WikiGraph";
import { ChatPanel } from "./components/ChatPanel";
import { NodeDetailPanel } from "./components/NodeDetailPanel";
import { useChatStream } from "./hooks/useChatStream";
import type { SelectedNode } from "./types";

export default function App() {
  const [highlightedPages, setHighlightedPages] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [chatOpen, setChatOpen] = useState(true);
  const lastQueryRef = useRef("");

  const handleHighlight = useCallback((pages: string[]) => {
    setHighlightedPages(new Set(pages));
  }, []);

  const clearHighlights = useCallback(() => {
    setHighlightedPages(new Set());
  }, []);

  const { messages, streaming, sendQuery } = useChatStream(handleHighlight);

  const handleSend = useCallback(
    (query: string) => {
      lastQueryRef.current = query;
      sendQuery(query);
    },
    [sendQuery]
  );

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={headerStyle}>
        <span style={{ color: "#e0e0e0", fontWeight: 600, marginRight: 8 }}>Librarian</span>
        <span>Wiki Graph Explorer</span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          {highlightedPages.size > 0 && (
            <button onClick={clearHighlights} style={clearBtnStyle}>
              ✕ {highlightedPages.size} highlighted
            </button>
          )}
          <button onClick={() => setChatOpen((o) => !o)} style={toggleBtnStyle}>
            {chatOpen ? "Hide Chat" : "Agent Chat ↗"}
          </button>
        </div>
      </header>

      <div style={{ flex: 1, overflow: "hidden", display: "flex" }}>
        {/* Graph panel */}
        <div style={{ flex: 1, overflow: "hidden", position: "relative" }}>
          <WikiGraph
            highlightedPages={highlightedPages}
            onNodeSelect={setSelectedNode}
          />
          {selectedNode && (
            <NodeDetailPanel
              nodeId={selectedNode.id}
              data={selectedNode.data}
              highlighted={highlightedPages.has(selectedNode.id)}
              lastQuery={lastQueryRef.current}
              onClose={() => setSelectedNode(null)}
            />
          )}
        </div>

        {/* Chat panel */}
        {chatOpen && (
          <div style={{ width: 360, borderLeft: "1px solid #222", flexShrink: 0, overflow: "hidden" }}>
            <ChatPanel
              messages={messages}
              streaming={streaming}
              onSend={handleSend}
              onClearHighlights={clearHighlights}
            />
          </div>
        )}
      </div>
    </div>
  );
}

const headerStyle: React.CSSProperties = {
  height: 40,
  background: "#111",
  borderBottom: "1px solid #222",
  display: "flex",
  alignItems: "center",
  padding: "0 16px",
  fontSize: 13,
  color: "#888",
  flexShrink: 0,
};

const clearBtnStyle: React.CSSProperties = {
  background: "#2196F322",
  border: "1px solid #2196F3",
  borderRadius: 12,
  color: "#2196F3",
  fontSize: 11,
  padding: "3px 10px",
  cursor: "pointer",
};

const toggleBtnStyle: React.CSSProperties = {
  background: "transparent",
  border: "1px solid #333",
  borderRadius: 12,
  color: "#888",
  fontSize: 11,
  padding: "3px 10px",
  cursor: "pointer",
};
