import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { SlideFrame } from "./SlideFrame";
import { beatClass } from "./slideBeats";
import type { SlideDeck, SlideFrameData } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import { canSpeak, sentences, useNarration } from "./useNarration";
import "./courses.css";
import "./slides.css";
import { courseColor } from "../../theme/domains";
import { apiFetch } from "../../utils/api";

/** While a build runs the viewer asks again at this interval. */
const POLL_MS = 3000;
const RATES = [1, 1.25, 1.5];

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

/** The frames grouped by part, in order, for the outline under the viewer. The title slide is its own group. */
function outline(frames: SlideFrameData[]): { title: string; frames: SlideFrameData[] }[] {
  const groups: { title: string; frames: SlideFrameData[] }[] = [];
  for (const f of frames) {
    const title = f.kind === "title" ? "Title" : f.part.n === null ? f.part.title : `${f.part.n} ${f.part.title}`;
    const last = groups[groups.length - 1];
    if (last && last.title === title) last.frames.push(f);
    else groups.push({ title, frames: [f] });
  }
  return groups;
}

/** One deck of slides: `#/slides/<module>[/<lecture>][?play=1]`. The slides are drawn in the page from the
 * deck's yaml (`frames`); a deck with no frames falls back to the built images and their text. You page
 * through them yourself: reading aloud (the browser's voice) and the read-along text are both off until
 * asked for. Arrow keys, Home and End move; `k` reads aloud and pauses (Space too, while it reads); `c`
 * read-along text, `n` speaker notes, `f` full screen. */
export function SlidesView({ deckId, onAsk }: { deckId: string; onAsk?: (question: string) => void }) {
  const [id, query = ""] = deckId.split("?");
  const [deck, setDeck] = useState<SlideDeck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pos, setPos] = useState(0);
  const [notes, setNotes] = useState(false);
  const [captions, setCaptions] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [rate, setRate] = useState(1);
  const [tick, setTick] = useState(0);
  const stage = useRef<HTMLElement>(null);
  useDocumentTitle(pageTitle(deck?.title ?? "Loading…", "Slides"));

  useEffect(() => {
    setPos(0);
    setPlaying(new URLSearchParams(query).get("play") === "1" && canSpeak());
  }, [id, query]);

  useEffect(() => {
    let cancelled = false;
    // GET only reads. A stale deck says so, and we ask for the build once per tick.
    const load = (url: string, init?: RequestInit): Promise<SlideDeck> =>
      apiFetch(url, init).then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status === 404 ? "No slides here" : `HTTP ${r.status}`))));
    load(`/api/courses/slides/${id}`)
      // Slides drawn from the yaml need no build. Otherwise a deployment serves prebuilt decks and has no
      // build route (404): keep what GET answered.
      .then((d) => (d.stale && !d.frames?.length ? load(`/api/courses/slides/${id}/build`, { method: "POST" }).catch(() => d) : d))
      .then((d: SlideDeck) => {
        if (cancelled) return;
        setDeck(d);
        setError(null);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [id, tick]);

  const frames = useMemo(() => deck?.frames ?? [], [deck]);
  const drawn = frames.length > 0;
  const building = deck?.status === "building" && !drawn;
  useEffect(() => {
    if (!building) return;
    const timer = window.setTimeout(() => setTick((t) => t + 1), POLL_MS);
    return () => window.clearTimeout(timer);
  }, [building, tick]);

  const count = drawn ? frames.length : (deck?.slides.length ?? 0);
  const at = Math.min(pos, Math.max(count - 1, 0));
  const frame = drawn ? frames[at] : null;
  const speech = canSpeak();

  // The player moves on when a slide has been read, and stops after the last one.
  const advance = useCallback(() => {
    if (at >= count - 1) setPlaying(false);
    else setPos(at + 1);
  }, [at, count]);
  const speaking = useNarration({ text: frame?.narration ?? "", playing: playing && drawn, rate, onDone: advance });

  const fullScreen = useCallback(() => {
    if (document.fullscreenElement) void document.exitFullscreen?.();
    else void stage.current?.requestFullscreen?.();
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (e.metaKey || e.ctrlKey || e.altKey || t?.closest("input, textarea, select")) return;
      const key = e.key.toLowerCase();
      if (e.key === " " && playing) setPlaying(false);
      else if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") setPos((p) => Math.min(p + 1, count - 1));
      else if (e.key === "ArrowLeft" || e.key === "PageUp") setPos((p) => Math.max(p - 1, 0));
      else if (e.key === "Home") setPos(0);
      else if (e.key === "End") setPos(Math.max(count - 1, 0));
      else if (key === "n") setNotes((v) => !v);
      else if (key === "k" && drawn && speech) setPlaying((v) => !v);
      else if (key === "c" && drawn) setCaptions((v) => !v);
      else if (key === "f" && drawn) fullScreen();
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [count, drawn, playing, speech, fullScreen]);

  if (error && !deck) return <div className="course-centered"><div>{error}</div></div>;
  if (!deck) return <div className="course-centered"><div>Loading…</div></div>;

  const slide = deck.slides[Math.min(at, deck.slides.length - 1)];
  const said = frame ? sentences(frame.narration) : [];
  const ask = () => {
    if (!frame || !onAsk) return;
    setPlaying(false);
    const source = frame.kind === "slide" && frame.source ? ` Its source is ${frame.source}.` : "";
    const point = frame.kind === "slide" && frame.takeaway ? ` Its takeaway: ${frame.takeaway}` : "";
    onAsk(`In the lecture "${deck.title}", explain the slide "${frame.title}".${point}${source}`);
  };

  return (
    <div className="course-scroll course-page" style={{ "--course": courseColor(deck.course) } as React.CSSProperties}>
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
        {!drawn && deck.status === "building" && <p className="slides-status" role="status">Rendering slide images… showing the text for now.</p>}
        {!drawn && deck.status === "text" && (
          <p className="slides-status" role="status">
            Slide images are not available here{deck.needs.length ? ` (needs ${deck.needs.join(", ")})` : ""}. Showing the text.
          </p>
        )}
        {!drawn && deck.status === "failed" && (
          <p className="slides-status" role="alert">
            The slide build failed{deck.error ? `: ${deck.error}` : ""}. Showing the text.
          </p>
        )}
        {frame ? (
          <>
            <div className="slide-progress" role="progressbar" aria-label="Place in the lecture" aria-valuemin={1} aria-valuemax={count} aria-valuenow={frame.n}>
              <i style={{ width: `${(frame.n / count) * 100}%` }} />
            </div>
            <section className="slide-stage slide-stage--frame" aria-label={`Slide ${frame.n} of ${count}`} ref={stage}>
              <SlideFrame frame={frame} total={count} courseColor={courseColor(deck.course)} />
            </section>
            <div className="slide-controls">
              <button onClick={() => setPos(Math.max(at - 1, 0))} disabled={at === 0} className="round-btn">Previous</button>
              <button onClick={() => setPos(Math.min(at + 1, count - 1))} disabled={at >= count - 1} className="btn-primary">Next</button>
              <button onClick={() => setCaptions((v) => !v)} aria-pressed={captions} className="round-btn" title="Show what the lecturer would say (c)">Read along</button>
              <button
                onClick={() => setPlaying((v) => !v)}
                disabled={!speech}
                aria-pressed={playing}
                title={speech ? "Read the lecture aloud in this browser's voice (k)" : "This browser cannot read text aloud"}
                className="round-btn"
              >
                {playing ? "Pause" : "Read aloud"}
              </button>
              {playing && (
                <select aria-label="Reading speed" value={rate} onChange={(e) => setRate(Number(e.target.value))}>
                  {RATES.map((r) => <option key={r} value={r}>{r}×</option>)}
                </select>
              )}
              <button onClick={() => setNotes((v) => !v)} aria-pressed={notes} className="round-btn">Notes</button>
              <button onClick={fullScreen} className="round-btn">Full screen</button>
              {onAsk && <button onClick={ask} className="round-btn">Ask about this slide</button>}
              <span className="flashcard-count">{frame.n} of {count}</span>
            </div>
            {captions && (
              <p className="slide-caption" aria-label="What is being said" data-testid="slide-caption">
                {said.length === 0 ? <span className="slide-caption-empty">Nothing is said on this slide.</span>
                  : said.map((s, i) => (
                    <span key={i} className={!playing ? undefined : i < speaking ? "said" : i === speaking ? "saying" : undefined}>{s} </span>
                  ))}
              </p>
            )}
            {notes && (
              <aside className="slide-notes" aria-label="Speaker notes">
                {frame.notes || <em>No notes for this slide.</em>}
              </aside>
            )}
            <nav className="slide-parts" aria-label="Parts of this lecture">
              <h2>In this lecture</h2>
              {outline(frames).map((group) => {
                const here = group.frames.includes(frame);
                return (
                  <div key={`${group.title}-${group.frames[0].n}`} className="slide-part">
                    <button onClick={() => setPos(group.frames[0].n - 1)} aria-current={here ? "true" : undefined}>{group.title}</button>
                    <div className="slide-thumbs">
                      {group.frames.map((f) => (
                        <button
                          key={f.n}
                          onClick={() => setPos(f.n - 1)}
                          className={`slide-thumb ${beatClass(f)}`}
                          aria-label={`Slide ${f.n}: ${f.title}`}
                          aria-current={f === frame ? "true" : undefined}
                          title={f.title}
                        >
                          {f.n}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </nav>
            <section className="slide-next" aria-label="After the lecture">
              <h2>{at >= count - 1 ? "You have reached the end. Next" : "After the lecture"}</h2>
              <div className="slide-next-links">
                <a href={`#/courses/${deck.module}`}>Notes and topic page</a>
                <a href={`#/quiz/${deck.module}?choice`}>Multiple choice</a>
                <a href={`#/flashcards/${deck.module}`}>Flashcards</a>
                <a href={`#/quiz/${deck.module}?worked`}>Worked problems</a>
                <a href="#/labs">Labs</a>
              </div>
            </section>
          </>
        ) : !slide ? (
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
              <button onClick={() => setPos(Math.max(at - 1, 0))} disabled={at === 0} className="round-btn">Previous</button>
              <button onClick={() => setPos(Math.min(at + 1, count - 1))} disabled={at >= count - 1} className="btn-primary">Next</button>
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
