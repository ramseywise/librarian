/**
 * The hash routes that draw a page over the graph. `parseRoute` is the one place that says which
 * path is which page; `null` means the graph itself (the `/` route and anything unknown).
 */
export type CoursePage =
  | { page: "login" }
  | { page: "admin" }
  | { page: "privacy" }
  | { page: "study" }
  | { page: "slides"; deckId: string }
  | { page: "quiz"; quizId: string }
  | { page: "lab"; labId: string }
  | { page: "labs" }
  | { page: "practice" }
  | { page: "flashcards"; deckId: string }
  | { page: "courses"; path: string };

const after = (route: string, prefix: string) => route.slice(prefix.length);

export function parseRoute(route: string): CoursePage | null {
  if (route === "/login" || route.startsWith("/login?")) return { page: "login" };
  if (route === "/admin") return { page: "admin" };
  if (route === "/privacy") return { page: "privacy" };
  if (route === "/study") return { page: "study" };
  if (route.startsWith("/slides/")) return { page: "slides", deckId: after(route, "/slides/") };
  if (route.startsWith("/quiz/")) return { page: "quiz", quizId: after(route, "/quiz/") };
  if (route.startsWith("/labs/") && route.length > "/labs/".length) return { page: "lab", labId: after(route, "/labs/") };
  if (route === "/labs" || route.startsWith("/labs/")) return { page: "labs" };
  if (route === "/practice") return { page: "practice" };
  if (route.startsWith("/flashcards/")) return { page: "flashcards", deckId: after(route, "/flashcards/") };
  if (route === "/courses" || route.startsWith("/courses/")) return { page: "courses", path: route.replace(/^\/courses\/?/, "") };
  return null;
}
