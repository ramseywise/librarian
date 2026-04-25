import { A2UIProvider, A2UIRenderer, ComponentRegistry, useA2UI } from "@a2ui/react";
import { Component, useCallback, useEffect, useRef, type ReactNode } from "react";

import { OnActionContext, OnSendMessageContext } from "./core/contexts";
import { resolveFetches } from "./core/fetch-resolver";
import { isV09Batch, translateV09ToV08 } from "./core/v09-to-v08";

import * as Shared from "./shared";
import * as Invoice from "./invoice";
import * as Customer from "./customer";
import * as Product from "./product";
import * as Insights from "./insights";

// ---------------------------------------------------------------------------
// All skill component registrations — add new skill folders here.
// ---------------------------------------------------------------------------

const ALL_COMPONENTS = [
  ...Shared.components,
  ...Invoice.components,
  ...Customer.components,
  ...Product.components,
  ...Insights.components,
];

// ---------------------------------------------------------------------------
// Per-surface error boundary so one bad surface doesn't blank the whole panel.
// ---------------------------------------------------------------------------

class SurfaceErrorBoundary extends Component<
  { surfaceId: string; children: ReactNode },
  { hasError: boolean; error: string }
> {
  constructor(props: { surfaceId: string; children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: "" };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-sm text-red-600 bg-red-50 rounded-xl border border-red-200">
          Surface &quot;{this.props.surfaceId}&quot; failed to render:{" "}
          {this.state.error}
        </div>
      );
    }
    return this.props.children;
  }
}

// ---------------------------------------------------------------------------
// SurfaceContent — uses useA2UI() and renders surfaces.
// Kept separate from SurfaceRenderer so that SurfaceRenderer can own the
// A2UIProvider (the hook must be called inside the provider tree).
// ---------------------------------------------------------------------------

// Surfaces that use incremental (merge) data model updates from the LLM.
// For these, each dataModelUpdate ADDS to the existing state rather than replacing it.
// Other surfaces (suggestions, main) always get full replacements so no merging needed.
const MERGE_SURFACES = new Set(["detail"]);

type V08Contents = { key: string; valueString?: string; valueNumber?: number; valueBoolean?: boolean };

/**
 * Apply v0.8 messages against the accumulator so that partial dataModelUpdate
 * messages for MERGE_SURFACES are merged with existing state instead of replacing it.
 * deleteSurface clears the accumulated state so a re-opened form starts fresh.
 */
function applyMerge(
  messages: unknown[],
  acc: Map<string, Record<string, V08Contents>>
): unknown[] {
  return messages.map((msg) => {
    const m = msg as Record<string, unknown>;
    if (m.deleteSurface) {
      const { surfaceId } = m.deleteSurface as { surfaceId: string };
      acc.delete(surfaceId);
      return msg;
    }
    if (m.dataModelUpdate) {
      const { surfaceId, contents } = m.dataModelUpdate as { surfaceId: string; contents: V08Contents[] };
      if (!MERGE_SURFACES.has(surfaceId)) return msg;
      const existing = acc.get(surfaceId) ?? {};
      for (const c of contents) existing[c.key] = c;
      acc.set(surfaceId, existing);
      return { dataModelUpdate: { surfaceId, contents: Object.values(existing) } };
    }
    return msg;
  });
}

function SurfaceContent({
  pendingMessages,
  onConsumed,
  onProcessMessages,
}: {
  pendingMessages: unknown[][];
  onConsumed: () => void;
  onProcessMessages: (fn: (msgs: unknown) => void) => void;
}) {
  const { processMessages, getSurfaces } = useA2UI();
  const dataModelAcc = useRef<Map<string, Record<string, V08Contents>>>(new Map());

  // Register all skill components once on mount.
  useEffect(() => {
    const registry = ComponentRegistry.getInstance();
    ALL_COMPONENTS.forEach(({ name, component }) =>
      registry.register(name, { component })
    );
  }, []);

  // Expose processMessages to the parent SurfaceRenderer so its action handler
  // can call it without being inside the provider tree.
  useEffect(() => {
    onProcessMessages(processMessages as (msgs: unknown) => void);
  }, [processMessages, onProcessMessages]);

  // Process new batches then clear the queue so old batches aren't replayed.
  // Batches may contain $fetch sentinels that are resolved against the Billy
  // REST API before being handed to processMessages.
  useEffect(() => {
    if (pendingMessages.length === 0) return;
    let cancelled = false;
    (async () => {
      for (const batch of pendingMessages) {
        try {
          const resolved = await resolveFetches(batch);
          if (cancelled) return;
          const v08 = isV09Batch(resolved) ? translateV09ToV08(resolved) : resolved;
          const merged = applyMerge(v08, dataModelAcc.current);
          console.log("[SurfacePanel] processMessages:", JSON.stringify(merged));
          processMessages(merged as Parameters<typeof processMessages>[0]);
        } catch (err) {
          console.error("[A2UI] processMessages error:", err);
        }
      }
      if (!cancelled) onConsumed();
    })();
    return () => { cancelled = true; };
  }, [pendingMessages, processMessages, onConsumed]);

  const surfaces = getSurfaces();
  // Only render surfaces that have been fully initialized (beginRendering received).
  // Surfaces created by a dataModelUpdate alone have rootComponentId === null and
  // would render as an empty white card.
  const surfaceIds = Array.from(surfaces.entries())
    .filter(([id, s]) => id !== "suggestions" && s.rootComponentId !== null)
    .map(([id]) => id);

  return (
    <div className="flex flex-col min-h-full p-4 gap-4">
      {surfaceIds.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-slate-400 text-sm text-center">
            UI surfaces will appear here as you interact with Billy.
          </p>
        </div>
      ) : (
        surfaceIds.map((id) => (
          <SurfaceErrorBoundary key={id} surfaceId={id}>
            <div className="relative bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-6">
              {id !== "suggestions" && (
                <button
                  onClick={() => processMessages([{ deleteSurface: { surfaceId: id } }] as Parameters<typeof processMessages>[0])}
                  className="absolute top-3 right-3 z-10 flex items-center justify-center w-6 h-6 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors text-lg leading-none"
                  aria-label="Close panel"
                >
                  ×
                </button>
              )}
              <A2UIRenderer surfaceId={id} />
            </div>
          </SurfaceErrorBoundary>
        ))
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// SurfaceRenderer — owns A2UIProvider and context providers.
// ---------------------------------------------------------------------------

interface Props {
  pendingMessages: unknown[][];
  onAction: (event: unknown) => void;
  onConsumed: () => void;
  onSendMessage?: (text: string) => void;
}

function SurfaceRenderer({ pendingMessages, onAction, onConsumed, onSendMessage }: Props) {
  const handleProcessMessages = useCallback((fn: (msgs: unknown) => void) => {
    void fn;
  }, []);

  return (
    <OnSendMessageContext.Provider value={onSendMessage ?? null}>
      <OnActionContext.Provider value={onAction}>
        <A2UIProvider onAction={onAction}>
          <SurfaceContent
            pendingMessages={pendingMessages}
            onConsumed={onConsumed}
            onProcessMessages={handleProcessMessages}
          />
        </A2UIProvider>
      </OnActionContext.Provider>
    </OnSendMessageContext.Provider>
  );
}

export function SurfacePanel({ pendingMessages, onAction, onConsumed, onSendMessage }: Props) {
  return (
    <SurfaceRenderer
      pendingMessages={pendingMessages}
      onAction={onAction}
      onConsumed={onConsumed}
      onSendMessage={onSendMessage}
    />
  );
}
