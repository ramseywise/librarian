/** A failed load, with the way to try again. `what` names the thing that did not load. */
export function ResourceNotice({ what, error, onRetry }: { what: string; error: string; onRetry: () => void }) {
  return (
    <div className="resource-notice" role="alert">
      <span>
        {what} did not load: {error}
      </span>
      <button type="button" className="pill-btn" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}
