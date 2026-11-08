import { useId, useState } from "react";
import { ApiError } from "../../utils/api";
import { MAX_NOTE, sendFeedback, type FeedbackKind } from "../../utils/feedback";
import "./feedback.css";

interface Props {
  kind: Extract<FeedbackKind, "page" | "lesson">;
  target: string;
}

/** Flag icon that opens a small report/suggest form for a wiki page or a lesson. */
export function ReportButton({ kind, target }: Props) {
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const id = useId();
  const noun = kind === "page" ? "page" : "lesson";

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const body = note.trim();
    if (!body || busy) return;
    setBusy(true);
    setError(null);
    try {
      await sendFeedback({ kind, target, body });
      setSent(true);
      setNote("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the API");
    } finally {
      setBusy(false);
    }
  }

  function toggle() {
    setOpen((o) => !o);
    setSent(false);
    setError(null);
  }

  return (
    <div className="report">
      <button
        type="button"
        className="report-btn"
        aria-expanded={open}
        aria-label={`Report or suggest a change to this ${noun}`}
        title={`Report or suggest a change to this ${noun}`}
        onClick={toggle}
      >
        <span aria-hidden="true">⚑</span> Report
      </button>
      {open && (
        <form className="feedback-form feedback-form--stack" onSubmit={(e) => void submit(e)}>
          {sent ? (
            <div className="feedback-status" role="status">Thanks, your note was sent.</div>
          ) : (
            <>
              <label htmlFor={id} className="feedback-label">What should change on this {noun}?</label>
              <textarea
                id={id}
                className="feedback-textarea"
                rows={3}
                required
                maxLength={MAX_NOTE}
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
              <div className="feedback-foot">
                <span className="feedback-count" aria-live="off">{note.length}/{MAX_NOTE}</span>
                <button type="submit" className="round-btn" disabled={busy || !note.trim()}>Send</button>
              </div>
            </>
          )}
          {error && <div className="feedback-error" role="alert">{error}</div>}
        </form>
      )}
    </div>
  );
}
