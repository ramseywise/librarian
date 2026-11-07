import { useEffect, useMemo, useState } from "react";
import type { Quiz, QuizAnswerResult, QuizQuestion } from "./types";
import { InlineMarkup } from "./FlashcardsView";
import { quizOrder } from "./studyQueue";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

function shuffled<T>(items: T[]): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/** One module's or lesson's multiple-choice quiz. The server grades (the answer is never sent ahead) and
 * stores each result; a wrong answer is due again tomorrow, like a missed flashcard. `#/quiz/<id>[?due]`. */
export function QuizView({ quizId: route }: { quizId: string }) {
  const [quizId, query] = route.split("?");
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [queue, setQueue] = useState<QuizQuestion[]>([]);
  const [pos, setPos] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);
  const [result, setResult] = useState<QuizAnswerResult | null>(null);
  const [right, setRight] = useState(0);
  const [saveFailed, setSaveFailed] = useState(false);
  useDocumentTitle(pageTitle(quiz?.id === quizId ? quiz.title : "Loading…", "Quiz"));

  useEffect(() => {
    let cancelled = false;
    setQuiz(null);
    setError(null);
    fetch(`/api/courses/quiz/${quizId}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status === 404 ? "No quiz here" : `HTTP ${r.status}`))))
      .then((q: Quiz) => {
        if (cancelled) return;
        setQuiz(q);
        setQueue(quizOrder(q.questions, query === "due"));
        setPos(0);
        setPicked(null);
        setResult(null);
        setRight(0);
      })
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, [quizId, query]);

  const question: QuizQuestion | undefined = queue[pos];
  // Options are shuffled once per question; the answer is an option's text, so order carries nothing.
  const options = useMemo(() => (question ? shuffled(question.options) : []), [question]);

  if (error) return <div className="course-centered"><div>{error}</div></div>;
  if (!quiz) return <div className="course-centered"><div>Loading…</div></div>;

  const answer = async (choice: string) => {
    if (!question || result) return;
    setPicked(choice);
    setSaveFailed(false);
    try {
      const r = await fetch("/api/courses/quiz-results", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz: quiz.id, question: question.id, choice }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const graded = (await r.json()) as QuizAnswerResult;
      setResult(graded);
      if (graded.correct) setRight((n) => n + 1);
      if (!graded.logged) setSaveFailed(true);
    } catch {
      setPicked(null);
      setSaveFailed(true);
    }
  };
  const next = () => {
    setPos(pos + 1);
    setPicked(null);
    setResult(null);
  };
  const restart = (dueOnly: boolean) => {
    setQueue(quizOrder(quiz.questions, dueOnly));
    setPos(0);
    setPicked(null);
    setResult(null);
    setRight(0);
  };

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <a href={`#/courses/${quiz.course}`} className="link-btn">← Course</a>
        <h1 className="course-page-title course-page-title--overview">{quiz.title}</h1>
        {!question ? (
          <div className="quiz-done">
            <p className="flashcard-done">
              {queue.length
                ? `Done: ${right} of ${queue.length} right.`
                : "Nothing left to study today in this quiz."}
            </p>
            <div className="flashcard-controls">
              <button onClick={() => restart(false)} className="round-btn">All {quiz.questions.length} questions</button>
              <button onClick={() => restart(true)} className="round-btn">Due and new only</button>
            </div>
          </div>
        ) : (
          <>
            <div className="quiz-prompt"><InlineMarkup text={question.prompt} /></div>
            <div className="quiz-options" role="group" aria-label="Answers">
              {options.map((o) => {
                const state = !result ? "" : o === result.answer ? " is-right" : o === picked ? " is-wrong" : "";
                return (
                  <button
                    key={o}
                    onClick={() => void answer(o)}
                    disabled={!!result}
                    aria-pressed={picked === o}
                    className={`quiz-option${state}`}
                  >
                    <InlineMarkup text={o} />
                  </button>
                );
              })}
            </div>
            {result && (
              <div className="quiz-feedback" role="status">
                <strong>{result.correct ? "Correct." : "Not quite."}</strong>{" "}
                {!result.correct && <>The answer is <InlineMarkup text={result.answer} />. </>}
                {result.explanation && <InlineMarkup text={result.explanation} />}
                {question.lesson && (
                  <div className="flashcard-source">From <a href={`#/courses/${question.lesson}`}>{question.lessonTitle}</a></div>
                )}
              </div>
            )}
            {saveFailed && <p className="slides-status" role="alert">That answer was not saved.</p>}
            <div className="flashcard-controls">
              {result && <button onClick={next} className="btn-primary">{pos + 1 < queue.length ? "Next" : "Finish"}</button>}
              <span className="flashcard-count">
                {question.status && <span className="flashcard-box">{question.box ? `Box ${question.box}` : "New"} · </span>}
                {pos + 1} of {queue.length}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
