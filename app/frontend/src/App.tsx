import { useState, useCallback, useRef } from "react";
import { WikiGraph } from "./components/WikiGraph";
import { ChatPanel } from "./components/ChatPanel";
import { NodeDetailPanel } from "./components/NodeDetailPanel";
import { CoursesView } from "./components/courses/CoursesView";
import { useChatStream } from "./hooks/useChatStream";
import { useHashRoute } from "./hooks/useHashRoute";
import type { SelectedNode } from "./types";

export default function App() {
  const [highlightedPages, setHighlightedPages] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [activeTags, setActiveTags] = useState<Set<string>>(new Set());
  const [chatOpen, setChatOpen] = useState(true);
  const [focusPage, setFocusPage] = useState<string | null>(null);
  const lastQueryRef = useRef("");
  const [route, navigate] = useHashRoute();
  const inCourses = route === "/courses" || route.startsWith("/courses/");
  const courseRoute = route.replace(/^\/courses\/?/, "");

  const handleTagClick = useCallback((tag: string) => {
    setActiveTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag); else next.add(tag);
      return next;
    });
  }, []);

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

  const handleBrief = useCallback(
    (domain: string) => {
      setChatOpen(true);
      handleSend(`get_domain_briefing("${domain}")`);
    },
    [handleSend]
  );

  // Course → graph: highlight the concept, centre it, switch to the graph.
  const openConcept = useCallback(
    (pageId: string) => {
      setHighlightedPages(new Set([pageId]));
      setFocusPage(pageId);
      navigate("/");
    },
    [navigate]
  );

  const openLesson = useCallback((lessonId: string) => navigate(`/courses/${lessonId}`), [navigate]);

  const askAbout = useCallback(
    (question: string) => {
      setChatOpen(true);
      handleSend(question);
    },
    [handleSend]
  );

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={headerStyle}>
        <span style={{ color: "#e0e0e0", fontWeight: 600, marginRight: 8 }}>Librarian</span>
        <nav style={{ display: "flex", gap: 4 }}>
          <button onClick={() => navigate("/")} style={tabStyle(!inCourses)}>Graph</button>
          <button onClick={() => navigate("/courses")} style={tabStyle(inCourses)}>Courses</button>
        </nav>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          {!inCourses && highlightedPages.size > 0 && (
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
        <div style={{ flex: 1, overflow: "hidden", position: "relative", minWidth: 0 }}>
          {inCourses && (
            <div style={{ position: "absolute", inset: 0, zIndex: 1, background: "#0f0f0f" }}>
              <CoursesView route={courseRoute} navigate={navigate} onOpenConcept={openConcept} onAsk={askAbout} />
            </div>
          )}

          {/* Graph panel — stays mounted (and sized, so React Flow can measure) under courses. */}
          <div style={{ position: "absolute", inset: 0, overflow: "hidden", visibility: inCourses ? "hidden" : "visible" }}>
            <WikiGraph
              highlightedPages={highlightedPages}
              onNodeSelect={setSelectedNode}
              onBrief={handleBrief}
              activeTags={activeTags}
              onActiveTagsChange={setActiveTags}
              focusPage={inCourses ? null : focusPage}
            />
            {selectedNode && (
              <NodeDetailPanel
                nodeId={selectedNode.id}
                data={selectedNode.data}
                highlighted={highlightedPages.has(selectedNode.id)}
                lastQuery={lastQueryRef.current}
                onClose={() => setSelectedNode(null)}
                onTagClick={handleTagClick}
                activeTags={activeTags}
                onOpenLesson={openLesson}
              />
            )}
          </div>
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

const tabStyle = (active: boolean): React.CSSProperties => ({
  background: active ? "#1f1f1f" : "transparent",
  border: "1px solid",
  borderColor: active ? "#333" : "transparent",
  borderRadius: 6,
  color: active ? "#e0e0e0" : "#777",
  fontSize: 12,
  padding: "3px 12px",
  cursor: "pointer",
  fontFamily: "inherit",
});

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
