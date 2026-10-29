import { useEffect, useState, useCallback } from "react";

/**
 * Minimal hash router — `#/` (graph), `#/courses`, `#/practice`, `#/courses/<course>`,
 * `#/courses/<lesson id with slashes>`. Hash routing keeps deep links working
 * under the Vite dev server and the static build without server rewrites.
 */
export function useHashRoute(): [string, (path: string) => void] {
  const read = () => window.location.hash.replace(/^#/, "") || "/";
  const [path, setPath] = useState(read);

  useEffect(() => {
    const onChange = () => setPath(read());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const navigate = useCallback((to: string) => {
    window.location.hash = to;
  }, []);

  return [path, navigate];
}
