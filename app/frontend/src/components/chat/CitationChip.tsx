interface Props {
  id: string;
  /** Cited by the answer but not read this turn (grounding.ungrounded). */
  ungrounded?: boolean;
  onOpenPage?: (id: string) => void;
}

// A page citation. Clickable when the host wires onOpenPage; inert text otherwise.
export function CitationChip({ id, ungrounded = false, onOpenPage }: Props) {
  const className = ungrounded ? "citation-chip citation-chip--warn" : "citation-chip";
  const title = ungrounded ? `${id} (cited but not read this turn)` : id;
  if (!onOpenPage) {
    return (
      <span className={className} title={title} data-ungrounded={ungrounded || undefined}>
        {id}
      </span>
    );
  }
  return (
    <button
      type="button"
      className={className}
      title={title}
      aria-label={ungrounded ? `Open page ${id} (cited but not read)` : `Open page ${id}`}
      data-ungrounded={ungrounded || undefined}
      onClick={() => onOpenPage(id)}
    >
      {id}
    </button>
  );
}
