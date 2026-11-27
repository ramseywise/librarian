import type { CourseModule, LessonOutline } from "./types";

/** A notebook or a file under the module's `practice/`: listed with the labs, not with the notes. */
export const isPractice = (moduleId: string, l: LessonOutline) =>
  l.kind === "notebook" || l.id.startsWith(`${moduleId}/practice/`);

/** The lessons a module's page lists as its notes, in reading order: not its own readme or references, a drill
 * or a practice file. `moduleId` is `<course>/<module>`. */
export function moduleNotes(moduleId: string, m: CourseModule): LessonOutline[] {
  return m.lessons.filter((l) => l.kind !== "drill" && l.id !== `${moduleId}/readme`
    && l.id !== `${moduleId}/references` && !isPractice(moduleId, l));
}

export interface LessonSection {
  /** The folder the lessons sit in, as the importer names it ("Behavioral"). */
  title: string;
  lessons: LessonOutline[];
  /** Where the section opens: its readme when it has one, else its first lesson. */
  first: LessonOutline;
}

const parts = (l: LessonOutline) => (l.section ?? "").split(" / ");

/** What follows the section's own name in a lesson's `section` ("Case study / Examples" → "Examples"). */
export const subsectionOf = (l: LessonOutline) => parts(l).slice(1).join(" / ");

/** Lessons grouped by the top folder of their `section`, in the order each folder first appears. Empty unless
 * there are at least two, so a module whose notes all sit in `notes/` stays one flat list. */
export function lessonSections(lessons: LessonOutline[]): LessonSection[] {
  const groups = new Map<string, LessonOutline[]>();
  for (const l of lessons) {
    const title = parts(l)[0];
    const list = groups.get(title);
    if (list) list.push(l);
    else groups.set(title, [l]);
  }
  if (groups.size < 2) return [];
  return [...groups].map(([title, list]) => ({
    title,
    lessons: list,
    first: list.find((l) => !subsectionOf(l) && /\/readme$/.test(l.id)) ?? list[0],
  }));
}

export interface Submodule {
  /** The part's number in the module deck, so `#/slides/<module>?part=n` opens on it. */
  n: number;
  title: string;
  summary?: string;
  /** The module's notes this part teaches, in reading order. */
  lessons: LessonOutline[];
}

/** The module's submodules: the parts of its deck after the overview (the module page is the intro), each with
 * the notes it teaches. A note no part cites is in none of them. Empty when the module has no deck parts. */
export function submodules(moduleId: string, m: CourseModule): Submodule[] {
  const deck = m.decks?.find((d) => d.id === moduleId);
  const notes = moduleNotes(moduleId, m);
  return (deck?.parts ?? []).map((p) => ({
    n: p.n,
    title: p.title,
    summary: p.summary,
    lessons: notes.filter((l) => p.notes.some((stem) => l.id === `${moduleId}/notes/${stem}`)),
  }));
}
