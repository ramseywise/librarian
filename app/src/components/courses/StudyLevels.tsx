import type { LevelProgress, StudyProgress } from "./types";

type Level = "choice" | "cards" | "worked";

/** "20 of 32 right · 4 to redo": what the caller has right, and what they last got wrong. */
function stat(level: Level, p: LevelProgress): string {
  const word = level === "choice" ? "right" : level === "cards" ? "known" : "solved";
  return `${p.right} of ${p.total} ${word}${p.redo ? ` · ${p.redo} to redo` : ""}`;
}

/** The study formats a module or lesson has, easiest first: multiple choice (recognise the answer), flashcards
 * (recall it), worked problems (calculate it). One tile per format it has; a format with nothing is left out.
 * With `progress` (a module's, from `GET /api/courses/study-progress`) each tile carries a meter and its tally. */
export function StudyLevels({ id, quizCount, flashcardCount, problemCount, progress }: {
  id: string;
  quizCount?: number;
  flashcardCount?: number;
  problemCount?: number;
  progress?: StudyProgress[string];
}) {
  const levels = [
    quizCount ? { level: 1, key: "choice" as Level, href: `#/quiz/${id}?choice`, name: "Multiple choice", does: "recognise", count: `${quizCount} questions` } : null,
    flashcardCount ? { level: 2, key: "cards" as Level, href: `#/flashcards/${id}`, name: "Flashcards", does: "recall", count: `${flashcardCount} cards` } : null,
    problemCount ? { level: 3, key: "worked" as Level, href: `#/quiz/${id}?worked`, name: "Worked problems", does: "calculate", count: `${problemCount} problems` } : null,
  ].filter((l) => l !== null);
  if (!levels.length) return null;
  return (
    <div className="study-levels" role="group" aria-label="Test yourself">
      {levels.map((l) => {
        const p = progress?.[l.key];
        const tried = !!p && p.right + p.redo > 0;
        return (
          <a key={l.level} href={l.href} className="study-tile" aria-label={`Level ${l.level}: ${l.name.toLowerCase()}, ${l.count}`}>
            <span className="study-tile-level">Level {l.level} · {l.does}</span>
            <span className="study-tile-name">{l.name}</span>
            {p ? (
              <>
                <span className="study-meter" role="meter" aria-label={`${l.name} right`} aria-valuemin={0} aria-valuemax={p.total} aria-valuenow={p.right}>
                  <i style={{ width: `${p.total ? Math.round((p.right / p.total) * 100) : 0}%` }} />
                </span>
                <span className="study-tile-stat">{stat(l.key, p)}</span>
                <span className="study-tile-go">{tried ? "Continue" : "Start"}</span>
              </>
            ) : (
              <span className="study-tile-count">{l.count}</span>
            )}
          </a>
        );
      })}
    </div>
  );
}
