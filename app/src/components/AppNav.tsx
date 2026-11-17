import { useCourses } from "../hooks/useCourses";
import type { CourseModule } from "./courses/types";

type Section = "graph" | "courses" | "study" | "labs" | null;

function sectionOf(route: string): Section {
  if (route === "/" || route === "") return "graph";
  if (/^\/(courses|slides)(\/|$)/.test(route)) return "courses";
  if (/^\/(study|quiz|flashcards)(\/|$)/.test(route)) return "study";
  if (/^\/(labs|practice)(\/|$)/.test(route)) return "labs";
  return null;
}

/** The one navigation for the whole app: Graph, Study, Labs and Courses. Courses comes last because each
 * course follows it as a group label over its modules, with the lesson count beside each; the module being
 * read is the filled row, and "Core" and "Advanced" head the modules of a course that sorts them. A module with
 * no lessons is left out. Lessons are not listed here, they are on the
 * module's page. */
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
      {top("study", "#/study", "Study", route === "/study")}
      {top("labs", "#/labs", "Labs", route === "/labs")}
      {top("courses", "#/courses", "Courses", route === "/courses")}
      {courses?.map((c) => (
        <div key={c.id} className="sidenav-group" role="group" aria-label={c.title}>
          <a
            href={`#/courses/${c.id}`}
            className={`sidenav-label${c === course && path !== c.id ? " is-within" : ""}`}
            aria-current={path === c.id ? "page" : undefined}
          >
            {c.title}
          </a>
          {c.modules.filter((m) => m.lessons.length > 0 || m === module).map((m, i, shown) => [
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
              <span className="sidenav-count" title={`${m.lessons.length} lessons`} aria-hidden="true">{m.lessons.length}</span>
            </a>,
          ])}
        </div>
      ))}
    </nav>
  );
}
