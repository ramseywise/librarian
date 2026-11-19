import { useEffect, useState } from "react";
import type { Course, SearchHit } from "./types";
import { searchHitsSchema } from "../../schemas/courses";
import { apiFetch, parseJson } from "../../utils/api";
import { lessonsOf } from "./courseLogic";
import { SearchBox, ProgressBar } from "./courseBits";

export function Catalog({ courses, done, onOpen }: {
  courses: Course[]; done: Set<string>; onOpen: (p: string) => void;
}) {
  const [query, setQuery] = useState("");
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--wide">
        <h1 className="course-page-title">Courses</h1>
        <p className="course-page-lede">
          Coursework across the AI engineering curriculum. Lessons link into the wiki graph.
        </p>
        <SearchBox value={query} onChange={setQuery} placeholder="Search all lessons…" />
        {query.trim().length >= 2 ? (
          <SearchResults query={query} onOpen={onOpen} />
        ) : (
          <div className="course-grid">
            {courses.map((c) => {
              const ids = lessonsOf(c).map((l) => l.id);
              const n = ids.filter((id) => done.has(id)).length;
              return (
                <button key={c.id} onClick={() => onOpen(c.id)} className="course-card">
                  <div className="course-card-title">{c.title}</div>
                  <div className="course-card-summary">{c.summary}</div>
                  <div className="course-card-meta">
                    {c.modules.length} modules · {c.lessonCount} lessons
                    {n > 0 && <span className="text-success"> · {n} done</span>}
                  </div>
                  <ProgressBar value={ids.length ? n / ids.length : 0} />
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function SearchResults({ query, onOpen }: { query: string; onOpen: (p: string) => void }) {
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  useEffect(() => {
    const ctrl = new AbortController();
    const t = setTimeout(() => {
      apiFetch(`/api/courses/search?q=${encodeURIComponent(query.trim())}`, { signal: ctrl.signal })
        .then((r) => parseJson(r, searchHitsSchema))
        .then(setHits)
        .catch(() => {});
    }, 200);
    return () => { clearTimeout(t); ctrl.abort(); };
  }, [query]);

  if (!hits) return <div className="course-status">Searching…</div>;
  if (!hits.length) return <div className="course-status">No lessons match.</div>;
  return (
    <div className="course-hits">
      {hits.map((h) => (
        <button key={h.id} onClick={() => onOpen(h.id)} className="course-nav-item course-hit">
          <div className="course-hit-where">{h.course} · {h.section}</div>
          <div className="course-hit-title">{h.title}</div>
          <div className="course-hit-snippet">{h.snippet}</div>
        </button>
      ))}
    </div>
  );
}
