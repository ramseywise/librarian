import type { CSSProperties } from "react";

interface Props {
  id: string;
  /** Cited by the answer but not read this turn (grounding.ungrounded). */
  ungrounded?: boolean;
  onOpenPage?: (id: string) => void;
}

// A page citation. Clickable when the host wires onOpenPage; inert text otherwise.
export function CitationChip({ id, ungrounded = false, onOpenPage }: Props) {
  const style = ungrounded ? { ...chipStyle, ...warnStyle } : chipStyle;
  const title = ungrounded ? `${id} (cited but not read this turn)` : id;
  if (!onOpenPage) {
    return (
      <span style={style} title={title} data-ungrounded={ungrounded || undefined}>
        {id}
      </span>
    );
  }
  return (
    <button
      type="button"
      style={{ ...style, cursor: "pointer" }}
      title={title}
      aria-label={ungrounded ? `Open page ${id} (cited but not read)` : `Open page ${id}`}
      data-ungrounded={ungrounded || undefined}
      onClick={() => onOpenPage(id)}
    >
      {id}
    </button>
  );
}

const chipStyle: CSSProperties = {
  display: "inline-block",
  margin: "0 2px",
  padding: "0 6px",
  borderRadius: 9,
  border: "1px solid #2f4f7f",
  background: "#16243a",
  color: "#8fb4e8",
  fontSize: 10,
  lineHeight: "16px",
  fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
  verticalAlign: "baseline",
  whiteSpace: "nowrap",
};

const warnStyle: CSSProperties = {
  border: "1px solid #7a6214",
  background: "#2a2310",
  color: "#c9a227",
};
