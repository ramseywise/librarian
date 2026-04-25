// ---------------------------------------------------------------------------
// ProductForm — create/edit product form matching the "Create item" dialog.
// Data model: { mode: "create"|"edit", form: { id, name, description,
// unitPrice, priceId, productNo, isArchived } }
// Fires: submit_create_product | submit_edit_product | cancel_product
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useContext, useState } from "react";
import { OnActionContext } from "../core/contexts";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const ProductForm = memo(function ProductFormInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const onAction = useContext(OnActionContext);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const L = (path: string, fallback: string) => (getValue(path) as string) || fallback;

  const mode = (getValue("/mode") as string) || "create";
  const [name, setName] = useState((getValue("/form/name") as string) || "");
  const [description, setDescription] = useState((getValue("/form/description") as string) || "");
  const [unitPrice, setUnitPrice] = useState((getValue("/form/unitPrice") as string) || "");
  const [productNo, setProductNo] = useState((getValue("/form/productNo") as string) || "");
  const [isArchived, setIsArchived] = useState(Boolean(getValue("/form/isArchived")));
  const id = (getValue("/form/id") as string) || "";
  const priceId = (getValue("/form/priceId") as string) || "";

  const fireEvent = useCallback((evName: string, context: Record<string, unknown>) => {
    if (!onAction) return;
    onAction({ userAction: { name: evName, sourceComponentId: node.id, surfaceId, context } });
  }, [onAction, node.id, surfaceId]);

  const handleSubmit = useCallback(() => {
    if (mode === "edit") {
      fireEvent("submit_edit_product", { id, priceId, name, description, unitPrice, productNo, isArchived });
    } else {
      fireEvent("submit_create_product", { name, description, unitPrice });
    }
  }, [mode, id, priceId, name, description, unitPrice, productNo, isArchived, fireEvent]);

  const inputCls = "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300";
  const labelCls = "block text-xs text-slate-500 mb-1";

  const canSubmit = name.trim() !== "" && unitPrice.trim() !== "";

  const title = mode === "edit" ? L("/labels/title_edit", "Edit item") : L("/labels/title_create", "Create item");
  const submitLabel = mode === "edit" ? L("/labels/submit_edit", "Save changes") : L("/labels/submit_create", "Create item");

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 w-full max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-slate-100">
        <h2 className="text-xl font-bold text-slate-900">{title}</h2>
        <button
          onClick={() => fireEvent("cancel_product", {})}
          className="text-slate-400 hover:text-slate-600 transition-colors text-xl leading-none"
          aria-label="Close"
        >✕</button>
      </div>

      {/* Body — 2-column layout */}
      <div className="px-6 py-5 grid grid-cols-2 gap-6">
        {/* Left column */}
        <div className="space-y-4">
          <div>
            <label className={labelCls}>{L("/labels/name_label", "Name of the product or service *")}</label>
            <input
              className={inputCls}
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder={L("/labels/name_placeholder", "E.g. web design services / Acme red hammer")}
            />
          </div>
          <div>
            <label className={labelCls}>{L("/labels/description", "Description")}</label>
            <textarea
              className={`${inputCls} resize-none`}
              rows={4}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={L("/labels/description_placeholder", "None")}
            />
            <p className="text-xs text-slate-400 mt-1">{L("/labels/description_hint", "Automatically inserted as default for new invoices")}</p>
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className={labelCls.replace("mb-1", "")}>{L("/labels/unit_price", "Unit price *")}</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                className={`${inputCls} flex-1`}
                value={unitPrice}
                onChange={e => setUnitPrice(e.target.value)}
                placeholder={L("/labels/unit_price_placeholder", "Unit price")}
              />
              <span className="text-sm font-medium text-slate-700 border border-slate-200 rounded-lg px-3 py-2 bg-white whitespace-nowrap">DKK</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">{L("/labels/excl_vat", "Excl. VAT")}</p>
          </div>
          <div>
            <label className={labelCls}>{L("/labels/sku", "SKU / Item code")}</label>
            <input
              className={inputCls}
              value={productNo}
              onChange={e => setProductNo(e.target.value)}
              placeholder={L("/labels/sku_placeholder", "None")}
            />
            <p className="text-xs text-slate-400 mt-1">{L("/labels/sku_hint", "Only seen by you")}</p>
          </div>
          {mode === "edit" && (
            <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer select-none">
              <input
                type="checkbox"
                className="w-4 h-4 rounded border-slate-300 accent-slate-800"
                checked={isArchived}
                onChange={e => setIsArchived(e.target.checked)}
              />
              {L("/labels/archived", "Archived (hide from lists)")}
            </label>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-end gap-3 px-6 pb-6">
        <button
          onClick={() => fireEvent("cancel_product", {})}
          className="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          {L("/labels/cancel", "Cancel")}
        </button>
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {submitLabel}
        </button>
      </div>
    </div>
  );
});
