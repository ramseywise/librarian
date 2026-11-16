/** The study formats a module or lesson has, easiest first: multiple choice (recognise the answer), flashcards
 * (recall it), worked problems (calculate it). One tile per format it has; a format with nothing is left out. */
export function StudyLevels({ id, quizCount, flashcardCount, problemCount }: {
  id: string;
  quizCount?: number;
  flashcardCount?: number;
  problemCount?: number;
}) {
  const levels = [
    quizCount ? { level: 1, href: `#/quiz/${id}?choice`, name: "Multiple choice", does: "recognise", count: `${quizCount} questions` } : null,
    flashcardCount ? { level: 2, href: `#/flashcards/${id}`, name: "Flashcards", does: "recall", count: `${flashcardCount} cards` } : null,
    problemCount ? { level: 3, href: `#/quiz/${id}?worked`, name: "Worked problems", does: "calculate", count: `${problemCount} problems` } : null,
  ].filter((l) => l !== null);
  if (!levels.length) return null;
  return (
    <div className="study-levels" role="group" aria-label="Test yourself">
      {levels.map((l) => (
        <a key={l.level} href={l.href} className="study-tile" aria-label={`Level ${l.level}: ${l.name.toLowerCase()}, ${l.count}`}>
          <span className="study-tile-level">Level {l.level} · {l.does}</span>
          <span className="study-tile-name">{l.name}</span>
          <span className="study-tile-count">{l.count}</span>
        </a>
      ))}
    </div>
  );
}
