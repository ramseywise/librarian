import { describe, expect, it } from "vitest";
import { parseRoute } from "../routes";

describe("parseRoute", () => {
  it("leaves the graph to `/` and anything unknown", () => {
    for (const r of ["/", "", "/nope", "/course", "/studies"]) expect(parseRoute(r), r).toBeNull();
  });

  it("maps the fixed pages", () => {
    expect(parseRoute("/login")).toEqual({ page: "login" });
    expect(parseRoute("/login?next=%2Fcourses")).toEqual({ page: "login" });
    expect(parseRoute("/admin")).toEqual({ page: "admin" });
    expect(parseRoute("/privacy")).toEqual({ page: "privacy" });
    expect(parseRoute("/study")).toEqual({ page: "study" });
    expect(parseRoute("/practice")).toEqual({ page: "practice" });
  });

  it("takes the id after a prefix", () => {
    expect(parseRoute("/slides/ai/deck")).toEqual({ page: "slides", deckId: "ai/deck" });
    expect(parseRoute("/quiz/ai/m/l")).toEqual({ page: "quiz", quizId: "ai/m/l" });
    expect(parseRoute("/flashcards/ai/m")).toEqual({ page: "flashcards", deckId: "ai/m" });
  });

  it("tells a lab from the lab list", () => {
    expect(parseRoute("/labs")).toEqual({ page: "labs" });
    expect(parseRoute("/labs/")).toEqual({ page: "labs" });
    expect(parseRoute("/labs/importance-noise")).toEqual({ page: "lab", labId: "importance-noise" });
  });

  it("gives the course path without its prefix", () => {
    expect(parseRoute("/courses")).toEqual({ page: "courses", path: "" });
    expect(parseRoute("/courses/")).toEqual({ page: "courses", path: "" });
    expect(parseRoute("/courses/ai/rag/l1")).toEqual({ page: "courses", path: "ai/rag/l1" });
  });
});
