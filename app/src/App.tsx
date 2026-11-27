import { useState, useCallback, useEffect, useMemo, useRef } from "react";
import { WikiGraph } from "./components/WikiGraph";
import { CourseLayer } from "./CourseLayer";
import { AppNav } from "./components/AppNav";
import { ChatPanel } from "./components/ChatPanel";
import { pageTitle, useDocumentTitle } from "./components/courses/useDocumentTitle";
import { useChatStream, type ChatContext, type LabChatContext, type StudyChatContext } from "./hooks/useChatStream";
import { parseRoute, type CoursePage } from "./routes";
import { dictationAllowed } from "./voice/policy";
import { useHashRoute } from "./hooks/useHashRoute";
import { useSlashSearch } from "./hooks/useSlashSearch";
import { ThemeToggle } from "./components/ThemeToggle";
import { UserMenu } from "./components/account/UserMenu";
import { useAuthConfig, useMe } from "./hooks/useAuth";
import type { SelectedNode } from "./types";
import { tagFacet } from "./utils/curriculum";

/** Below this width the chat panel overlays the main area instead of sitting beside it.
 *  Keep in sync with the 1099px media queries in theme/ui.css. */
const NARROW_QUERY = "(max-width: 1099px)";
const isNarrow = () =>
  typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia(NARROW_QUERY).matches;

function useNarrow(): boolean {
  const [narrow, setNarrow] = useState(isNarrow);
  useEffect(() => {
    const mq = typeof window.matchMedia === "function" ? window.matchMedia(NARROW_QUERY) : null;
    const onChange = () => setNarrow(isNarrow());
    mq?.addEventListener?.("change", onChange);
    return () => mq?.removeEventListener?.("change", onChange);
  }, []);
  return narrow;
}

const NAV_HIDDEN_KEY = "librarian:nav-hidden";
// Storage can be blocked (private window); the sidebar then just starts open.
function readFlag(key: string): boolean {
  try {
    return localStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}
function writeFlag(key: string, on: boolean) {
  try {
    localStorage.setItem(key, on ? "1" : "0");
  } catch {
    // Not remembered.
  }
}

/** The chat sits beside whatever is open, so the page decides whether it may offer a mic. */
function pageAllowsDictation(page: CoursePage | null): boolean {
  if (page?.page === "courses") return dictationAllowed(page.path);
  if (page?.page === "flashcards" || page?.page === "slides") return dictationAllowed(page.deckId);
  return true;
}

export default function App() {
  const [highlightedPages, setHighlightedPages] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [activeTags, setActiveTags] = useState<Set<string>>(new Set());
  // Open beside the graph on wide screens; on narrow ones it would cover the page on load.
  const [chatOpen, setChatOpen] = useState(() => !isNarrow());
  const chatToggleRef = useRef<HTMLButtonElement>(null);
  // The slot in the right column that the map's bar is drawn in. Wide screens keep the column
  // with the chat hidden (the filters fill it); narrow ones drop it, and the bar goes back on the map.
  const [mapDock, setMapDock] = useState<HTMLElement | null>(null);
  const narrow = useNarrow();
  // The column stacks Browse & filter, Reading and the chat; the first two fold to a header row.
  const [filtersOpen, setFiltersOpen] = useState(false);
  // The slot the selected page (or the atlas's sector or spike) is read in.
  const [readingDock, setReadingDock] = useState<HTMLElement | null>(null);
  const [readingOpen, setReadingOpen] = useState(true);
  // Narrow screens: the navigation is a drawer behind the Menu button. Wide ones: a sidebar the
  // same button slides away, which is remembered.
  const [navOpen, setNavOpen] = useState(false);
  const [navHidden, setNavHidden] = useState(() => readFlag(NAV_HIDDEN_KEY));
  const toggleNav = () => {
    if (isNarrow()) return setNavOpen((o) => !o);
    setNavHidden((h) => {
      writeFlag(NAV_HIDDEN_KEY, !h);
      return !h;
    });
  };
  const navToggleRef = useRef<HTMLButtonElement>(null);
  // Picking a page opens the Reading section, so the click always shows something.
  const selectedId = selectedNode?.id ?? null;
  useEffect(() => {
    if (selectedId) setReadingOpen(true);
  }, [selectedId]);
  const mainRef = useRef<HTMLElement>(null);
  const [focusPage, setFocusPage] = useState<string | null>(null);
  const lastQueryRef = useRef("");
  const [route, navigate] = useHashRoute();
  useSlashSearch();
  const authConfig = useAuthConfig();
  const me = useMe();
  const page = parseRoute(route);
  const inLogin = page?.page === "login";
  // Every page drawn over the graph; the graph stays mounted underneath.
  const inCourses = page !== null;
  // Course views set their own titles; the graph's is set here.
  useDocumentTitle(inCourses ? null : pageTitle("Graph"));

  // A tag on a page's open card is the same filter as its chip in the map sidebar.
  const handleTagClick = useCallback((tag: string) => {
    const id = tagFacet(tag);
    setActiveTags((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }, []);
  const activePageTags = useMemo(
    () => new Set([...activeTags].filter((t) => t.startsWith("tag:")).map((t) => t.slice("tag:".length))),
    [activeTags],
  );

  const handleHighlight = useCallback((pages: string[]) => {
    setHighlightedPages(new Set(pages));
  }, []);

  const clearHighlights = useCallback(() => {
    setHighlightedPages(new Set());
  }, []);

  const { messages, streaming, sendQuery, stop, clear } = useChatStream(handleHighlight);

  // An open lab, card or quiz question registers what the chat is told about it; every send
  // carries it while it is open.
  const chatContextRef = useRef<(() => ChatContext) | null>(null);
  const setLabContext = useCallback((get: (() => LabChatContext) | null) => {
    chatContextRef.current = get && (() => ({ lab: get() }));
  }, []);
  const setStudyContext = useCallback((get: (() => StudyChatContext | null) | null) => {
    chatContextRef.current = get && (() => {
      const study = get();
      return study ? { study } : {};
    });
  }, []);

  const handleSend = useCallback(
    (query: string) => {
      lastQueryRef.current = query;
      void sendQuery(query, chatContextRef.current?.() ?? null);
    },
    [sendQuery]
  );

  const handleBrief = useCallback(
    (domain: string) => {
      setChatOpen(true);
      handleSend(`Brief me on "${domain}".`);
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
  const openLab = useCallback((id: string) => navigate(`/labs/${id}`), [navigate]);

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
  //   order): close the chat unless an inner popup (navigation drawer, graph menu) already
  //   handled the key with preventDefault().
  // Beside the graph (wide screens) the chat is a persistent column; Escape leaves it.
  const chatPanelRef = useRef<HTMLElement>(null);

  // Picking a page from the navigation drawer closes it.
  useEffect(() => setNavOpen(false), [route]);
  useEffect(() => {
    if (!navOpen) return;
    document.querySelector<HTMLElement>("#app-sidenav a[href]")?.focus();
    // The drawer is modal (backdrop): keep Tab and screen readers out of the page behind it. Widening
    // past the drawer breakpoint turns it back into a sidebar, so close it then.
    const main = mainRef.current;
    if (main) main.inert = true;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      e.preventDefault();
      setNavOpen(false);
      navToggleRef.current?.focus();
    };
    document.addEventListener("keydown", onKey);
    const wide = window.matchMedia?.("(min-width: 1100px)");
    const onWide = () => wide?.matches && setNavOpen(false);
    wide?.addEventListener("change", onWide);
    return () => {
      document.removeEventListener("keydown", onKey);
      if (main) main.inert = false;
      wide?.removeEventListener("change", onWide);
    };
  }, [navOpen]);
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
        {!inLogin && (
          <button
            ref={navToggleRef}
            type="button"
            className="pill-btn app-menu-btn"
            aria-expanded={isNarrow() ? navOpen : !navHidden}
            aria-controls="app-sidenav"
            aria-label={(isNarrow() ? navOpen : !navHidden) ? "Hide navigation" : "Show navigation"}
            title={(isNarrow() ? navOpen : !navHidden) ? "Hide navigation" : "Show navigation"}
            onClick={toggleNav}
          >
            {/* A sidebar: a panel down the left of a window. */}
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
              strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="16" rx="2" />
              <line x1="9" y1="4" x2="9" y2="20" />
            </svg>
          </button>
        )}
        <span className="app-brand">Librarian</span>
        <div className="app-header-actions">
          <ThemeToggle />
          <UserMenu me={me} config={authConfig} />
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
        {!inLogin && <AppNav id="app-sidenav" route={route} open={navOpen} hidden={navHidden} />}
        {navOpen && <div className="app-sidenav-backdrop" aria-hidden="true" onClick={() => setNavOpen(false)} />}
        <main className="app-main" ref={mainRef}>
          {page && (
            <CourseLayer
              page={page}
              route={route}
              navigate={navigate}
              openLesson={openLesson}
              openLab={openLab}
              openConcept={openConcept}
              askAbout={askAbout}
              setLabContext={setLabContext}
              setStudyContext={setStudyContext}
            />
          )}

          {/* Graph panel — stays mounted (and sized, so React Flow can measure) under courses. */}
          <div className="app-graph-layer" style={{ visibility: inCourses ? "hidden" : "visible" }}>
            <h1 className="sr-only">Wiki graph</h1>
            <WikiGraph
              highlightedPages={highlightedPages}
              onNodeSelect={setSelectedNode}
              selectedId={selectedNode?.id ?? null}
              lastQuery={lastQueryRef.current}
              onTagClick={handleTagClick}
              activePageTags={activePageTags}
              onOpenLesson={openLesson}
              onBrief={handleBrief}
              activeTags={activeTags}
              onActiveTagsChange={setActiveTags}
              focusPage={inCourses ? null : focusPage}
              onFocusApplied={clearFocus}
              dock={mapDock}
              reading={readingDock}
            />
          </div>
        </main>

        {/* Right column, top to bottom: Browse & filter, Reading, then the chat pinned at the
            bottom so its input never moves. Wide screens keep the column with the chat hidden;
            narrow ones show it only with the chat, as an overlay. */}
        {(chatOpen || (!narrow && !inCourses && !inLogin)) && (
          <aside
            id="chat-panel"
            ref={chatPanelRef}
            className={chatOpen ? "app-chat" : "app-chat app-chat--filters"}
            aria-label={chatOpen ? "Agent chat" : "Map filters"}
          >
            {!inCourses && (
              <>
                <button
                  type="button"
                  className="app-map-dock-toggle"
                  aria-expanded={filtersOpen}
                  aria-controls="app-map-dock"
                  onClick={() => setFiltersOpen((o) => !o)}
                >
                  <span>Browse &amp; filter</span>
                  {activeTags.size > 0 && <span className="app-map-dock-count">{activeTags.size} active</span>}
                  <span className="app-map-dock-chevron" aria-hidden="true">{filtersOpen ? "▾" : "▸"}</span>
                </button>
                <div id="app-map-dock" ref={setMapDock} className="app-map-dock" hidden={!filtersOpen} />
                <button
                  type="button"
                  className="app-map-dock-toggle"
                  aria-expanded={readingOpen}
                  aria-controls="app-reading"
                  onClick={() => setReadingOpen((o) => !o)}
                >
                  <span>Reading</span>
                  {selectedNode && <span className="app-map-dock-count app-reading-name">{selectedNode.data.title}</span>}
                  <span className="app-map-dock-chevron" aria-hidden="true">{readingOpen ? "▾" : "▸"}</span>
                </button>
                <section
                  id="app-reading"
                  ref={setReadingDock}
                  className="app-reading"
                  aria-label="Reading"
                  hidden={!readingOpen}
                />
              </>
            )}
            {chatOpen && (
              <ChatPanel
                messages={messages}
                streaming={streaming}
                onSend={handleSend}
                onClearHighlights={clearHighlights}
                onOpenPage={openConcept}
                onStop={stop}
                onClear={clear}
                dictationAllowed={pageAllowsDictation(page)}
              />
            )}
          </aside>
        )}
      </div>
    </div>
  );
}
