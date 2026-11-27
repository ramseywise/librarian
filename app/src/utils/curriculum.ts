import type { Node } from "@xyflow/react";
import { courseColor } from "../theme/domains";
import type { Theme } from "./theme";
import type { Area, Curriculum, Facets, Glossary, WikiNodeData } from "../types";
import type { RankGroup } from "./neighbourRank";

export const courseFacet = (course: string) => `course:${course}`;
export const moduleFacet = (course: string, module: string) => `module:${course}/${module}`;
/** A note (lesson) by its lesson id, `<course>/<module>/notes/NN-slug`: the pages it links. */
export const noteFacet = (lesson: string) => `note:${lesson}`;
export const beyondFacet = (domain: string) => `beyond:${domain}`;
/** Every page no lesson links, whatever its directory. */
export const OUTSIDE_COURSES = "beyond:all";
export const dirFacet = (dir: string) => `dir:${dir}`;
export const tagFacet = (tag: string) => `tag:${tag}`;
export const termFacet = (term: string) => `term:${term}`;
/** Every page in an area's directories. */
export const areaFacet = (area: string) => `area:${area}`;
/** An area's pages no lesson links yet: what its course has still to cover. */
export const gapFacet = (area: string) => `gap:${area}`;
/** Pages first taught at a tier: the lowest tier among the notes that link them. */
export const TIERS = ["foundations", "practitioner", "specialist"] as const;
export const tierFacet = (tier: string) => `tier:${tier}`;

const FACET_ID = /^(course|module|note|beyond|area|gap|tier|dir|tag|term):/;
const CURRICULUM_FACET = /^(course|module|note|beyond|gap|tier):/;
export const isFacetId = (tag: string) => FACET_ID.test(tag);
export const isModuleFacet = (tag: string) => tag.startsWith("module:");

/**
 * Has a filter id's source not arrived yet? Curriculum facets wait on the curriculum, term facets
 * on the glossary; a `tag:` facet comes with the pages.
 */
export function facetPending(id: string, c: Curriculum | null, glossary: Glossary | null): boolean {
  if (CURRICULUM_FACET.test(id)) return !c;
  if (id.startsWith("term:")) return !glossary;
  return false;
}

/**
 * Filter id → the pages it selects: every course, module and "beyond" directory once the
 * curriculum is in (and all pages outside a course), every wiki directory, every area (and,
 * with the curriculum, its gap: the area's pages no lesson links), every frontmatter tag, and
 * every glossary term (the pages that mention it).
 */
export function facetsOf(
  c: Curriculum | null,
  nodes: Pick<Node<WikiNodeData>, "id" | "data">[] = [],
  glossary: Glossary | null = null,
  areas: Area[] = [],
): Facets {
  const out: Facets = new Map();
  if (c) {
    for (const course of c.courses) {
      out.set(courseFacet(course.id), new Set(course.pageIds));
      for (const m of course.modules) {
        out.set(moduleFacet(course.id, m.id), new Set(m.pageIds));
        for (const n of m.notes) if (n.pageIds.length) out.set(noteFacet(n.id), new Set(n.pageIds));
      }
    }
    for (const b of c.beyond) out.set(beyondFacet(b.domain), new Set(b.pageIds));
    out.set(OUTSIDE_COURSES, new Set(c.beyond.flatMap((b) => b.pageIds)));
    for (const [page, tier] of Object.entries(c.pageTier ?? {})) {
      const set = out.get(tierFacet(tier));
      if (set) set.add(page);
      else out.set(tierFacet(tier), new Set([page]));
    }
  }
  const add = (id: string, page: string) => {
    const set = out.get(id);
    if (set) set.add(page);
    else out.set(id, new Set([page]));
  };
  const areaOfDir = new Map(areas.flatMap((a) => a.domains.map((d) => [d, a.id] as [string, string])));
  for (const n of nodes) {
    const dir = n.data.path?.split("/")[0];
    if (dir) add(dirFacet(dir), n.id);
    const area = dir && areaOfDir.get(dir);
    if (area) {
      add(areaFacet(area), n.id);
      if (c && !c.primaryCourse[n.id]) add(gapFacet(area), n.id);
    }
    for (const t of n.data.tags ?? []) add(tagFacet(t), n.id);
  }
  if (glossary) for (const [term, pages] of Object.entries(glossary.mentions)) out.set(termFacet(term), new Set(pages));
  return out;
}

/** Each page's curriculum modules, as facet ids: the "same module" layer walks these. */
export function modulesOf(c: Curriculum | null): Map<string, string[]> {
  const out = new Map<string, string[]>();
  if (!c) return out;
  for (const course of c.courses) {
    for (const m of course.modules) {
      const id = moduleFacet(course.id, m.id);
      for (const page of m.pageIds) {
        const list = out.get(page);
        if (list) list.push(id);
        else out.set(page, [id]);
      }
    }
  }
  return out;
}

/**
 * The groups a page's level is ranked over (utils/neighbourRank): every module, every note and
 * every glossary term with its pages, and each module's notes in reading order.
 */
export function rankGroupsOf(c: Curriculum | null, glossary: Glossary | null): { groups: RankGroup[]; readingOrder: string[][] } {
  const groups: RankGroup[] = [];
  const readingOrder: string[][] = [];
  for (const course of c?.courses ?? []) {
    for (const m of course.modules) {
      groups.push({ id: moduleFacet(course.id, m.id), kind: "module", pages: m.pageIds });
      const order: string[] = [];
      for (const n of m.notes) {
        if (!n.pageIds.length) continue;
        groups.push({ id: noteFacet(n.id), kind: "note", pages: n.pageIds });
        order.push(noteFacet(n.id));
      }
      if (order.length > 1) readingOrder.push(order);
    }
  }
  for (const [term, pages] of Object.entries(glossary?.mentions ?? {})) groups.push({ id: termFacet(term), kind: "term", pages });
  return { groups, readingOrder };
}

/**
 * Colour and label cards by their main course, so the panel doubles as a legend. Pages no
 * lesson links keep their directory colour. Done per render rather than on the graph payload:
 * a new `baseNodes` array means a relayout, and the curriculum arriving must not move cards.
 */
export function withCourseGroups<T extends Node<WikiNodeData>>(nodes: T[], c: Curriculum | null, theme?: Theme): T[] {
  if (!c) return nodes;
  const titles = new Map(c.courses.map((x) => [x.id, x.title]));
  return nodes.map((n) => {
    const course = c.primaryCourse[n.id];
    if (!course) return n;
    return {
      ...n,
      data: { ...n.data, groupColor: courseColor(course, theme), groupLabel: titles.get(course) ?? course },
    };
  });
}
