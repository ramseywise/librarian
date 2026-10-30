import type { CSSProperties } from "react";
import type { Grounding } from "../../hooks/useChatStream";
import { CitationChip } from "./CitationChip";

interface Props {
  grounding: Grounding;
  onOpenPage?: (id: string) => void;
}

// Sources the answer cited, plus any it cited without reading in that turn (the
// backend's grounding check). Same chips as the inline citations.
export function GroundingLine({ grounding, onOpenPage }: Props) {
  if (grounding.cited.length === 0) {
    return <div style={groundingStyle}>no citations</div>;
  }
  const grounded = grounding.cited.filter((c) => !grounding.ungrounded.includes(c));
  return (
    <div style={groundingStyle}>
      {grounded.length > 0 && (
        <div>
          sources:{" "}
          {grounded.map((id) => (
            <CitationChip key={id} id={id} onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
      {grounding.ungrounded.length > 0 && (
        <div style={{ color: "#c9a227", marginTop: 2 }}>
          cited but not read:{" "}
          {grounding.ungrounded.map((id) => (
            <CitationChip key={id} id={id} ungrounded onOpenPage={onOpenPage} />
          ))}
        </div>
      )}
    </div>
  );
}

const groundingStyle: CSSProperties = { marginTop: 6, fontSize: 10, color: "#666" };
