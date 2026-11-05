/**
 * The map's levels in the hash route, so a reload restores the level:
 *
 *   #/ , #/map/domain                  atlas by directory
 *   #/map/course                       atlas by course
 *   #/map/<grouping>/<sector>          focused sector
 *   #/map/<grouping>/<sector>/<page>   focused page
 *   #/map/all?tags=a,b                 every page under the filter
 *
 * `?cap=300` widens a focused view. Course, practice and flashcard routes aren't map routes:
 * parse gives null and the graph, which stays mounted under them, keeps its level.
 */

export type Grouping = "domain" | "course";

/** Pages a focused view holds until asked for more. */
export const DEFAULT_CAP = 150;
/** A page's neighbourhood is meant to be read card by card, so it opens smaller than a sector. */
export const PAGE_CAP = 60;
export const MAX_CAP = 2400;

export type MapView =
  | { level: "atlas"; grouping: Grouping }
  | { level: "sector"; grouping: Grouping; sector: string; cap: number }
  | { level: "page"; grouping: Grouping; sector: string; page: string; cap: number }
  | { level: "all"; tags: string[] };

export const ATLAS: MapView = { level: "atlas", grouping: "domain" };

const OTHER_SECTIONS = /^\/(courses|practice|flashcards)(\/|$)/;

function capOf(query: URLSearchParams, fallback: number): number {
  const n = Number(query.get("cap"));
  return Number.isInteger(n) && n > 0 ? Math.min(n, MAX_CAP) : fallback;
}

function decode(part: string): string | null {
  try {
    return decodeURIComponent(part);
  } catch {
    return null;
  }
}

export function parseMapRoute(route: string): MapView | null {
  const [path, rawQuery = ""] = route.split("?");
  if (OTHER_SECTIONS.test(path)) return null;
  const query = new URLSearchParams(rawQuery);
  if (path !== "/map" && !path.startsWith("/map/")) return ATLAS;
  const parts = path.split("/").slice(2).filter(Boolean).map(decode);
  if (parts.includes(null) || parts.length > 3) return ATLAS;
  const [first, sector, page] = parts as string[];
  if (first === "all" && !sector) {
    return { level: "all", tags: (query.get("tags") ?? "").split(",").filter(Boolean) };
  }
  if (first !== "domain" && first !== "course") return ATLAS;
  if (page) return { level: "page", grouping: first, sector, page, cap: capOf(query, PAGE_CAP) };
  if (sector) return { level: "sector", grouping: first, sector, cap: capOf(query, DEFAULT_CAP) };
  return { level: "atlas", grouping: first };
}

export function mapPath(v: MapView): string {
  const cap = "cap" in v && v.cap !== (v.level === "page" ? PAGE_CAP : DEFAULT_CAP) ? `?cap=${v.cap}` : "";
  const part = encodeURIComponent;
  switch (v.level) {
    case "atlas":
      return `/map/${v.grouping}`;
    case "sector":
      return `/map/${v.grouping}/${part(v.sector)}${cap}`;
    case "page":
      return `/map/${v.grouping}/${part(v.sector)}/${part(v.page)}${cap}`;
    case "all":
      return v.tags.length ? `/map/all?tags=${v.tags.map(part).join(",")}` : "/map/all";
  }
}

/** One level up: page → sector → atlas, and All → atlas. */
export function parentOf(v: MapView): MapView | null {
  switch (v.level) {
    case "page":
      return { level: "sector", grouping: v.grouping, sector: v.sector, cap: DEFAULT_CAP };
    case "sector":
      return { level: "atlas", grouping: v.grouping };
    case "all":
      return ATLAS;
    case "atlas":
      return null;
  }
}

/** Identity of a level, ignoring the cap: widening a view is not a new view. */
export function levelKey(v: MapView): string {
  return mapPath(v.level === "all" ? { level: "all", tags: [] } : v).split("?")[0];
}

/** Go to a path without a history entry, for a route that turned out to be unusable. */
export function replaceRoute(path: string): void {
  window.history.replaceState(null, "", `#${path}`);
  window.dispatchEvent(new HashChangeEvent("hashchange"));
}
