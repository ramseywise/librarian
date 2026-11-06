import type { Node } from "@xyflow/react";
import { courseColor } from "../theme/domains";
import type { Theme } from "./theme";
import type { Curriculum, Facets, WikiNodeData } from "../types";

export const courseFacet = (course: string) => `course:${course}`;
export const moduleFacet = (course: string, module: string) => `module:${course}/${module}`;
export const beyondFacet = (domain: string) => `beyond:${domain}`;

const FACET_ID = /^(course|module|beyond):/;
export const isFacetId = (tag: string) => FACET_ID.test(tag);
export const isModuleFacet = (tag: string) => tag.startsWith("module:");

/** Filter id → the pages it selects, for every course, module and "beyond" directory. */
export function facetsOf(c: Curriculum | null): Facets | undefined {
  if (!c) return undefined;
  const out: Facets = new Map();
  for (const course of c.courses) {
    out.set(courseFacet(course.id), new Set(course.pageIds));
    for (const m of course.modules) out.set(moduleFacet(course.id, m.id), new Set(m.pageIds));
  }
  for (const b of c.beyond) out.set(beyondFacet(b.domain), new Set(b.pageIds));
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
