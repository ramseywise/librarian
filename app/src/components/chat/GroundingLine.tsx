import type { Grounding } from "../../hooks/useChatStream";
import "./chat.css";
import type { StaleMap } from "../../hooks/useCitationStatus";
import { CitationChip } from "./CitationChip";
import {
  CHANGED_LABEL,
  MISSING_LABEL,
  SOURCES_LABEL,
  UNGROUNDED_LABEL,
  UNSUPPORTED_LABEL,
} from "./groundingLabels";

interface Props {
  grounding: Grounding;
  /** Cited pages that changed or went away after the answer (useCitationStatus). */
  stale?: StaleMap;
  onOpenPage?: (id: string) => void;
}

const NONE: StaleMap = {};

// Sources the answer cited, plus any it cited without reading in that turn (the
// backend's grounding check), any it read without the claim being found in the page (the
// backend's support check) and any whose page is no longer what the answer read.
// Each cited page is listed once, under the first row that applies. Same chips as
// the inline citations.
export function GroundingLine({ grounding, stale = NONE, onOpenPage }: Props) {
  if (grounding.cited.length === 0) {
    return <div className="grounding">no citations</div>;
  }
  const ungrounded = grounding.cited.filter((c) => grounding.ungrounded.includes(c));
  const read = grounding.cited.filter((c) => !grounding.ungrounded.includes(c));
  const changed = read.filter((c) => stale[c]?.status === "changed");
  const missing = read.filter((c) => stale[c]?.status === "missing");
  const current = read.filter((c) => !stale[c]);
  const unsupported = current.filter((c) => grounding.unsupported?.includes(c));
  const sources = current.filter((c) => !unsupported.includes(c));
  return (
    <div className="grounding">
      {sources.length > 0 && (
        <div>
          {SOURCES_LABEL}:{" "}
          {sources.map((id) => (
            <CitationChip key={id} id={id} onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
      {ungrounded.length > 0 && (
        <div className="grounding-warn">
          {UNGROUNDED_LABEL}:{" "}
          {ungrounded.map((id) => (
            <CitationChip key={id} id={id} ungrounded stale={stale[id]} onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
      {unsupported.length > 0 && (
        <div className="grounding-warn" data-testid="grounding-unsupported">
          {UNSUPPORTED_LABEL} ({unsupported.length}):{" "}
          {unsupported.map((id) => (
            <CitationChip key={id} id={id} unsupported onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
      {changed.length > 0 && (
        <div className="grounding-warn" data-testid="grounding-changed">
          {CHANGED_LABEL} ({changed.length}):{" "}
          {changed.map((id) => (
            <CitationChip key={id} id={id} stale={stale[id]} onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
      {missing.length > 0 && (
        <div className="grounding-warn" data-testid="grounding-missing">
          {MISSING_LABEL} ({missing.length}):{" "}
          {missing.map((id) => (
            <CitationChip key={id} id={id} stale={stale[id]} onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
    </div>
  );
}
