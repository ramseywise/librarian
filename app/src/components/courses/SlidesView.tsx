import { useEffect, useState } from "react";
import type { SlideDeck } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";
import { apiFetch } from "../../utils/api";

/** While a build runs the viewer asks again at this interval. */
const POLL_MS = 3000;

/** A slide image, fetched as a blob: an `<img src>` cannot carry the bearer token. */
function SlideImage({ url, alt }: { url: string; alt: string }) {
  const [src, setSrc] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    let made: string | null = null;
    setSrc(null);
    apiFetch(url)
      .then((r) => (r.ok ? r.blob() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((blob) => {
        if (cancelled) return;
        made = URL.createObjectURL(blob);
        setSrc(made);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
      if (made) URL.revokeObjectURL(made);
    };
  }, [url]);
  return src ? <img src={src} alt={alt} className="slide-image" /> : <div className="slide-image slide-image--loading" />;
}

/** One deck of slides: `#/slides/<module>[/<lecture>]`. Arrow keys, Home and End move; `n` toggles the
 * speaker notes. The slide's text is always in the page (for search, screen readers and machines with no
 * renderer), shown beside the image or alone when there is none. */
export function SlidesView({ deckId }: { deckId: string }) {
  const [deck, setDeck] = useState<SlideDeck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pos, setPos] = useState(0);
  const [notes, setNotes] = useState(false);
  const [tick, setTick] = useState(0);
  useDocumentTitle(pageTitle(deck?.title ?? "Loading…", "Slides"));

  useEffect(() => {
    setPos(0);
  }, [deckId]);

  useEffect(() => {
    let cancelled = false;
    // GET only reads. A stale deck says so, and we ask for the build once per tick.
    const load = (url: string, init?: RequestInit): Promise<SlideDeck> =>
      apiFetch(url, init).then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status === 404 ? "No slides here" : `HTTP ${r.status}`))));
    load(`/api/courses/slides/${deckId}`)
      // A deployment serves prebuilt decks and has no build route (404): keep what GET answered.
      .then((d) => (d.stale ? load(`/api/courses/slides/${deckId}/build`, { method: "POST" }).catch(() => d) : d))
      .then((d: SlideDeck) => {
        if (cancelled) return;
        setDeck(d);
        setError(null);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [deckId, tick]);

  const building = deck?.status === "building";
  useEffect(() => {
    if (!building) return;
    const id = window.setTimeout(() => setTick((t) => t + 1), POLL_MS);
    return () => window.clearTimeout(id);
  }, [building, tick]);

  const count = deck?.slides.length ?? 0;
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (e.metaKey || e.ctrlKey || e.altKey || t?.closest("input, textarea, select")) return;
      if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") setPos((p) => Math.min(p + 1, count - 1));
      else if (e.key === "ArrowLeft" || e.key === "PageUp") setPos((p) => Math.max(p - 1, 0));
      else if (e.key === "Home") setPos(0);
      else if (e.key === "End") setPos(Math.max(count - 1, 0));
      else if (e.key === "n" || e.key === "N") setNotes((v) => !v);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [count]);

  if (error && !deck) return <div className="course-centered"><div>{error}</div></div>;
  if (!deck) return <div className="course-centered"><div>Loading…</div></div>;

  const slide = deck.slides[Math.min(pos, count - 1)];
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--slides">
        <a href={`#/courses/${deck.course}`} className="link-btn">← Course</a>
        <h1 className="course-page-title course-page-title--overview">{deck.title}</h1>
        {deck.decks.length > 1 && (
          <nav className="slides-decks" aria-label="Decks in this module">
            {deck.decks.map((d) => (
              <a key={d.id} href={`#/slides/${d.id}`} aria-current={d.id === deck.id ? "page" : undefined}>{d.title}</a>
            ))}
          </nav>
        )}
        {deck.status === "building" && <p className="slides-status" role="status">Rendering slide images… showing the text for now.</p>}
        {deck.status === "text" && (
          <p className="slides-status" role="status">
            Slide images are not available here{deck.needs.length ? ` (needs ${deck.needs.join(", ")})` : ""}. Showing the text.
          </p>
        )}
        {deck.status === "failed" && (
          <p className="slides-status" role="alert">
            The slide build failed{deck.error ? `: ${deck.error}` : ""}. Showing the text.
          </p>
        )}
        {!slide ? (
          <p className="flashcard-done">This deck has no slides.</p>
        ) : (
          <>
            <section className="slide-stage" aria-label={`Slide ${slide.n} of ${count}`} aria-live="polite">
              {slide.image && <SlideImage url={slide.image} alt={slide.title || `Slide ${slide.n}`} />}
              <div className={slide.image ? "slide-text sr-only" : "slide-text"} data-testid="slide-text">
                <h2 className="slide-title">{slide.title}</h2>
                <pre className="slide-body">{slide.text}</pre>
              </div>
            </section>
            <div className="flashcard-controls">
              <button onClick={() => setPos(Math.max(pos - 1, 0))} disabled={pos === 0} className="round-btn">Previous</button>
              <button onClick={() => setPos(Math.min(pos + 1, count - 1))} disabled={pos >= count - 1} className="btn-primary">Next</button>
              <button onClick={() => setNotes((v) => !v)} aria-pressed={notes} className="round-btn">Notes</button>
              <span className="flashcard-count">{slide.n} of {count}</span>
            </div>
            {notes && (
              <aside className="slide-notes" aria-label="Speaker notes">
                {slide.notes || <em>No notes for this slide.</em>}
              </aside>
            )}
          </>
        )}
      </div>
    </div>
  );
}
