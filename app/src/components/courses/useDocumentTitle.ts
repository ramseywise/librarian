import { useEffect } from "react";

/** Set the tab title while a view is shown. `null` leaves it alone (e.g. still loading). */
export function useDocumentTitle(title: string | null) {
  useEffect(() => {
    if (title !== null) document.title = title;
  }, [title]);
}

export const pageTitle = (...parts: string[]) => [...parts, "Librarian"].join(" · ");
