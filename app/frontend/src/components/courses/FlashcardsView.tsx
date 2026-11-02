import { useEffect, useState } from "react";
import type { FlashcardDeck } from "../../courses/types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

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

function shuffled(n: number): number[] {
  const order = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

/** Flip through one deck: a module's cards or a single lesson's. No scheduling, no saved state. */
export function FlashcardsView({ deckId }: { deckId: string }) {
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [order, setOrder] = useState<number[]>([]);
  const [pos, setPos] = useState(0);
  const [flipped, setFlipped] = useState(false);
  useDocumentTitle(pageTitle(deck?.id === deckId ? deck.title : "Loading…", "Flashcards"));

  useEffect(() => {
    let cancelled = false;
    setDeck(null);
    setError(null);
    fetch(`/api/courses/flashcards/${deckId}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status === 404 ? "No flashcards here" : `HTTP ${r.status}`))))
      .then((d: FlashcardDeck) => {
        if (cancelled) return;
        setDeck(d);
        setOrder(d.cards.map((_, i) => i));
        setPos(0);
        setFlipped(false);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, [deckId]);

  if (error) return <div className="course-centered"><div>{error}</div></div>;
  if (!deck || !order.length) return <div className="course-centered"><div>Loading…</div></div>;

  const card = deck.cards[order[pos]];
  const turn = (next: number) => { setPos(next); setFlipped(false); };
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <a href={`#/courses/${deck.course}`} className="link-btn">← Course</a>
        <h1 className="course-page-title course-page-title--overview">{deck.title}</h1>
        <button onClick={() => setFlipped((f) => !f)} aria-pressed={flipped} className={`flashcard${flipped ? " is-flipped" : ""}`}>
          <span className="flashcard-side">{flipped ? "Answer" : "Question (click to flip)"}</span>
          <span className="flashcard-text"><InlineMarkup text={flipped ? card.back : card.front} /></span>
        </button>
        {flipped && card.lesson && deck.id !== card.lesson && (
          <div className="flashcard-source">From <a href={`#/courses/${card.lesson}`}>{card.lessonTitle}</a></div>
        )}
        <div className="flashcard-controls">
          <button onClick={() => turn((pos + 1) % order.length)} className="btn-primary">Next</button>
          <button onClick={() => { setOrder(shuffled(deck.cards.length)); turn(0); }} className="round-btn">Shuffle</button>
          <span className="flashcard-count">{pos + 1} of {order.length}</span>
        </div>
      </div>
    </div>
  );
}
