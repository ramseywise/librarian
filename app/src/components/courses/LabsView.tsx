import { useMemo, useState } from "react";
import { useLabs } from "../../hooks/useCourses";
import { languageLabel, moduleLabel } from "../../utils/labs";
import type { LabRow } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

interface Props {
  onOpenLab: (labId: string) => void;
  onOpenLesson: (lessonId: string) => void;
  onOpenDrills: () => void;
}

/** Labs mode: every course's runnable practice examples, by course and module, each linked to its notes. */
export function LabsView({ onOpenLab, onOpenLesson, onOpenDrills }: Props) {
  const { data, error, retry } = useLabs();
  const [course, setCourse] = useState("");
  const [module, setModule] = useState("");
  useDocumentTitle(pageTitle("Labs"));

  const labs = useMemo(() => data?.labs ?? [], [data]);
  const courses = useMemo(() => [...new Set(labs.map((l) => l.course))], [labs]);
  const modules = useMemo(
    () => [...new Set(labs.filter((l) => l.course === course).map((l) => l.module))],
    [labs, course],
  );
  const shown = labs.filter((l) => (!course || l.course === course) && (!module || l.module === module));
  const groups = useMemo(() => {
    const out = new Map<string, LabRow[]>();
    for (const lab of shown) {
      const key = `${lab.course}/${lab.module}`;
      out.set(key, [...(out.get(key) ?? []), lab]);
    }
    return [...out.entries()];
  }, [shown]);

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        <h1 className="course-page-title">Labs</h1>
        <p className="course-page-lede">
          The code behind the notes: open a lab, run it, change it, check it, and ask the librarian about what it printed.{" "}
          <button onClick={onOpenDrills} className="practice-link">Timed coding drills →</button>
        </p>
        {data && !data.canRun && (
          <div className="lab-callout">
            Labs open read-only here. Running one is local only: start the API with <code>make api</code>.
          </div>
        )}
        {error && (
          <div className="practice-error">
            Could not load labs: {error}{" "}
            <button onClick={retry} className="practice-link practice-link--retry">Retry</button>
          </div>
        )}
        {!data && !error && <div className="practice-status">Loading labs…</div>}
        {data && !labs.length && (
          <div className="practice-status">
            No labs yet. They come from each pillar's <code>practice/manifest.yaml</code> on <code>librarian courses import</code>.
          </div>
        )}
        {labs.length > 0 && (
          <>
            <div className="practice-filters">
              <Chip label="All courses" active={!course} onClick={() => { setCourse(""); setModule(""); }} />
              {courses.map((c) => (
                <Chip key={c} label={c} active={course === c} onClick={() => { setCourse(c); setModule(""); }} />
              ))}
            </div>
            {course && modules.length > 1 && (
              <div className="practice-filters">
                <Chip label="All modules" active={!module} onClick={() => setModule("")} />
                {modules.map((m) => (
                  <Chip key={m} label={moduleLabel(m)} active={module === m} onClick={() => setModule(m)} />
                ))}
              </div>
            )}
            {groups.map(([key, rows]) => (
              <section key={key} className="lab-group">
                <h2 className="section-label">
                  {rows[0].course} · {moduleLabel(rows[0].module)}
                </h2>
                {rows.map((lab) => (
                  <div key={lab.id} className="course-nav-item practice-row">
                    <button onClick={() => onOpenLab(lab.id)} className="practice-title">
                      {lab.title}
                    </button>
                    {lab.purpose && <div className="lab-purpose">{lab.purpose}</div>}
                    <div className="practice-meta">
                      <span className="lab-badge">{languageLabel(lab.language)}</span>
                      {lab.hasCheck && <span className="lab-badge lab-badge--check" title="Has a check this app can run">check</span>}
                      {!lab.runsOffline && <span className="lab-badge" title="Calls a model provider">online</span>}
                      {lab.notes.map((n) => (
                        <button key={n.id} onClick={() => onOpenLesson(n.id)} title={n.summary} className="practice-link">
                          ▤ {n.title}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </section>
            ))}
            {!shown.length && <div className="practice-status">No labs match.</div>}
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
