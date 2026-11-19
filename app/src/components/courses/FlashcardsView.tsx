import { useEffect, useRef, useState } from "react";
import type { Flashcard, FlashcardDeck } from "./types";
import { StudyFilter } from "./StudyFilter";
import { studyOrder, type StudyMode } from "./studyQueue";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";
import { flashcardDeckSchema } from "../../schemas/courses";
import { apiFetch, parseJson } from "../../utils/api";
import type { StudyChatContext } from "../../hooks/useChatStream";

/** Deck text allows `**bold**` and `code` and nothing else (deck-spec.md), so no Markdown parser. */
export function InlineMarkup({ text }: { text: string }) {
  return (
    <>
      {text.split(/(`[^`]+`|\*\*.+?\*\*)/).map((part, i) => {
        if (part.startsWith("`") && part.endsWith("`") && part.length > 2) return <code key={i}>{part.slice(1, -1)}</code>;
        if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
          return <strong key={i}><InlineMarkup text={part.slice(2, -2)} /></strong>;
        }
        return part;
      })}
    </>
  );
}

/** A card reference: plain text, with any `[text](http...)` in it as a link. Only web links are kept by
 * the generator, and nothing else is linked here. */
function SourceRef({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\[[^\]]+\]\(https?:\/\/[^)\s]+\))/).map((part, i) => {
        const link = /^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/.exec(part);
        return link ? <a key={i} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a> : part;
      })}
    </>
  );
}

function shuffled(n: number): number[] {
  const order = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

/** Flip through one deck: a module's cards or a single lesson's. A grade only appends to the server's log,
 * which the Leitner schedule (librarian/courses/leitner.py) and coursework review read; a failed write never
 * interrupts studying. A route ending in `?due` opens on the cards to study today. */
export function FlashcardsView({
  deckId: route,
  onChatContext,
}: {
  deckId: string;
  /** Registers what the chat is told about the card on screen (its ids; the server builds the brief). */
  onChatContext?: (get: (() => StudyChatContext | null) | null) => void;
}) {
  const [deckId, query] = route.split("?");
  const [mode, setMode] = useState<StudyMode>("all");
  const [graded, setGraded] = useState<ReadonlySet<string>>(new Set());
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [order, setOrder] = useState<number[]>([]);
  const [pos, setPos] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [inDepth, setInDepth] = useState(false);
  useDocumentTitle(pageTitle(deck?.id === deckId ? deck.title : "Loading…", "Flashcards"));

  useEffect(() => {
    let cancelled = false;
    setDeck(null);
    setError(null);
    apiFetch(`/api/courses/flashcards/${deckId}`)
      .then((r) => (r.ok ? parseJson(r, flashcardDeckSchema) : Promise.reject(new Error(r.status === 404 ? "No flashcards here" : `HTTP ${r.status}`))))
      .then((d) => {
        if (cancelled) return;
        const start = query === "due" ? "due" : "all";
        setDeck(d);
        setMode(start);
        setGraded(new Set());
        setOrder(studyOrder(d.cards, start, new Set()));
        setPos(0);
        setFlipped(false);
        setInDepth(false);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, [deckId, query]);

  // The chat reads the card on screen through a ref, so registering once is enough.
  const shownRef = useRef<StudyChatContext | null>(null);
  const shown = deck?.cards[order[pos]];
  shownRef.current = deck && shown ? { deck: deck.id, card: shown.id } : null;
  useEffect(() => {
    if (!onChatContext) return;
    onChatContext(() => shownRef.current);
    return () => onChatContext(null);
  }, [onChatContext]);

  if (error) return <div className="course-centered"><div>{error}</div></div>;
  if (!deck || (!order.length && mode === "all")) return <div className="course-centered"><div>Loading…</div></div>;

  const card: Flashcard | undefined = deck.cards[order[pos]];
  const turn = (next: number) => { setPos(next); setFlipped(false); setInDepth(false); };
  const labels = card ? [card.tier, card.depth].filter(Boolean).join(" · ") : "";
  const study = (next: StudyMode) => {
    setMode(next);
    setOrder(studyOrder(deck.cards, next, graded));
    turn(0);
  };
  const grade = (result: "knew" | "missed") => {
    if (!card) return;
    void apiFetch("/api/courses/flashcard-results", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ deck: deck.id, card: card.id, result }),
    }).catch(() => undefined);
    setGraded((g) => new Set(g).add(card.id));
    if (mode === "due") {
      // Graded either way means not due again today: a miss comes back tomorrow.
      const rest = order.filter((_, i) => i !== pos);
      setOrder(rest);
      turn(rest.length ? pos % rest.length : 0);
    } else {
      turn((pos + 1) % order.length);
    }
  };
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <a href={`#/courses/${deck.course}`} className="link-btn">← Course</a>
        <h1 className="course-page-title course-page-title--overview">{deck.title}</h1>
        <StudyFilter cards={deck.cards} mode={mode} graded={graded} onChange={study} />
        {!card ? (
          <p className="flashcard-done">Nothing left to study today in this deck.</p>
        ) : (
        <>
        <button onClick={() => setFlipped((f) => !f)} aria-pressed={flipped} className={`flashcard${flipped ? " is-flipped" : ""}`}>
          <span className="flashcard-side">{flipped ? "Answer" : "Question (click to flip)"}{labels && ` · ${labels}`}</span>
          <span className="flashcard-text"><InlineMarkup text={flipped ? card.back : card.front} /></span>
        </button>
        {flipped && card.more && (
          <div className="flashcard-more">
            <button onClick={() => setInDepth((d) => !d)} aria-expanded={inDepth} className="link-btn">
              {inDepth ? "Hide the in-depth answer" : "In depth"}
            </button>
            {inDepth && <p className="flashcard-more-text"><InlineMarkup text={card.more} /></p>}
          </div>
        )}
        {flipped && card.lesson && deck.id !== card.lesson && (
          <div className="flashcard-source">From <a href={`#/courses/${card.lesson}`}>{card.lessonTitle}</a></div>
        )}
        {flipped && !!card.sources?.length && (
          <ul className="flashcard-source flashcard-refs" aria-label="Sources">
            {card.sources.map((s) => <li key={s}><SourceRef text={s} /></li>)}
          </ul>
        )}
        <div className="flashcard-controls">
          {flipped && <button onClick={() => grade("knew")} className="btn-primary">Knew it</button>}
          {flipped && <button onClick={() => grade("missed")} className="round-btn">Missed it</button>}
          <button onClick={() => turn((pos + 1) % order.length)} className={flipped ? "round-btn" : "btn-primary"}>Next</button>
          <button onClick={() => { setOrder(shuffled(order.length).map((i) => order[i])); turn(0); }} className="round-btn">Shuffle</button>
          <span className="flashcard-count">{card.status && <span className="flashcard-box">{card.box ? `Box ${card.box}` : "New"} · </span>}{pos + 1} of {order.length}</span>
        </div>
        </>
        )}
      </div>
    </div>
  );
}
