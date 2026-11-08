import { useState } from "react";
import { deleteFeedback, MAX_NOTE, sendFeedback } from "../../utils/feedback";
import "./feedback.css";

type Rating = 1 | -1;

/** Thumbs under a finished chat answer. A down-rating offers a note; errors show inline. */
export function AnswerRating({ answerId }: { answerId: string }) {
  const [rating, setRating] = useState<Rating | null>(null);
  const [rowId, setRowId] = useState<string | null>(null);
  const [noteOpen, setNoteOpen] = useState(false);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function send(r: Rating, body?: string) {
    setBusy(true);
    setError(null);
    try {
      const id = await sendFeedback({ kind: "answer", target: answerId, rating: r, ...(body ? { body } : {}) });
      setRating(r);
      setRowId(id);
      setStatus(body ? "Thanks, note sent." : "Thanks for the feedback.");
      return true;
    } catch (e) {
      setError(`Could not send feedback: ${(e as Error).message}`);
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function rate(r: Rating) {
    if (busy) return;
    if (rating === r) {
      // Toggle off: remove the row we created.
      if (!rowId) return;
      setBusy(true);
      setError(null);
      try {
        await deleteFeedback(rowId);
        setRating(null);
        setRowId(null);
        setNoteOpen(false);
        setStatus(null);
      } catch (e) {
        setError(`Could not remove feedback: ${(e as Error).message}`);
      } finally {
        setBusy(false);
      }
      return;
    }
    const ok = await send(r);
    if (ok) setNoteOpen(r === -1);
  }

  async function sendNote() {
    const body = note.trim();
    if (!body || rating !== -1) return;
    if (await send(-1, body)) {
      setNote("");
      setNoteOpen(false);
    }
  }

  return (
    <div className="answer-rating">
      <div className="answer-rating-row">
        <button type="button" className="rate-btn" aria-pressed={rating === 1} aria-label="Good answer" title="Good answer" disabled={busy} onClick={() => void rate(1)}>
          👍
        </button>
        <button type="button" className="rate-btn" aria-pressed={rating === -1} aria-label="Bad answer" title="Bad answer" disabled={busy} onClick={() => void rate(-1)}>
          👎
        </button>
        {rating !== null && !noteOpen && (
          <button type="button" className="link-btn feedback-link" onClick={() => setNoteOpen(true)}>
            add a note
          </button>
        )}
        {status && !error && <span className="feedback-status" role="status">{status}</span>}
      </div>
      {noteOpen && rating === -1 && (
        <div className="feedback-form">
          <textarea
            aria-label="Note on this answer"
            className="feedback-textarea"
            rows={2}
            maxLength={MAX_NOTE}
            placeholder="What was wrong or missing?"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <button type="button" className="round-btn" disabled={busy || !note.trim()} onClick={() => void sendNote()}>
            Send note
          </button>
        </div>
      )}
      {error && <div className="feedback-error" role="alert">{error}</div>}
    </div>
  );
}
