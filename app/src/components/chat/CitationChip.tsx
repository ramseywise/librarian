import type { StaleCitation } from "../../hooks/useCitationStatus";
import { CHANGED_LABEL, MISSING_LABEL, UNSUPPORTED_LABEL } from "./groundingLabels";

interface Props {
  id: string;
  /** Cited by the answer but not read this turn (grounding.ungrounded). */
  ungrounded?: boolean;
  /** Read this turn, but the claim beside the citation was not found in the page. */
  unsupported?: boolean;
  /** The page changed or went away after the answer was written. */
  stale?: StaleCitation;
  onOpenPage?: (id: string) => void;
}

// A page citation. Clickable when the host wires onOpenPage; inert text otherwise, and
// always inert once its page no longer exists. A renamed page opens under its new id.
export function CitationChip({ id, ungrounded = false, unsupported = false, stale, onOpenPage }: Props) {
  const missing = stale?.status === "missing";
  const warn = ungrounded || unsupported || !!stale;
  const className = [
    "citation-chip",
    warn && "citation-chip--warn",
    missing && "citation-chip--missing",
  ]
    .filter(Boolean)
    .join(" ");
  const why = stale
    ? stale.status === "missing"
      ? MISSING_LABEL
      : stale.now
        ? `${CHANGED_LABEL}; now ${stale.now}`
        : CHANGED_LABEL
    : ungrounded
      ? "cited but not read this turn"
      : unsupported
        ? UNSUPPORTED_LABEL
        : null;
  const title = why ? `${id} (${why})` : id;
  if (!onOpenPage || missing) {
    return (
      <span
        className={className}
        title={title}
        data-ungrounded={ungrounded || undefined}
        data-unsupported={unsupported || undefined}
        data-stale={stale?.status}
      >
        {id}
      </span>
    );
  }
  const label = stale
    ? `Open page ${id} (${CHANGED_LABEL})`
    : ungrounded
      ? `Open page ${id} (cited but not read)`
      : unsupported
        ? `Open page ${id} (${UNSUPPORTED_LABEL})`
        : `Open page ${id}`;
  return (
    <button
      type="button"
      className={className}
      title={title}
      aria-label={label}
      data-ungrounded={ungrounded || undefined}
      data-unsupported={unsupported || undefined}
      data-stale={stale?.status}
      onClick={() => onOpenPage(stale?.now ?? id)}
    >
      {id}
    </button>
  );
}
