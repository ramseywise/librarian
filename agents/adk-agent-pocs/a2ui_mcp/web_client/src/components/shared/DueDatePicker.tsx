// ---------------------------------------------------------------------------
// DueDatePicker — custom component for selecting a payment term (Net X days).
// Shows preset options (On receipt, Net 15/30/60/90) and a custom "Net... X days"
// spinner. Calculates the actual ISO date from today + days and writes it to
// the bound data model path.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { createPortal } from "react-dom";

const NET_PRESETS = [
  { label: "On receipt", days: 0 },
  { label: "Net 15", days: 15 },
  { label: "Net 30", days: 30 },
  { label: "Net 60", days: 60 },
  { label: "Net 90", days: 90 },
];

function addDays(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().split("T")[0];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const DueDatePicker = memo(function DueDatePicker2({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue, setValue, resolveString } = useA2UIComponent(node, surfaceId);
  const props = node.properties ?? {};

  // Accept `value` (v0.9) or `text` (translated TextField convention)
  const valuePath: string | undefined =
    (props.value as { path?: string })?.path ??
    (props.text as { path?: string })?.path;
  const fieldLabel = resolveString(props.label) ?? resolveString(props.description) ?? "Due date";

  const [selectedDays, setSelectedDays] = useState(7);
  const [customDays, setCustomDays] = useState(7);
  const [showCustom, setShowCustom] = useState(false);
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [dropPos, setDropPos] = useState({ top: 0, left: 0, width: 0 });

  // Write initial Net 7 date on first mount
  useEffect(() => {
    if (valuePath && !getValue(valuePath)) setValue(valuePath, addDays(7));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updatePos = useCallback(() => {
    if (triggerRef.current) {
      const r = triggerRef.current.getBoundingClientRect();
      setDropPos({ top: r.bottom + 4, left: r.left, width: Math.max(r.width, 240) });
    }
  }, []);

  // Reposition on scroll/resize while open
  useEffect(() => {
    if (!open) return;
    window.addEventListener("scroll", updatePos, true);
    window.addEventListener("resize", updatePos);
    return () => {
      window.removeEventListener("scroll", updatePos, true);
      window.removeEventListener("resize", updatePos);
    };
  }, [open, updatePos]);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      const t = e.target as Node;
      if (!triggerRef.current?.contains(t) && !dropdownRef.current?.contains(t)) {
        setOpen(false);
        setShowCustom(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const handleSelect = useCallback((days: number) => {
    setSelectedDays(days);
    if (valuePath) setValue(valuePath, addDays(days));
    setOpen(false);
    setShowCustom(false);
  }, [valuePath, setValue]);

  const selectionLabel = NET_PRESETS.find((p) => p.days === selectedDays)?.label ?? `Net ${selectedDays}`;

  const dropdown = open ? createPortal(
    <div
      ref={dropdownRef}
      style={{ position: "fixed", top: dropPos.top, left: dropPos.left, width: dropPos.width, zIndex: 9999 }}
      className="rounded-xl border border-slate-200 bg-white shadow-lg overflow-hidden"
    >
      {NET_PRESETS.map((preset) => (
        <div
          key={preset.days}
          className={`px-4 py-3 text-sm cursor-pointer hover:bg-slate-50 ${selectedDays === preset.days ? "font-semibold text-slate-900" : "text-slate-700"}`}
          onMouseDown={(e) => { e.preventDefault(); handleSelect(preset.days); }}
        >
          {preset.label}
        </div>
      ))}
      {/* Custom "Net... X days" row */}
      <div className={`border-t border-slate-100 px-4 py-3 ${showCustom ? "bg-slate-50" : ""}`}>
        {!showCustom ? (
          <div
            className="text-sm text-slate-500 cursor-pointer hover:text-slate-700"
            onMouseDown={(e) => { e.preventDefault(); setShowCustom(true); }}
          >
            Net…
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-500">Net…</span>
            <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2 py-1">
              <input
                type="number"
                min={1}
                max={365}
                className="w-10 text-sm text-right outline-none tabular-nums"
                value={customDays}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setCustomDays(Math.max(1, parseInt(e.target.value) || 1))
                }
              />
              <span className="text-sm text-slate-500 ml-1">days</span>
              <div className="flex flex-col ml-1">
                <button
                  className="text-slate-400 hover:text-slate-700 text-[9px] leading-tight"
                  onMouseDown={(e) => { e.preventDefault(); setCustomDays((d) => d + 1); }}
                >▲</button>
                <button
                  className="text-slate-400 hover:text-slate-700 text-[9px] leading-tight"
                  onMouseDown={(e) => { e.preventDefault(); setCustomDays((d) => Math.max(1, d - 1)); }}
                >▼</button>
              </div>
            </div>
            <button
              className="text-slate-400 hover:text-slate-700 text-lg leading-none"
              onMouseDown={(e) => { e.preventDefault(); handleSelect(customDays); }}
            >✓</button>
          </div>
        )}
      </div>
    </div>,
    document.body
  ) : null;

  const hostStyle = node.weight !== undefined ? ({ "--weight": node.weight } as React.CSSProperties) : {};

  return (
    <div className="w-full flex items-center justify-end gap-3 py-1" style={hostStyle}>
      <span className="text-sm text-slate-500 w-20 text-right whitespace-nowrap">{fieldLabel}</span>
      <button
        ref={triggerRef}
        type="button"
        className="w-48 flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 hover:border-slate-300 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-400 focus:ring-offset-0"
        onClick={() => { updatePos(); setOpen((o) => !o); }}
      >
        <span>{selectionLabel}</span>
        <span className="text-slate-400 text-xs">▾</span>
      </button>
      {dropdown}
    </div>
  );
});
