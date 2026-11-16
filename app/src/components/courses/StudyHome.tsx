import { useCourses } from "../../hooks/useCourses";
import type { CourseModule } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

type Counts = Pick<CourseModule, "quizCount" | "flashcardCount" | "problemCount">;

/** The three formats, easiest first; the same order and routes as StudyLevels. */
const LEVELS = [
  { name: "Multiple choice", does: "recognise", count: (c: Counts) => c.quizCount, unit: "questions", href: (id: string) => `#/quiz/${id}?choice` },
  { name: "Flashcards", does: "recall", count: (c: Counts) => c.flashcardCount, unit: "cards", href: (id: string) => `#/flashcards/${id}` },
  { name: "Worked problems", does: "calculate", count: (c: Counts) => c.problemCount, unit: "problems", href: (id: string) => `#/quiz/${id}?worked` },
] as const;

const hasStudy = (c: Counts) => LEVELS.some((l) => l.count(c));

function LevelCells({ id, title, counts }: { id: string; title: string; counts: Counts }) {
  return (
    <>
      {LEVELS.map((l) => {
        const n = l.count(counts);
        return (
          <td key={l.name} className="study-cell">
            {n ? (
              <a href={l.href(id)} aria-label={`${title}: ${l.name.toLowerCase()}, ${n} ${l.unit}`}>{n} {l.unit}</a>
            ) : (
              <span className="study-none" aria-label="none">–</span>
            )}
          </td>
        );
      })}
    </>
  );
}

/** Everything there is to test yourself on, as one table per course: a row per module (the topic) and a column
 * per level. Each cell links to that format for the module (`#/quiz/<id>?choice`, `#/flashcards/<id>`,
 * `#/quiz/<id>?worked`); the topic links to the module's page, which lists its lessons. */
export function StudyHome() {
  const { data: courses, error } = useCourses();
  useDocumentTitle(pageTitle("Study"));

  if (error) return <div className="course-centered"><div>Could not load the study topics: {error}</div></div>;
  if (!courses) return <div className="course-centered"><div>Loading…</div></div>;

  const domains = courses
    .map((c) => ({ ...c, modules: c.modules.filter(hasStudy) }))
    .filter((c) => c.modules.length);

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <h1 className="course-page-title">Study</h1>
        <p className="course-page-lede">
          Each topic at up to three levels: {LEVELS.map((l, i) => `${i ? ", " : ""}${l.name.toLowerCase()} (${l.does})`)}.
        </p>
        {domains.length === 0 ? (
          <p className="practice-status">No flashcards or questions yet.</p>
        ) : (
          domains.map((c) => (
            <section key={c.id} className="study-block" aria-label={c.title}>
              <h2 className="study-heading">{c.title}</h2>
              <table className="study-table">
                <thead>
                  <tr>
                    <th scope="col">Topic</th>
                    {LEVELS.map((l, i) => (
                      <th key={l.name} scope="col"><span className="study-level-no">Level {i + 1}</span> {l.name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {c.modules.map((m) => {
                    const id = `${c.id}/${m.id}`;
                    return (
                      <tr key={id} className="study-topic">
                        <th scope="row"><a href={`#/courses/${id}`}>{m.title}</a></th>
                        <LevelCells id={id} title={m.title} counts={m} />
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
