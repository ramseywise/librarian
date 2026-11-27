import { useState } from "react";
import { useCourses } from "../hooks/useCourses";
import { lessonSections, moduleNotes, submodules } from "./courses/sections";
import type { Course, CourseModule } from "./courses/types";

/** Courses that are practice rather than a subject pillar: listed at the bottom under Practice, not under Courses. */
const PRACTICE_COURSES = ["interviewing"];

type Section = "graph" | "courses" | "study" | "labs" | null;

function sectionOf(route: string): Section {
  if (route === "/" || route === "") return "graph";
  if (/^\/(courses|slides)(\/|$)/.test(route)) return "courses";
  if (/^\/(study|quiz|flashcards)(\/|$)/.test(route)) return "study";
  if (/^\/(labs|practice)(\/|$)/.test(route)) return "labs";
  return null;
}

/** The one navigation for the whole app, in this order: Graph, Courses with its pillars under it, Study, Labs,
 * and Practice (the interview rounds) at the bottom. Each pillar (course) is a grey label: pillar, then module,
 * then submodule. A pillar is collapsed until
 * it is the one being read or is opened by hand (its label opens it and its page; its chevron opens or closes it
 * in place). An open pillar shows its modules in the body colour, "Core" and "Advanced" over them when it sorts
 * them, and under each module its submodules (its deck's parts after the overview, which is the module page) in
 * small grey text; each opens its first note, or its slides when it teaches no note of its own. The module being
 * read is the filled row. A module with no lessons is left out. A module whose notes sit in folders of their own (the interview rounds) lists
 * those folders under it while it is open, or always when it is the course's only module. Lessons are not
 * listed here, they are on the module's page. `open` is the drawer of a narrow screen; `hidden` slides it away on a wide one. */
export function AppNav({ route, open, hidden = false, id }: { route: string; open: boolean; hidden?: boolean; id: string }) {
  const { data: courses } = useCourses();
  // Pillars opened or closed by hand; a pillar not in here is open only while it is the one being read.
  const [opened, setOpened] = useState<Record<string, boolean>>({});
  const section = sectionOf(route);
  // `/courses/<course>[/<module>[/...]]` and `/slides/<course>/<module>[/<lecture>]` both start with the course.
  const path = section === "courses" ? route.replace(/^\/(courses|slides)\/?/, "").split("?")[0] : "";
  const course = path ? courses?.find((c) => path === c.id || path.startsWith(`${c.id}/`)) : undefined;
  const moduleOf = (m: CourseModule) => `${course?.id}/${m.id}`;
  const module = course?.modules.find(
    (m) => path === moduleOf(m) || path.startsWith(`${moduleOf(m)}/`) || m.lessons.some((l) => l.id === path),
  );

  const top = (name: Exclude<Section, null>, href: string, label: string, exact: boolean, elsewhere = false) => (
    <a
      href={href}
      className={`sidenav-item sidenav-item--top${section === name && !exact && !elsewhere ? " is-within" : ""}`}
      aria-current={section === name && exact ? "page" : undefined}
    >
      {label}
    </a>
  );

  const pillar = (c: Course) => {
        const isOpen = opened[c.id] ?? c === course;
        return (
        <div key={c.id} className="sidenav-group" role="group" aria-label={c.title}>
          <div className="sidenav-pillar">
            <a
              href={`#/courses/${c.id}`}
              className={`sidenav-label${c === course && path !== c.id ? " is-within" : ""}`}
              aria-current={path === c.id ? "page" : undefined}
              onClick={() => setOpened((o) => ({ ...o, [c.id]: true }))}
            >
              {c.title}
            </a>
            <button
              type="button"
              className="sidenav-toggle"
              aria-expanded={isOpen}
              aria-label={`${isOpen ? "Collapse" : "Expand"} ${c.title}`}
              onClick={() => setOpened((o) => ({ ...o, [c.id]: !isOpen }))}
            >
              <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true" className={isOpen ? "is-open" : undefined}>
                <path d="M4 2.5 7.5 6 4 9.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
          {!isOpen ? null : c.modules.filter((m) => m.lessons.length > 0 || m === module).map((m, i, shown) => [
            m.group && m.group !== shown[i - 1]?.group
              ? <div key={`${m.id}-group`} className="sidenav-sublabel">{m.group === "core" ? "Core" : m.group === "advanced" ? "Advanced" : m.group}</div>
              : null,
            <a
              key={m.id}
              href={`#/courses/${c.id}/${m.id}`}
              className={`sidenav-item sidenav-item--module${c === course && m === module ? " is-current" : ""}`}
              aria-current={c === course && path === moduleOf(m) ? "page" : undefined}
            >
              <span className="grow">{m.title}</span>
            </a>,
            ...submodules(`${c.id}/${m.id}`, m).map((sub) => (
              <a
                key={`${m.id}-part-${sub.n}`}
                href={sub.lessons[0] ? `#/courses/${sub.lessons[0].id}` : `#/slides/${c.id}/${m.id}?part=${sub.n}`}
                className={`sidenav-item sidenav-item--part${sub.lessons.some((l) => l.id === path) ? " is-current" : ""}`}
              >
                {sub.title}
              </a>
            )),
            ...(m === module || shown.length === 1 ? lessonSections(moduleNotes(`${c.id}/${m.id}`, m)) : []).map((sec) => (
              <a
                key={`${m.id}-${sec.title}`}
                href={`#/courses/${sec.first.id}`}
                className={`sidenav-item sidenav-item--section${sec.lessons.some((l) => l.id === path) ? " is-current" : ""}`}
              >
                <span className="grow">{sec.title}</span>
              </a>
            )),
          ])}
        </div>
        );
  };

  const isPractice = (c: Course) => PRACTICE_COURSES.includes(c.id);
  const inPractice = course !== undefined && isPractice(course);
  return (
    <nav id={id} className={`app-sidenav${open ? " is-open" : ""}${hidden ? " is-hidden" : ""}`} aria-label="Sections">
      {top("graph", "#/", "Graph", true)}
      {top("courses", "#/courses", "Courses", route === "/courses", inPractice)}
      {courses?.filter((c) => !isPractice(c)).map(pillar)}
      {top("study", "#/study", "Study", route === "/study")}
      {top("labs", "#/labs", "Labs", route === "/labs")}
      {courses?.some(isPractice) ? (
        <>
          <div className={`sidenav-item sidenav-item--top sidenav-heading${inPractice ? " is-within" : ""}`}>Practice</div>
          {courses.filter(isPractice).map(pillar)}
        </>
      ) : null}
    </nav>
  );
}
