import { useEffect, useState } from "react";
import type { FlashcardsDueSummary } from "../../courses/types";

/** Modules listed; the total still counts every one. */
const MAX_MODULES = 6;

/** What the flashcard schedule asks for today. An unavailable summary shows nothing: it's optional. */
export function FlashcardsDue() {
  const [summary, setSummary] = useState<FlashcardsDueSummary | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/courses/flashcards-due")
      .then((r) => (r.ok ? (r.json() as Promise<FlashcardsDueSummary>) : null))
      .then((body) => {
        if (!cancelled && typeof body?.due === "number") setSummary(body);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  if (!summary || (!summary.due && !summary.new)) return null;
  return (
    <section className="flashcards-due" aria-label="Flashcards due today">
      <span className="flashcards-due-title">Flashcards</span>: {summary.due} due today, {summary.new} new
      <ul>
        {summary.modules.slice(0, MAX_MODULES).map((m) => (
          <li key={m.deck}>
            <a href={`#/flashcards/${m.deck}?due`}>{m.title}</a> ({m.due} due, {m.new} new)
          </li>
        ))}
      </ul>
    </section>
  );
}
