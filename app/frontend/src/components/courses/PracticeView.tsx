import { useEffect, useMemo, useState } from "react";
import type { PracticeDrill } from "../../courses/types";
import { useCourseProgress } from "../../hooks/useCourseProgress";
import { DrillBadges } from "./LessonView";
import "./courses.css";

interface Props {
  onOpenLesson: (lessonId: string) => void;
  onOpenConcept: (pageId: string) => void;
}

const DIFFICULTIES = ["easy", "medium", "hard"];

/** Practice mode — the gym: every drill (lesson kind "drill"), filterable by track and difficulty. */
export function PracticeView({ onOpenLesson, onOpenConcept }: Props) {
  const [drills, setDrills] = useState<PracticeDrill[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [track, setTrack] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const { done } = useCourseProgress();

  useEffect(() => {
    fetch("/api/courses/practice")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setDrills)
      .catch((e: Error) => setError(e.message));
  }, []);

  const tracks = useMemo(() => [...new Set((drills ?? []).map((d) => d.drill.track))].sort(), [drills]);
  const shown = (drills ?? []).filter(
    (d) => (!track || d.drill.track === track) && (!difficulty || d.drill.difficulty === difficulty)
  );

  return (
    <div className="course-scroll" style={{ height: "100%", overflowY: "auto" }}>
      <div style={{ maxWidth: 880, margin: "0 auto", padding: "40px 24px 60px" }}>
        <h1 style={{ color: "#f0f0f0", fontSize: 28, margin: "0 0 6px" }}>Practice</h1>
        <p style={{ color: "#888", margin: "0 0 20px", fontSize: 14 }}>
          Timed drills from sisyphus, by language. Attempt cold, then open the solution.
        </p>
        {error && <div style={{ color: "#EF5350", fontSize: 13 }}>Could not load drills: {error}</div>}
        {!drills && !error && <div style={{ color: "#666", fontSize: 13 }}>Loading drills…</div>}
        {drills && !drills.length && (
          <div style={{ color: "#666", fontSize: 13 }}>
            No drills yet. Add files following the schema in sisyphus <code>drills/README.md</code>, then run{" "}
            <code>make import-courses</code>.
          </div>
        )}
        {drills && drills.length > 0 && (
          <>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 16 }}>
              <Chip label="All tracks" active={!track} onClick={() => setTrack("")} />
              {tracks.map((t) => <Chip key={t} label={t} active={track === t} onClick={() => setTrack(t)} />)}
              <span style={{ width: 16 }} />
              <Chip label="Any level" active={!difficulty} onClick={() => setDifficulty("")} />
              {DIFFICULTIES.map((d) => (
                <Chip key={d} label={d} active={difficulty === d} onClick={() => setDifficulty(d)} />
              ))}
            </div>
            {shown.map((d) => (
              <div key={d.id} className="course-nav-item" style={rowStyle}>
                <button onClick={() => onOpenLesson(d.id)} style={titleBtnStyle}>
                  {done.has(d.id) && <span style={{ color: "#4CAF50" }}>✓ </span>}
                  {d.title}
                </button>
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginTop: 4 }}>
                  <DrillBadges drill={d.drill} />
                  {d.concepts.map((c) => (
                    <button key={c.id} onClick={() => onOpenConcept(c.id)} title={c.summary} style={conceptStyle}>
                      ◆ {c.title}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            {!shown.length && <div style={{ color: "#666", fontSize: 13 }}>No drills match.</div>}
          </>
        )}
      </div>
    </div>
  );
}

function Chip({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} style={{
      background: active ? "#1f2a36" : "#151515", border: "1px solid", borderColor: active ? "#2f4b66" : "#262626",
      color: active ? "#90caf9" : "#999", borderRadius: 14, fontSize: 12, padding: "4px 12px", cursor: "pointer",
      fontFamily: "inherit",
    }}>
      {label}
    </button>
  );
}

const rowStyle: React.CSSProperties = {
  border: "1px solid #222", borderRadius: 8, padding: "12px 14px", marginBottom: 8,
};
const titleBtnStyle: React.CSSProperties = {
  background: "none", border: "none", padding: 0, color: "#e0e0e0", fontSize: 15, fontWeight: 500,
  cursor: "pointer", fontFamily: "inherit", textAlign: "left",
};
const conceptStyle: React.CSSProperties = {
  background: "none", border: "none", padding: 0, color: "#ce93d8", fontSize: 12, cursor: "pointer", fontFamily: "inherit",
};
