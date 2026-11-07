import type { Flashcard } from "./types";
import { isToStudy, type StudyMode } from "./studyQueue";

/** All cards, or today's. Renders nothing for a deck with no schedule. */
export function StudyFilter({ cards, mode, graded, onChange }: {
  cards: Flashcard[];
  mode: StudyMode;
  graded: ReadonlySet<string>;
  onChange: (mode: StudyMode) => void;
}) {
  if (!cards.some((c) => c.status)) return null;
  const left = cards.filter((c) => isToStudy(c, graded));
  const due = left.filter((c) => c.status === "due").length;
  return (
    <div className="flashcard-filter" role="group" aria-label="Study filter">
      <button type="button" aria-pressed={mode === "due"} className={mode === "due" ? "btn-primary" : "round-btn"} onClick={() => onChange("due")}>
        Due today: {due} + {left.length - due} new
      </button>
      <button type="button" aria-pressed={mode === "all"} className={mode === "all" ? "btn-primary" : "round-btn"} onClick={() => onChange("all")}>
        All {cards.length}
      </button>
    </div>
  );
}
