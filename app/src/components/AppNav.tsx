import { useEffect } from "react";
import { useCourseProgress } from "../hooks/useCourseProgress";
import { useCourses } from "../hooks/useCourses";
import { Check } from "./courses/Check";
import type { CourseModule } from "./courses/types";

type Section = "graph" | "courses" | "study" | "labs" | null;

function sectionOf(route: string): Section {
  if (route === "/" || route === "") return "graph";
  if (/^\/(courses|slides)(\/|$)/.test(route)) return "courses";
  if (/^\/(study|quiz|flashcards)(\/|$)/.test(route)) return "study";
  if (/^\/(labs|practice)(\/|$)/.test(route)) return "labs";
  return null;
}

/** The one navigation for the whole app: Graph, Courses, Study and Labs, with the courses listed under Courses.
 * Nothing in it opens or closes by hand: the course being read shows its modules, and the module being read
 * shows its lessons. */
export function AppNav({ route, open, id }: { route: string; open: boolean; id: string }) {
  const { data: courses } = useCourses();
  const section = sectionOf(route);
  // `/courses/<course>[/<module>[/...]]` and `/slides/<course>/<module>[/<lecture>]` both start with the course.
  const path = section === "courses" ? route.replace(/^\/(courses|slides)\/?/, "").split("?")[0] : "";
  const course = path ? courses?.find((c) => path === c.id || path.startsWith(`${c.id}/`)) : undefined;
  const moduleOf = (m: CourseModule) => `${course?.id}/${m.id}`;
  const module = course?.modules.find(
    (m) => path === moduleOf(m) || path.startsWith(`${moduleOf(m)}/`) || m.lessons.some((l) => l.id === path),
  );

  const top = (name: Exclude<Section, null>, href: string, label: string, exact: boolean) => (
    <a
      href={href}
      className={`sidenav-item sidenav-item--top${section === name && !exact ? " is-within" : ""}`}
      aria-current={section === name && exact ? "page" : undefined}
    >
      {label}
    </a>
  );

  return (
    <nav id={id} className={`app-sidenav${open ? " is-open" : ""}`} aria-label="Sections">
      {top("graph", "#/", "Graph", true)}
      {top("courses", "#/courses", "Courses", route === "/courses")}
      {courses?.map((c) => (
        <div key={c.id}>
          <a
            href={`#/courses/${c.id}`}
            className={`sidenav-item sidenav-item--course${c === course && path !== c.id ? " is-within" : ""}`}
            aria-current={path === c.id ? "page" : undefined}
          >
            {c.title}
          </a>
          {c === course && c.modules.map((m) => (
            <div key={m.id}>
              <a
                href={`#/courses/${c.id}/${m.id}`}
                className={`sidenav-item sidenav-item--module${m === module && path !== moduleOf(m) ? " is-within" : ""}`}
                aria-current={path === moduleOf(m) ? "page" : undefined}
              >
                {m.title}
              </a>
              {m === module && <NavLessons module={m} activeId={path} />}
            </div>
          ))}
        </div>
      ))}
      {top("study", "#/study", "Study", route === "/study")}
      {top("labs", "#/labs", "Labs", route === "/labs")}
    </nav>
  );
}

/** The lessons of the module being read, under their section headings, with what is done ticked. */
function NavLessons({ module: m, activeId }: { module: CourseModule; activeId: string }) {
  const { done } = useCourseProgress();
  useEffect(() => {
    document.getElementById(`nav-${activeId}`)?.scrollIntoView?.({ block: "nearest" });
  }, [activeId]);
  let prevSection = "";
  return (
    <>
      {m.lessons.map((l) => {
        const header = l.section && l.section !== prevSection ? l.section : null;
        prevSection = l.section;
        return (
          <div key={l.id}>
            {header && <div className="sidenav-section">{header}</div>}
            <a
              id={`nav-${l.id}`}
              href={`#/courses/${l.id}`}
              className="sidenav-item sidenav-item--lesson"
              aria-current={l.id === activeId ? "page" : undefined}
            >
              <Check on={done.has(l.id)} small />
              <span className="grow">{l.title}</span>
            </a>
          </div>
        );
      })}
    </>
  );
}
