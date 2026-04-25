import { createContext } from "react";

// OnSendMessageContext — lets custom components send a plain chat message
// (e.g. DashboardSuggestions chips) without going through the [ui_event] path.
export const OnSendMessageContext = createContext<((text: string) => void) | null>(null);

// OnActionContext — lets custom components fire UI events without needing
// direct access to the A2UIProvider's onAction callback.
export const OnActionContext = createContext<((action: unknown) => void) | null>(null);
