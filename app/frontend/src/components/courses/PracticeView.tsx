import { useMemo, useState } from "react";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { usePracticeDrills } from "../../hooks/useCourses";
import { DrillTimer } from "./DrillTimer";
import { DrillBadges } from "./LessonView";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

interface Props {
  onOpenLesson: (lessonId: string) => void;
  onOpenConcept: (pageId: string) => void;
}

const DIFFICULTIES = ["easy", "medium", "hard"];

/** Practice mode — the gym: every drill (lesson kind "drill"), filterable by track and difficulty. */
export function PracticeView({ onOpenLesson, onOpenConcept }: Props) {
  const { data: drills, error, retry } = usePracticeDrills();
  const [track, setTrack] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const { done } = useCourseProgress();
  useDocumentTitle(pageTitle("Practice"));

  const tracks = useMemo(() => [...new Set((drills ?? []).map((d) => d.drill.track))].sort(), [drills]);
  const shown = (drills ?? []).filter(
    (d) => (!track || d.drill.track === track) && (!difficulty || d.drill.difficulty === difficulty)
  );

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <h1 className="course-page-title">Practice</h1>
        <p className="course-page-lede">
          Timed drills from sisyphus, by language. Attempt cold, then open the solution.
        </p>
        {error && (
          <div className="practice-error">
            Could not load drills: {error}{" "}
            <button onClick={retry} className="practice-link practice-link--retry">Retry</button>
          </div>
        )}
        {!drills && !error && <div className="practice-status">Loading drills…</div>}
        {drills && !drills.length && (
          <div className="practice-status">
            No drills yet. Add files following the schema in sisyphus <code>drills/README.md</code>, then run{" "}
            <code>make import-courses</code>.
          </div>
        )}
        {drills && drills.length > 0 && (
          <>
            <div className="practice-filters">
              <Chip label="All tracks" active={!track} onClick={() => setTrack("")} />
              {tracks.map((t) => <Chip key={t} label={t} active={track === t} onClick={() => setTrack(t)} />)}
              <span className="practice-filters-gap" />
              <Chip label="Any level" active={!difficulty} onClick={() => setDifficulty("")} />
              {DIFFICULTIES.map((d) => (
                <Chip key={d} label={d} active={difficulty === d} onClick={() => setDifficulty(d)} />
              ))}
            </div>
            {shown.map((d) => (
              <div key={d.id} className="course-nav-item practice-row">
                <button onClick={() => onOpenLesson(d.id)} className="practice-title">
                  {done.has(d.id) && <span className="text-success">✓ </span>}
                  {d.title}
                </button>
                <div className="practice-meta">
                  <DrillBadges drill={d.drill} />
                  {d.drill.timebox_min ? <DrillTimer lessonId={d.id} timeboxMin={d.drill.timebox_min} compact /> : null}
                  {d.attempts && (
                    <span title={`Last score: ${d.attempts.score}`} className="practice-attempts">
                      {d.attempts.count}× · last {d.attempts.last}
                    </span>
                  )}
                  {d.concepts.map((c) => (
                    <button key={c.id} onClick={() => onOpenConcept(c.id)} title={c.summary} className="practice-link">
                      ◆ {c.title}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            {!shown.length && <div className="practice-status">No drills match.</div>}
          </>
        )}
      </div>
    </div>
  );
}

function Chip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`filter-chip${active ? " is-active" : ""}`}>
      {label}
    </button>
  );
}
