import { createContext } from "react";
import type { RelatedPages } from "./NodeDetailPanel";

/** What an open card on the canvas needs beyond its node's data. WikiGraph provides it. */
export interface NodeCard {
  related: (pageId: string) => RelatedPages[];
  /** Pages the last chat answer cited, and the question it answered. */
  cited: Set<string>;
  lastQuery: string;
  activeTags?: Set<string>;
  onClose: () => void;
  onOpenPage: (pageId: string) => void;
  onTagClick?: (tag: string) => void;
  onOpenLesson?: (lessonId: string) => void;
}

export const NodeCardContext = createContext<NodeCard | null>(null);
