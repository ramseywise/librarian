import { useEffect, useState } from "react";
import { apiJson } from "../../utils/api";
import { deleteFeedback, type MyFeedback as Row } from "../../utils/feedback";

const label = (r: Row) => (r.rating === 1 ? "👍" : r.rating === -1 ? "👎" : "");

/** The caller's own ratings, reports and notes, each deletable. */
export function MyFeedback() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiJson<Row[]>("/api/feedback/mine")
      .then((r) => !cancelled && setRows(r))
      .catch((e: Error) => !cancelled && (setError(e.message), setRows([])));
    return () => {
      cancelled = true;
    };
  }, []);

  async function remove(row: Row) {
    try {
      await deleteFeedback(row.id);
      setRows((rs) => (rs ?? []).filter((r) => r.id !== row.id));
      setError(null);
    } catch (e) {
      setError(`Could not delete: ${(e as Error).message}`);
    }
  }

  return (
    <section aria-label="My feedback">
      <h2>My feedback</h2>
      {error && <p className="account-error" role="alert">{error}</p>}
      {rows === null ? (
        <p>Loading…</p>
      ) : rows.length === 0 ? (
        <p className="account-hint">You have not sent any feedback.</p>
      ) : (
        <table className="account-table">
          <thead>
            <tr><th>When</th><th>Kind</th><th>Target</th><th>Rating</th><th>Note</th><th><span className="sr-only">Delete</span></th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.ts).toLocaleDateString()}</td>
                <td>{r.kind}</td>
                <td>{r.target}</td>
                <td>{label(r)}</td>
                <td className="account-note">{r.body ?? ""}</td>
                <td>
                  <button type="button" className="round-btn" aria-label={`Delete my ${r.kind} feedback on ${r.target}`} onClick={() => void remove(r)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
