// ---------------------------------------------------------------------------
// Controlled MultipleChoice override — rendered as a searchable combobox.
//
// Replaces the v0.8 library's uncontrolled <select> with a text input +
// filtered dropdown. Supports a path-bound options list and an optional
// `onCreateAction` prop: when set, a "Create '[query]'" row appears at the
// bottom of the dropdown and fires the named event via OnActionContext.
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { OnActionContext } from "../core/contexts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const ControlledMultipleChoice = memo(function ControlledMultipleChoice2({
  node,
  surfaceId,
}: {
  node: any;
  surfaceId: string;
}) {
  const { resolveString, setValue, getValue } = useA2UIComponent(node, surfaceId);
  const onAction = useContext(OnActionContext);
  const props = node.properties ?? {};
  const id = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Resolve options (literal array or path-bound JSON string)
  const optionsRaw = props.options;
  const optionsPath: string | undefined =
    optionsRaw && typeof optionsRaw === "object" && !Array.isArray(optionsRaw)
      ? (optionsRaw as { path?: string }).path
      : undefined;
  const resolvedRaw = optionsPath ? getValue(optionsPath) : optionsRaw;
  const resolvedOptions =
    typeof resolvedRaw === "string"
      ? (() => { try { return JSON.parse(resolvedRaw); } catch { return []; } })()
      : resolvedRaw;
  const options: Array<{ label: unknown; value: string }> = Array.isArray(resolvedOptions)
    ? resolvedOptions
    : [];

  const getLabel = (o: { label: unknown; value: string }): string =>
    typeof o.label === "string" ? o.label
    : typeof (o.label as { literalString?: string })?.literalString === "string"
      ? (o.label as { literalString: string }).literalString
      : String(o.label ?? "");

  const selectionsPath: string | undefined = props.selections?.path;
  const rawSelectionsDebug = selectionsPath ? getValue(selectionsPath) : undefined;
  console.log("[ChoicePicker] render — selectionsPath:", selectionsPath, "| raw:", rawSelectionsDebug, "| options count:", options.length);
  const label = resolveString(props.description) ?? "Select";
  const placeholder = `Select ${label.toLowerCase()}`;
  const onCreateAction: string | undefined = props.onCreateAction;

  // Current selection value → resolved label
  const rawSelections = selectionsPath ? getValue(selectionsPath) : undefined;
  const currentValue: string = Array.isArray(rawSelections)
    ? String(rawSelections[0] ?? "")
    : typeof rawSelections === "string" ? rawSelections : "";
  const currentLabel = (() => { const o = options.find((o) => o.value === currentValue); return o ? getLabel(o) : ""; })();

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  // Portal dropdown position — tracked via getBoundingClientRect so it escapes overflow:hidden cards
  const [dropPos, setDropPos] = useState({ top: 0, left: 0, width: 0 });

  const updatePos = useCallback(() => {
    if (inputRef.current) {
      const r = inputRef.current.getBoundingClientRect();
      setDropPos({ top: r.bottom + 4, left: r.left, width: r.width });
    }
  }, []);

  const openDropdown = useCallback(() => {
    updatePos();
    setOpen(true);
    setQuery("");
  }, [updatePos]);

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

  // Close on outside click (checks both input and portal dropdown)
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      const t = e.target as Node;
      if (!inputRef.current?.contains(t) && !dropdownRef.current?.contains(t)) {
        setOpen(false);
        setQuery("");
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const filtered = query
    ? options.filter((o) => getLabel(o).toLowerCase().includes(query.toLowerCase()))
    : options;
  const exactMatch = options.some((o) => getLabel(o).toLowerCase() === query.toLowerCase());

  const handleSelect = useCallback((value: string) => {
    if (selectionsPath) setValue(selectionsPath, [value]);
    setOpen(false);
    setQuery("");
  }, [selectionsPath, setValue]);

  const handleCreate = useCallback(() => {
    if (onAction && onCreateAction && query) {
      onAction({
        userAction: {
          name: onCreateAction,
          sourceComponentId: node.id,
          surfaceId,
          context: { name: query },
        },
      });
    }
    setOpen(false);
    setQuery("");
  }, [onAction, onCreateAction, query, node.id, surfaceId]);

  const hostStyle = node.weight !== undefined ? ({ "--weight": node.weight } as React.CSSProperties) : {};

  const dropdown = open ? createPortal(
    <div
      ref={dropdownRef}
      style={{ position: "fixed", top: dropPos.top, left: dropPos.left, width: dropPos.width, zIndex: 9999 }}
      className="max-h-60 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg"
    >
      {filtered.length === 0 && (
        <div className="px-3 py-2 text-sm text-slate-400">No contacts found.</div>
      )}
      {filtered.map((option) => (
        <div
          key={option.value}
          className="px-3 py-2 text-sm cursor-pointer hover:bg-slate-100"
          onMouseDown={(e) => { e.preventDefault(); handleSelect(option.value); }}
        >
          {getLabel(option)}
        </div>
      ))}
      {onCreateAction && query && !exactMatch && (
        <>
          <div className="border-t border-slate-100" />
          <div
            className="px-3 py-2 text-sm cursor-pointer hover:bg-slate-50 text-slate-600 flex items-center gap-2"
            onMouseDown={(e) => { e.preventDefault(); handleCreate(); }}
          >
            <span className="text-slate-400 text-base leading-none">⊕</span>
            Create &quot;{query}&quot;
          </div>
        </>
      )}
    </div>,
    document.body
  ) : null;

  return (
    <div className="a2ui-multiplechoice" style={hostStyle}>
      <div className="w-full flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 hover:border-slate-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-400 focus-within:ring-offset-0">
        <input
          ref={inputRef}
          id={id}
          type="text"
          autoComplete="off"
          placeholder={placeholder}
          className="flex-1 bg-transparent outline-none text-sm text-slate-800 placeholder:text-slate-400 font-medium"
          value={open ? query : currentLabel}
          onChange={(e) => { setQuery(e.target.value); if (!open) openDropdown(); }}
          onFocus={openDropdown}
        />
        <span className="pointer-events-none text-slate-400 text-xs shrink-0">▾</span>
      </div>
      {dropdown}
    </div>
  );
});
