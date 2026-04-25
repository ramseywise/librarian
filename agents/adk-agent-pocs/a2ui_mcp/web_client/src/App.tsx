import { useCallback, useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { ChatPanel } from "./components/ChatPanel";
import { StatusBar } from "./components/StatusBar";
import { SurfacePanel } from "./components/SurfacePanel";
import { BILLY_REST_BASE } from "./components/core/fetch-resolver";
import { useAgents } from "./hooks/useAgents";
import { useChat } from "./hooks/useChat";

// Generate a stable session ID for this browser tab
const SESSION_ID = uuidv4();

const MIN_PANEL_PX = 240;

export default function App() {
  // Queued A2UI message batches — cleared after SurfacePanel consumes them
  const [pendingA2UI, setPendingA2UI] = useState<unknown[][]>([]);
  const pendingRef = useRef<unknown[][]>([]);

  // Suggestion chips extracted from the agent's "suggestions" surface
  const [chatSuggestions, setChatSuggestions] = useState<string[]>([]);

  // Track whether the invoice create form is open so we can resolve "set customer" client-side
  const invoiceFormOpenRef = useRef(false);

  // Resizable split — surfaceWidth is the left (surface) panel width in px
  const containerRef = useRef<HTMLDivElement>(null);
  const [surfaceWidth, setSurfaceWidth] = useState<number | null>(null);
  const dragging = useRef(false);

  const handleA2UIMessages = useCallback((messages: unknown[]) => {
    pendingRef.current = [...pendingRef.current, messages];
    setPendingA2UI([...pendingRef.current]);
    for (const msg of messages) {
      const m = msg as {
        deleteSurface?: { surfaceId: string };
        updateDataModel?: { surfaceId: string; path?: string; value?: unknown };
      };
      // Track invoice form open/close
      if (m.deleteSurface?.surfaceId === "detail") {
        invoiceFormOpenRef.current = false;
      }
      if (m.updateDataModel?.surfaceId === "detail") {
        const val = m.updateDataModel.value;
        if (val && typeof val === "object" && !Array.isArray(val)) {
          const form = (val as Record<string, unknown>).form;
          if (form && typeof form === "object" && "customerId" in (form as object)) {
            invoiceFormOpenRef.current = true;
          }
        }
      }
      // Extract suggestions
      if (m.updateDataModel?.surfaceId === "suggestions") {
        const val = m.updateDataModel.value;
        if (Array.isArray(val)) {
          setChatSuggestions(val as string[]);
        } else if (val && typeof val === "object" && Array.isArray((val as Record<string, unknown>).suggestions)) {
          setChatSuggestions((val as Record<string, unknown>).suggestions as string[]);
        }
      }
    }
  }, []);

  const { activeAgent } = useAgents(SESSION_ID);

  const { messages, loading, connected, sendMessage, sendSilentMessage, addUserMessage, addAgentMessage } = useChat(
    SESSION_ID,
    activeAgent,
    handleA2UIMessages
  );

  // Inject the initial dashboard directly — no LLM round trip needed.
  const dashboardSentRef = useRef(false);
  useEffect(() => {
    if (connected && !dashboardSentRef.current) {
      dashboardSentRef.current = true;
      const year = new Date().getFullYear();
      handleA2UIMessages([
        { version: "v0.9", createSurface: { surfaceId: "main", catalogId: "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
        { version: "v0.9", updateDataModel: { surfaceId: "main", path: "/", value: { year, labels: { rev_title: "Revenue Overview" } } } },
        { version: "v0.9", updateComponents: { surfaceId: "main", components: [{ id: "root", component: "RevenueSummary" }] } },
        { version: "v0.9", createSurface: { surfaceId: "panel_1", catalogId: "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
        { version: "v0.9", updateDataModel: { surfaceId: "panel_1", path: "/", value: { year, labels: { pipe_title: "Invoice Pipeline" } } } },
        { version: "v0.9", updateComponents: { surfaceId: "panel_1", components: [{ id: "root", component: "InvoiceStatusChart" }] } },
        { version: "v0.9", createSurface: { surfaceId: "suggestions", catalogId: "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
        { version: "v0.9", updateDataModel: { surfaceId: "suggestions", path: "/", value: {
          suggestions: ["Who owes me money?", "Show top customers", "Monthly revenue 2026", "Is revenue trending up?", "Any unusual months?", "Which products sell best?"],
          labels: { sugg_heading: "Explore further" },
        } } },
        { version: "v0.9", updateComponents: { surfaceId: "suggestions", components: [{ id: "root", component: "DashboardSuggestions" }] } },
      ]);
    }
  }, [connected, handleA2UIMessages]);

  // Parse "set customer [as/to] X" / "sæt X som kunde" etc. and return the customer name, or null
  const parseSetCustomer = useCallback((text: string): string | null => {
    const t = text.trim();
    const patterns = [
      // English: "set/change/update [the] customer[s] [on [the] invoice] [to/as] X"
      /^(?:set|change|update)(?: the)? customers?(?: on (?:the )?invoice)? (?:(?:to|as) )?(.+)$/i,
      // English: "use X as [the] customer"
      /^use (.+?) as (?:the )?customer$/i,
      // Danish: "sæt X som kunde"
      /^sæt (.+?) som kunde$/i,
      // Danish: "sæt kunde[n] [til/som/=] X"
      /^sæt kunden? (?:til|som|as|=) (.+)$/i,
      // Danish: "vælg X som kunde"
      /^vælg (.+?) som kunde$/i,
      // Danish: "brug X som kunde / på faktura"
      /^brug (.+?) (?:som kunde|på faktura)$/i,
    ];
    for (const pat of patterns) {
      const m = t.match(pat);
      if (m?.[1]) return m[1].trim();
    }
    return null;
  }, []);

  // Wrap sendMessage to intercept "set customer" requests when the invoice form is open.
  // Resolves the customer via REST and emits updateDataModel immediately — no LLM round trip.
  // The original message is still forwarded to the LLM for text confirmation.
  const sendMessageWithCustomerInterception = useCallback(
    async (text: string) => {
      console.log("[setCustomer] formOpen:", invoiceFormOpenRef.current, "| text:", text);
      if (invoiceFormOpenRef.current) {
        const customerName = parseSetCustomer(text);
        console.log("[setCustomer] parsed name:", customerName);
        if (customerName) {
          try {
            const url = `${BILLY_REST_BASE}/customers?name=${encodeURIComponent(customerName)}&page_size=10`;
            console.log("[setCustomer] fetching:", url);
            const res = await fetch(url);
            const data = await res.json() as unknown;
            console.log("[setCustomer] response ok:", res.ok, "| data:", data);
            if (res.ok) {
              const list = Array.isArray(data) ? data : ((data as Record<string, unknown>)?.customers ?? []) as unknown[];
              console.log("[setCustomer] list length:", list.length, "| items:", list);
              if (list.length === 1) {
                const customer = list[0] as Record<string, unknown>;
                // Show user message in chat
                addUserMessage(text);
                // Re-emit the full form data model so customerOptions/productOptions
                // are preserved — A2UI replaces the surface data model on each
                // dataModelUpdate, so a targeted single-key update would wipe the options.
                handleA2UIMessages([
                  {
                    version: "v0.9",
                    updateDataModel: {
                      surfaceId: "detail",
                      path: "/",
                      value: {
                        form: { customerId: String(customer.id ?? ""), dueDate: "", lineItems: [] },
                        customerOptions: { "$fetch": "/customers" },
                        productOptions: { "$fetch": "/products" },
                      },
                    },
                  },
                ]);
                // Synthetic agent confirmation — no LLM call so the surface isn't re-rendered
                addAgentMessage(`${String(customer.name ?? customerName)} selected as customer.`);
                return;
              }
            }
          } catch (err) {
            console.log("[setCustomer] fetch error:", err);
            // Fall through — LLM will handle it
          }
        }
      }
      sendMessage(text);
    },
    [sendMessage, handleA2UIMessages, parseSetCustomer, addUserMessage, addAgentMessage]
  );

  // A2UI messages for the invoice list main surface (no LLM needed)
  const injectInvoiceMain = useCallback(() => {
    const year = new Date().getFullYear();
    handleA2UIMessages([
      { version: "v0.9", createSurface: { surfaceId: "main", catalogId: "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
      { version: "v0.9", updateDataModel: { surfaceId: "main", path: "/", value: { year, invoices: { "$fetch": `/invoices?fiscal_year=${year}` } } } },
      { version: "v0.9", updateComponents: { surfaceId: "main", components: [{ id: "root", component: "InvoiceList" }] } },
    ]);
  }, [handleA2UIMessages]);

  // Forward surface events — handle invoice form events client-side to skip the LLM
  const handleSurfaceAction = useCallback(
    async (event: unknown) => {
      const e = event as { userAction?: { name?: string; context?: Record<string, unknown> } };
      const name = e.userAction?.name;
      const ctx = (e.userAction?.context ?? {}) as Record<string, unknown>;

      // cancel_invoice: close the form and restore the invoice list — no LLM needed
      if (name === "cancel_invoice") {
        handleA2UIMessages([{ version: "v0.9", deleteSurface: { surfaceId: "detail" } }]);
        injectInvoiceMain();
        return;
      }

      // submit_invoice_form: create a new invoice via REST, then refresh the list
      if (name === "submit_invoice_form") {
        // ChoicePicker returns selections as an array; unwrap single-select value
        const rawCustomerId = ctx.customerId;
        const customerId = Array.isArray(rawCustomerId) ? (rawCustomerId[0] as string) : (rawCustomerId as string);
        const dueDate = ctx.dueDate as string | undefined;
        type LineItem = { productId: string; quantity: unknown; unitPrice: unknown };
        const lineItems = (ctx.lineItems ?? []) as LineItem[];
        const today = new Date().toISOString().split("T")[0];
        const ptDays = dueDate
          ? Math.max(0, Math.round((new Date(dueDate).getTime() - Date.now()) / 86400000))
          : 7;
        try {
          const res = await fetch(`${BILLY_REST_BASE}/invoices`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contact_id: customerId,
              entry_date: today,
              payment_terms_days: ptDays,
              state: "approved",
              lines: lineItems.map((l) => ({
                product_id: l.productId,
                quantity: parseFloat(String(l.quantity)),
                unit_price: parseFloat(String(l.unitPrice)),
              })),
            }),
          });
          if (!res.ok) throw new Error(await res.text());
          handleA2UIMessages([{ version: "v0.9", deleteSurface: { surfaceId: "detail" } }]);
          injectInvoiceMain();
        } catch (err) {
          console.error("Invoice create failed:", err);
          sendSilentMessage(`[ui_event] ${JSON.stringify(event)}`);
        }
        return;
      }

      // submit_edit_invoice_form: save a draft invoice via REST, then refresh
      if (name === "submit_edit_invoice_form") {
        const invoiceId = ctx.invoiceId as string;
        const dueDate = ctx.dueDate as string | undefined;
        type LineItem = { productId: string; quantity: unknown; unitPrice: unknown };
        const lineItems = (ctx.lineItems ?? []) as LineItem[];
        const ptDays = dueDate
          ? Math.max(0, Math.round((new Date(dueDate).getTime() - Date.now()) / 86400000))
          : undefined;
        try {
          const res = await fetch(`${BILLY_REST_BASE}/invoices/${invoiceId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              ...(ptDays !== undefined && { payment_terms_days: ptDays }),
              lines: lineItems.map((l) => ({
                product_id: l.productId,
                quantity: parseFloat(String(l.quantity)),
                unit_price: parseFloat(String(l.unitPrice)),
              })),
            }),
          });
          if (!res.ok) throw new Error(await res.text());
          handleA2UIMessages([{ version: "v0.9", deleteSurface: { surfaceId: "detail" } }]);
          injectInvoiceMain();
        } catch (err) {
          console.error("Invoice edit failed:", err);
          sendSilentMessage(`[ui_event] ${JSON.stringify(event)}`);
        }
        return;
      }

      // All other events go to the agent
      sendMessage(`[ui_event] ${JSON.stringify(event)}`);
    },
    [sendMessage, sendSilentMessage, handleA2UIMessages, injectInvoiceMain]
  );

  // After SurfacePanel renders new messages, clear the pending queue
  const handlePendingConsumed = useCallback(() => {
    pendingRef.current = [];
    setPendingA2UI([]);
  }, []);

  const onDividerMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;

    const onMove = (ev: MouseEvent) => {
      if (!dragging.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const totalWidth = rect.width;
      // surfaceWidth = distance from left edge to divider
      const newWidth = Math.min(
        totalWidth - MIN_PANEL_PX,
        Math.max(MIN_PANEL_PX, ev.clientX - rect.left)
      );
      setSurfaceWidth(newWidth);
    };

    const onUp = () => {
      dragging.current = false;
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, []);

  return (
    <div className="flex flex-col h-screen">
      <StatusBar connected={connected} />
      <div ref={containerRef} className="flex flex-1 overflow-hidden">
        {/* Left: A2UI surfaces */}
        <div
          className="flex-shrink-0 bg-slate-50 overflow-y-auto"
          style={surfaceWidth != null ? { width: surfaceWidth } : { flex: "0 0 60%" }}
        >
          <SurfacePanel
            pendingMessages={pendingA2UI}
            onAction={handleSurfaceAction}
            onConsumed={handlePendingConsumed}
            onSendMessage={sendMessage}
          />
        </div>

        {/* Drag divider */}
        <div
          onMouseDown={onDividerMouseDown}
          className="w-1.5 flex-shrink-0 bg-slate-200 hover:bg-indigo-400 cursor-col-resize transition-colors"
          title="Drag to resize"
        />

        {/* Right: Chat */}
        <div className="flex-1 min-w-60 flex flex-col bg-slate-50">
          <ChatPanel
            messages={messages}
            loading={loading}
            onSend={sendMessageWithCustomerInterception}
            suggestions={chatSuggestions}
          />
        </div>
      </div>
    </div>
  );
}
