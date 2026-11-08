import { useEffect, useState } from "react";
import { apiJson } from "../../utils/api";

interface Row {
  target: string;
  count?: number;
  notes?: string[];
  misses?: number;
  miss_rate?: number;
  read?: number;
  cited?: number;
  ungrounded?: number;
}
type Summary = Partial<Record<string, Row[]>>;

interface Column { head: string; cell: (r: Row) => string }

const pct = (r: Row) => (typeof r.miss_rate === "number" ? `${Math.round(r.miss_rate * 100)}%` : "");
const num = (n: number | undefined) => (typeof n === "number" ? String(n) : "");

const LISTS: { key: string; title: string; cols: Column[] }[] = [
  { key: "answers_down", title: "Answers rated down", cols: [{ head: "Answer", cell: (r) => r.target }, { head: "Ratings", cell: (r) => num(r.count) }] },
  { key: "pages_reported", title: "Pages reported", cols: [{ head: "Page", cell: (r) => r.target }, { head: "Reports", cell: (r) => num(r.count) }] },
  { key: "lessons_reported", title: "Lessons reported", cols: [{ head: "Lesson", cell: (r) => r.target }, { head: "Reports", cell: (r) => num(r.count) }] },
  { key: "unanswered", title: "Unanswered queries", cols: [{ head: "Query", cell: (r) => r.target }, { head: "Times", cell: (r) => num(r.count) }] },
  {
    key: "lesson_miss_rates",
    title: "Lesson miss rates",
    cols: [
      { head: "Lesson", cell: (r) => r.target },
      { head: "Attempts", cell: (r) => num(r.count) },
      { head: "Misses", cell: (r) => num(r.misses) },
      { head: "Rate", cell: pct },
    ],
  },
  {
    key: "page_reads",
    title: "Page reads",
    cols: [
      { head: "Page", cell: (r) => r.target },
      { head: "Read", cell: (r) => num(r.read) },
      { head: "Cited", cell: (r) => num(r.cited) },
      { head: "Ungrounded", cell: (r) => num(r.ungrounded) },
    ],
  },
];

/** Top ten of each reader-feedback signal. Fields beyond the ones used are ignored. */
export function FeedbackSummaryView() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiJson<Summary>("/api/admin/feedback/summary")
      .then((s) => !cancelled && setSummary(s ?? {}))
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="study-block" aria-label="Reader feedback">
      <h2 className="study-heading">Reader feedback</h2>
      {error && <p className="account-error" role="alert">Could not load reader feedback: {error}</p>}
      {!error && !summary && <p>Loading…</p>}
      {summary &&
        LISTS.map(({ key, title, cols }) => {
          const raw = summary[key];
          const rows = Array.isArray(raw) ? raw.filter((r) => r && typeof r.target === "string") : [];
          return (
            <div key={key} role="group" aria-label={title}>
              <h3 className="study-subheading">{title}</h3>
              {rows.length === 0 ? (
                <p className="account-hint">none yet</p>
              ) : (
                <table className="account-table">
                  <thead>
                    <tr>{cols.map((c) => <th key={c.head}>{c.head}</th>)}</tr>
                  </thead>
                  <tbody>
                    {rows.map((r, i) => (
                      <FeedbackRow key={`${r.target}-${i}`} row={r} cols={cols} />
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          );
        })}
    </section>
  );
}

function FeedbackRow({ row, cols }: { row: Row; cols: Column[] }) {
  const notes = Array.isArray(row.notes) ? row.notes.filter((n) => typeof n === "string" && n) : [];
  return (
    <>
      <tr>{cols.map((c) => <td key={c.head}>{c.cell(row)}</td>)}</tr>
      {notes.length > 0 && (
        <tr>
          <td colSpan={cols.length} className="feedback-notes">
            <ul>{notes.map((n, i) => <li key={i}>{n}</li>)}</ul>
          </td>
        </tr>
      )}
    </>
  );
}
