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

  // On narrow screens the chat is a non-modal sheet over the right of the page (no
  // backdrop; the page beside it stays usable), so it takes focus but does not trap it.
  // Escape acts on whatever holds focus, so one press closes one thing:
  // - capture phase: focus inside the chat → close the chat and stop the event, so a
  //   popup elsewhere (graph menu) that happens to be open is left alone;
  // - bubble phase on window (after every document listener, whatever their mount
  //   order): close the chat unless an inner popup (lessons drawer, graph menu) already
  //   handled the key with preventDefault().
  // Beside the graph (wide screens) the chat is a persistent column; Escape leaves it.
  const chatPanelRef = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!chatOpen) return;
    if (isNarrow()) chatPanelRef.current?.querySelector<HTMLElement>("textarea, input")?.focus();
    const close = () => {
      setChatOpen(false);
      chatToggleRef.current?.focus();
    };
    const onCapture = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || !isNarrow()) return;
      if (!chatPanelRef.current?.contains(document.activeElement)) return;
      e.preventDefault();
      e.stopPropagation();
      close();
    };
    const onBubble = (e: KeyboardEvent) => {
      if (e.key !== "Escape" || e.defaultPrevented || !isNarrow()) return;
      close();
    };
    window.addEventListener("keydown", onCapture, true);
    window.addEventListener("keydown", onBubble);
    return () => {
      window.removeEventListener("keydown", onCapture, true);
      window.removeEventListener("keydown", onBubble);
    };
  }, [chatOpen]);

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-brand">Librarian</span>
        <nav className="app-nav" aria-label="Sections">
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
        <main className="app-main">
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
            <h1 className="sr-only">Wiki graph</h1>
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
        </main>

        {/* Chat panel: a column beside the main area, or an overlay on narrow screens. */}
        {chatOpen && (
          <aside id="chat-panel" ref={chatPanelRef} className="app-chat" aria-label="Agent chat">
            <ChatPanel
              messages={messages}
              streaming={streaming}
              onSend={handleSend}
              onClearHighlights={clearHighlights}
              onOpenPage={openConcept}
              onStop={stop}
              onClear={clear}
            />
          </aside>
        )}
      </div>
    </div>
  );
}
