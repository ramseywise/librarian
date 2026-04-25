// ---------------------------------------------------------------------------
// CustomerForm — tabbed create/edit contact form (Company | Individual).
// Data model: { mode: "create"|"edit", form: { id, name, type, country,
// registrationNo, phone, email, street, city, zipcode } }
// Fires: submit_create_customer | submit_edit_customer | cancel
// ---------------------------------------------------------------------------

import { useA2UIComponent } from "@a2ui/react";
import { memo, useCallback, useState } from "react";
import { OnActionContext } from "../core/contexts";
import { useContext } from "react";

const COUNTRIES = Object.entries({
  DK: "Denmark", SE: "Sweden", NO: "Norway", DE: "Germany",
  GB: "United Kingdom", US: "United States", FI: "Finland", NL: "Netherlands",
  FR: "France", IT: "Italy", ES: "Spain", PL: "Poland",
}).sort((a, b) => a[1].localeCompare(b[1]));

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const CustomerForm = memo(function CustomerFormInner({ node, surfaceId }: { node: any; surfaceId: string }) {
  const { getValue } = useA2UIComponent(node, surfaceId);
  const onAction = useContext(OnActionContext);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const L = (path: string, fallback: string) => (getValue(path) as string) || fallback;

  const mode = (getValue("/mode") as string) || "create";
  const initialType = (getValue("/form/type") as string) === "person" ? "person" : "company";

  const [tab, setTab] = useState<"company" | "person">(initialType);
  const [name, setName] = useState((getValue("/form/name") as string) || "");
  const [firstName, setFirstName] = useState(() => {
    if (initialType !== "person") return "";
    const n = (getValue("/form/name") as string) || "";
    return n.split(" ")[0] || "";
  });
  const [lastName, setLastName] = useState(() => {
    if (initialType !== "person") return "";
    const n = (getValue("/form/name") as string) || "";
    return n.split(" ").slice(1).join(" ") || "";
  });
  const [country, setCountry] = useState((getValue("/form/country") as string) || "DK");
  const [registrationNo, setRegistrationNo] = useState((getValue("/form/registrationNo") as string) || "");
  const [phone, setPhone] = useState((getValue("/form/phone") as string) || "");
  const [email, setEmail] = useState((getValue("/form/email") as string) || "");
  const [street, setStreet] = useState((getValue("/form/street") as string) || "");
  const [city, setCity] = useState((getValue("/form/city") as string) || "");
  const [zipcode, setZipcode] = useState((getValue("/form/zipcode") as string) || "");
  const id = (getValue("/form/id") as string) || "";

  const fireEvent = useCallback((evName: string, context: Record<string, unknown>) => {
    if (!onAction) return;
    onAction({ userAction: { name: evName, sourceComponentId: node.id, surfaceId, context } });
  }, [onAction, node.id, surfaceId]);

  const handleSubmit = useCallback(() => {
    const finalName = tab === "person" ? `${firstName} ${lastName}`.trim() : name;
    const ctx: Record<string, unknown> = {
      name: finalName,
      type: tab,
      country,
      registrationNo,
      phone,
      email,
      street,
      city,
      zipcode,
    };
    if (mode === "edit") {
      ctx.id = id;
      fireEvent("submit_edit_customer", ctx);
    } else {
      fireEvent("submit_create_customer", ctx);
    }
  }, [tab, firstName, lastName, name, country, registrationNo, phone, email, street, city, zipcode, mode, id, fireEvent]);

  const inputCls = "w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-300";
  const labelCls = "block text-xs text-slate-500 mb-1";

  const canSubmit = tab === "company" ? name.trim() !== "" : firstName.trim() !== "";

  const title = mode === "edit" ? L("/labels/title_edit", "Edit contact") : L("/labels/title_create", "New contact");
  const submitLabel = mode === "edit" ? L("/labels/submit_edit", "Save changes") : L("/labels/submit_create", "Create contact");

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 w-full max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-slate-100">
        <h2 className="text-xl font-bold text-slate-900">{title}</h2>
        <button
          onClick={() => fireEvent("cancel", {})}
          className="text-slate-400 hover:text-slate-600 transition-colors text-xl leading-none"
          aria-label="Close"
        >✕</button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 px-6">
        {(["company", "person"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`py-3 px-1 mr-6 text-sm font-medium border-b-2 transition-colors ${
              tab === t
                ? "border-blue-600 text-slate-900"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {t === "company" ? L("/labels/tab_company", "Company") : L("/labels/tab_individual", "Individual")}
          </button>
        ))}
      </div>

      {/* Body */}
      <div className="px-6 py-5 space-y-4">
        {tab === "company" ? (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>{L("/labels/company_name", "Company name *")}</label>
                <input className={inputCls} value={name} onChange={e => setName(e.target.value)} placeholder={L("/labels/company_name_placeholder", "Company name")} />
              </div>
              <div>
                <label className={labelCls}>{L("/labels/country", "Country *")}</label>
                <select className={inputCls} value={country} onChange={e => setCountry(e.target.value)}>
                  {COUNTRIES.map(([code, label]) => (
                    <option key={code} value={code}>{label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>{L("/labels/tax_id", "Tax ID")}</label>
                <input className={inputCls} value={registrationNo} onChange={e => setRegistrationNo(e.target.value)} placeholder={L("/labels/cvr_placeholder", "CVR number")} />
              </div>
              <div>
                <label className={labelCls}>{L("/labels/phone", "Phone")}</label>
                <input className={inputCls} value={phone} onChange={e => setPhone(e.target.value)} placeholder={L("/labels/phone", "Phone")} />
              </div>
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600 mb-2">{L("/labels/contact_person", "Contact person")}</p>
              <div className="space-y-2">
                <input className={inputCls} value={email} onChange={e => setEmail(e.target.value)} placeholder={L("/labels/email", "Email")} />
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>{L("/labels/first_name", "First name *")}</label>
                <input className={inputCls} value={firstName} onChange={e => setFirstName(e.target.value)} placeholder={L("/labels/first_name_placeholder", "First name")} />
              </div>
              <div>
                <label className={labelCls}>{L("/labels/country", "Country *")}</label>
                <select className={inputCls} value={country} onChange={e => setCountry(e.target.value)}>
                  {COUNTRIES.map(([code, label]) => (
                    <option key={code} value={code}>{label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>{L("/labels/last_name", "Last name")}</label>
                <input className={inputCls} value={lastName} onChange={e => setLastName(e.target.value)} placeholder={L("/labels/last_name_placeholder", "Last name")} />
              </div>
              <div>
                <label className={labelCls}>{L("/labels/email", "Email")}</label>
                <input className={inputCls} value={email} onChange={e => setEmail(e.target.value)} placeholder={L("/labels/email", "Email")} />
              </div>
            </div>
            <div>
              <label className={labelCls}>{L("/labels/phone", "Phone")}</label>
              <input className={inputCls} value={phone} onChange={e => setPhone(e.target.value)} placeholder={L("/labels/phone", "Phone")} />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-600 mb-2">{L("/labels/address", "Address")}</p>
              <div className="space-y-2">
                <input className={inputCls} value={street} onChange={e => setStreet(e.target.value)} placeholder={L("/labels/street_placeholder", "Street")} />
                <div className="grid grid-cols-2 gap-2">
                  <input className={inputCls} value={zipcode} onChange={e => setZipcode(e.target.value)} placeholder={L("/labels/zip_placeholder", "ZIP")} />
                  <input className={inputCls} value={city} onChange={e => setCity(e.target.value)} placeholder={L("/labels/city_placeholder", "City")} />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-end gap-3 px-6 pb-6">
        <button
          onClick={() => fireEvent("cancel", {})}
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
