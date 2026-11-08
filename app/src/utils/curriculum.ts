import type { Node } from "@xyflow/react";
import { courseColor } from "../theme/domains";
import type { Theme } from "./theme";
import type { Curriculum, Facets, Glossary, WikiNodeData } from "../types";

export const courseFacet = (course: string) => `course:${course}`;
export const moduleFacet = (course: string, module: string) => `module:${course}/${module}`;
export const beyondFacet = (domain: string) => `beyond:${domain}`;
/** Every page no lesson links, whatever its directory. */
export const OUTSIDE_COURSES = "beyond:all";
export const dirFacet = (dir: string) => `dir:${dir}`;
export const tagFacet = (tag: string) => `tag:${tag}`;
export const termFacet = (term: string) => `term:${term}`;

const FACET_ID = /^(course|module|beyond|dir|tag|term):/;
const CURRICULUM_FACET = /^(course|module|beyond):/;
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
 * curriculum is in (and all pages outside a course), every wiki directory, every frontmatter
 * tag, and every glossary term (the pages that mention it).
 */
export function facetsOf(
  c: Curriculum | null,
  nodes: Pick<Node<WikiNodeData>, "id" | "data">[] = [],
  glossary: Glossary | null = null,
): Facets {
  const out: Facets = new Map();
  if (c) {
    for (const course of c.courses) {
      out.set(courseFacet(course.id), new Set(course.pageIds));
      for (const m of course.modules) out.set(moduleFacet(course.id, m.id), new Set(m.pageIds));
    }
    for (const b of c.beyond) out.set(beyondFacet(b.domain), new Set(b.pageIds));
    out.set(OUTSIDE_COURSES, new Set(c.beyond.flatMap((b) => b.pageIds)));
  }
  const add = (id: string, page: string) => {
    const set = out.get(id);
    if (set) set.add(page);
    else out.set(id, new Set([page]));
  };
  for (const n of nodes) {
    const dir = n.data.path?.split("/")[0];
    if (dir) add(dirFacet(dir), n.id);
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
