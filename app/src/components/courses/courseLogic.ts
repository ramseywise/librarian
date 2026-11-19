import type { Course, CourseModule, Lesson } from "./types";
import { stripDuplicateH1 } from "./lessonParts";

export const lessonsOf = (c: Course) => c.modules.flatMap((m) => m.lessons);

const GROUP_TITLES: Record<string, string> = { core: "Core modules", advanced: "Advanced topics" };

/** The course's modules as the groups its README sorts them into, in order. A course with no groups is one
 * unlabelled group. */
export function moduleGroups(modules: CourseModule[]): { key: string; title: string; modules: CourseModule[] }[] {
  const groups: { key: string; title: string; modules: CourseModule[] }[] = [];
  for (const m of modules) {
    const key = m.group ?? "";
    const last = groups[groups.length - 1];
    if (last && last.key === key) last.modules.push(m);
    else groups.push({ key, title: GROUP_TITLES[key] ?? "", modules: [m] });
  }
  return groups.length > 1 || groups[0]?.key ? groups.map((g) => ({ ...g, title: g.title || "More" })) : groups;
}

/** A course readme as its page shows it: the lead and "What it is" above the modules, each module group's own
 * section (its syllabus table) under that group's cards, and the rest below. The outcomes and the per-module
 * units are dropped, because the page lists the outcomes itself and each module's page holds its unit. */
export function splitCourseReadme(lesson: Lesson): { intro: string; groups: Record<string, string>; rest: string } {
  const [lead, ...sections] = stripDuplicateH1(lesson.body, lesson.title).split(/^(?=## )/m);
  const groups: Record<string, string> = {};
  let intro = lead;
  let rest = "";
  for (const section of sections) {
    const heading = section.match(/^## (.*)/)?.[1].trim() ?? "";
    const body = section.replace(/^## .*\n/, "");
    const group = heading.match(/^(core|advanced)\b/i)?.[1].toLowerCase();
    if (group) groups[group] = body;
    else if (/^what it is$/i.test(heading)) intro += body;
    else if (!/^(course outcomes|units)$/i.test(heading)) rest += section;
  }
  return { intro, groups, rest };
}

/** A readme as the page shows it: the lead above the lecture, the rest below it. The readme's own "Lecture"
 * and "Next" sections say what the page's lecture card and its closing "What's next" already say, so they are dropped. */
export function splitOverview(lesson: Lesson): { lead: string; rest: string } {
  const body = stripDuplicateH1(lesson.body, lesson.title);
  const at = body.search(/^## /m);
  if (at < 0) return { lead: body, rest: "" };
  return { lead: body.slice(0, at), rest: body.slice(at).replace(/^## (Lecture|Next)\s*\n[\s\S]*?(?=^## |(?![\s\S]))/gm, "") };
}

/** The syllabus row a note is studied in ("1. Load"), read off the readme's table. */
export function submoduleOf(body: string, noteId: string): string | null {
  const slug = noteId.split("/").pop() ?? "";
  const row = body.split("\n").find((line) => line.startsWith("| **") && new RegExp(`/${slug}(\\.md)?[)#]`).test(line));
  return row?.match(/^\| \*\*(.+?):?\*\*/)?.[1] ?? null;
}
