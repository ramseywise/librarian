// ---------------------------------------------------------------------------
// DashboardSuggestions — clickable query chips for the initial dashboard.
// Reads a `suggestions` string array from the A2UI data model and renders
// each as a pill. Clicking a chip sends the text directly to the chat.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useContext } from "react";
import { OnSendMessageContext } from "../core/contexts";
import { insightLabel } from "./helpers";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const DashboardSuggestions = memo(function DashboardSuggestionsInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const label = (key: string) => insightLabel(getValue, key);
  const onSendMessage = useContext(OnSendMessageContext);

  const raw = getValue("/suggestions") as string | undefined;
  const suggestions: string[] = (() => {
    if (!raw) return [];
    try { return JSON.parse(raw) as string[]; } catch { return []; }
  })();

  if (suggestions.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-slate-100">
      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">
        {label("sugg_heading")}
      </p>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((text) => (
          <button
            key={text}
            onClick={() => onSendMessage?.(text)}
            className="px-3 py-1.5 text-sm rounded-full border border-slate-200 bg-white text-slate-600 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors shadow-sm"
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
});
