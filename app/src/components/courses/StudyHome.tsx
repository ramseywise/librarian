import { useEffect, useState } from "react";
import type { StudyHomeData } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";
import { apiFetch } from "../../utils/api";

/** The study queue, the entry point to practice: cards and questions due, the next drill for the weakest
 * track, and the lecture for the module in hand. Every row links to the existing views (`#/flashcards/<id>?due`,
 * `#/quiz/<id>?due`, `#/slides/<id>`), so each stays reachable on its own. */
export function StudyHome() {
  const [home, setHome] = useState<StudyHomeData | null>(null);
  const [error, setError] = useState<string | null>(null);
  useDocumentTitle(pageTitle("Study"));

  useEffect(() => {
    let cancelled = false;
    apiFetch("/api/courses/study")
      .then((r) => (r.ok ? (r.json() as Promise<StudyHomeData>) : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d) => !cancelled && setHome(d))
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, []);

  if (error) return <div className="course-centered"><div>Could not load the study queue: {error}</div></div>;
  if (!home) return <div className="course-centered"><div>Loading…</div></div>;

  const drill = home.nextDrill;
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <h1 className="course-page-title">Study</h1>
        <p className="course-page-lede">
          {home.due || home.new
            ? `${home.due} due today, ${home.new} new.`
            : "Nothing due today."}
        </p>

        <section className="study-block" aria-label="Due today">
          <h2 className="study-heading">Due today</h2>
          {home.modules.length === 0 ? (
            <p className="practice-status">No flashcards or questions are due.</p>
          ) : (
            <ul className="study-list">
              {home.modules.map((m) => (
                <li key={m.module}>
                  <span className="study-module">{m.title}</span>
                  {(m.cards.due > 0 || m.cards.new > 0) && (
                    <a href={`#/flashcards/${m.module}?due`}>
                      Flashcards ({m.cards.due} due, {m.cards.new} new)
                    </a>
                  )}
                  {(m.questions.due > 0 || m.questions.new > 0) && (
                    <a href={`#/quiz/${m.module}?due`}>
                      Quiz ({m.questions.due} due, {m.questions.new} new)
                    </a>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="study-block" aria-label="Next drill">
          <h2 className="study-heading">Next drill</h2>
          {drill ? (
            <p>
              <a href="#/practice">{drill.title}</a>
              <span className="study-meta">
                {" "}
                {drill.track}
                {drill.drill?.difficulty ? `, ${drill.drill.difficulty}` : ""}
                {drill.reason === "weakest track" ? " (your weakest track)" : ""}
              </span>
            </p>
          ) : (
            <p className="practice-status">No drills yet.</p>
          )}
        </section>

        <section className="study-block" aria-label="Lecture">
          <h2 className="study-heading">Lecture</h2>
          {home.lecture ? (
            <>
              <p className="study-meta">{home.lecture.title}</p>
              <ul className="study-list">
                {home.lecture.decks.map((d) => (
                  <li key={d.id}><a href={`#/slides/${d.id}`}>{d.title}</a></li>
                ))}
              </ul>
            </>
          ) : (
            <p className="practice-status">No slides yet.</p>
          )}
        </section>
      </div>
    </div>
  );
}
