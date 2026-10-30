import { useState, useCallback, useEffect, useRef, lazy, Suspense } from "react";
import { WikiGraph } from "./components/WikiGraph";
import { ChatPanel } from "./components/ChatPanel";
import { NodeDetailPanel } from "./components/NodeDetailPanel";
import { pageTitle, useDocumentTitle } from "./components/courses/useDocumentTitle";
import { useChatStream } from "./hooks/useChatStream";
import { useHashRoute } from "./hooks/useHashRoute";
import type { SelectedNode } from "./types";
import "./theme/tokens.css";
import "./theme/components.css";

/** Below this width the chat panel overlays the main area instead of sitting beside it.
 *  Keep in sync with the 1099px media queries in theme/components.css. */
const NARROW_QUERY = "(max-width: 1099px)";
const isNarrow = () =>
  typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia(NARROW_QUERY).matches;

// Courses and Practice pull in react-markdown + KaTeX; load them only when opened.
const CoursesView = lazy(() =>
  import("./components/courses/CoursesView").then((m) => ({ default: m.CoursesView }))
);
const PracticeView = lazy(() =>
  import("./components/courses/PracticeView").then((m) => ({ default: m.PracticeView }))
);

export default function App() {
  const [highlightedPages, setHighlightedPages] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [activeTags, setActiveTags] = useState<Set<string>>(new Set());
  // Open beside the graph on wide screens; on narrow ones it would cover the page on load.
  const [chatOpen, setChatOpen] = useState(() => !isNarrow());
  const chatToggleRef = useRef<HTMLButtonElement>(null);
  const [focusPage, setFocusPage] = useState<string | null>(null);
  const lastQueryRef = useRef("");
  const [route, navigate] = useHashRoute();
  const inPractice = route === "/practice";
  const inCourses = route === "/courses" || route.startsWith("/courses/") || inPractice;
  const courseRoute = route.replace(/^\/courses\/?/, "");
  // Course views set their own titles; the graph's is set here.
  useDocumentTitle(inCourses ? null : pageTitle("Graph"));

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

  const { messages, streaming, sendQuery, stop, clear } = useChatStream(handleHighlight);

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

  // WikiGraph has fitted to the page and opened its panel; drop the request so a later
  // visit to the graph doesn't re-centre on it.
  const clearFocus = useCallback(() => setFocusPage(null), []);

  const openLesson = useCallback((lessonId: string) => navigate(`/courses/${lessonId}`), [navigate]);

  const askAbout = useCallback(
    (question: string) => {
      setChatOpen(true);
      handleSend(question);
    },
    [handleSend]
  );

  // Escape closes the chat while it is an overlay (narrow screens); beside the graph it
  // is a persistent column and Escape leaves it alone. Listens on window, not document:
  // the window bubble phase runs after every document listener whatever their mount
  // order, so an inner popup (lessons drawer, graph menu) that handled the key with
  // preventDefault() is always seen here and one Escape closes one thing.
  useEffect(() => {
    if (!chatOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || e.defaultPrevented || !isNarrow()) return;
      setChatOpen(false);
      chatToggleRef.current?.focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [chatOpen]);

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-brand">Librarian</span>
        <nav className="app-nav">
          <button onClick={() => navigate("/")} className="tab" aria-current={!inCourses ? "page" : undefined}>
            Graph
          </button>
          <button
            onClick={() => navigate("/courses")}
            className="tab"
            aria-current={inCourses && !inPractice ? "page" : undefined}
          >
            Courses
          </button>
          <button onClick={() => navigate("/practice")} className="tab" aria-current={inPractice ? "page" : undefined}>
            Practice
          </button>
        </nav>
        <div className="app-header-actions">
          {!inCourses && highlightedPages.size > 0 && (
            <button onClick={clearHighlights} className="pill-btn pill-btn--accent">
              ✕ {highlightedPages.size} highlighted
            </button>
          )}
          <button
            ref={chatToggleRef}
            onClick={() => setChatOpen((o) => !o)}
            className="pill-btn"
            aria-expanded={chatOpen}
            aria-controls="chat-panel"
          >
            {chatOpen ? "Hide Chat" : "Agent Chat ↗"}
          </button>
        </div>
      </header>

      <div className="app-body">
        <div className="app-main">
          {inCourses && (
            <div className="app-course-layer">
              <Suspense fallback={<div className="app-loading">Loading…</div>}>
                {inPractice ? (
                  <PracticeView onOpenLesson={openLesson} onOpenConcept={openConcept} />
                ) : (
                  <CoursesView route={courseRoute} navigate={navigate} onOpenConcept={openConcept} onAsk={askAbout} />
                )}
              </Suspense>
            </div>
          )}

          {/* Graph panel — stays mounted (and sized, so React Flow can measure) under courses. */}
          <div className="app-graph-layer" style={{ visibility: inCourses ? "hidden" : "visible" }}>
            <WikiGraph
              highlightedPages={highlightedPages}
              onNodeSelect={setSelectedNode}
              onBrief={handleBrief}
              activeTags={activeTags}
              onActiveTagsChange={setActiveTags}
              focusPage={inCourses ? null : focusPage}
              onFocusApplied={clearFocus}
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

        {/* Chat panel: a column beside the main area, or an overlay on narrow screens. */}
        {chatOpen && (
          <div id="chat-panel" className="app-chat">
            <ChatPanel
              messages={messages}
              streaming={streaming}
              onSend={handleSend}
              onClearHighlights={clearHighlights}
              onOpenPage={openConcept}
              onStop={stop}
              onClear={clear}
            />
          </div>
        )}
      </div>
    </div>
  );
}
