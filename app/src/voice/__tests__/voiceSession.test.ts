import { describe, expect, it } from "vitest";
import { coachSaid, EMPTY_VIEW, endText, serverSaid, ungradedText, userSaid } from "../voiceSession";

describe("the transcript", () => {
  it("replaces an interim line and keeps a final one", () => {
    let view = userSaid(EMPTY_VIEW, "two pointers", false);
    view = userSaid(view, "two pointers from both ends", true);
    view = userSaid(view, "and then", false);
    expect(view.lines.map((l) => (l.kind === "you" ? l.text : ""))).toEqual(["two pointers from both ends", "and then"]);
  });

  it("joins the coach's sentences until something else is said", () => {
    let view = coachSaid(EMPTY_VIEW, "One.");
    view = coachSaid(view, "Two.");
    view = userSaid(view, "Yes", true);
    view = coachSaid(view, "Three.");
    expect(view.lines).toEqual([
      { kind: "coach", text: "One. Two." },
      { kind: "you", text: "Yes", final: true },
      { kind: "coach", text: "Three." },
    ]);
  });
});

describe("messages from the voice server", () => {
  it("shows a grade", () => {
    expect(serverSaid(EMPTY_VIEW, { type: "grade", score: 0.75 }).lines).toEqual([{ kind: "graded", score: 0.75 }]);
  });

  it.each([[-0.1], [1.5], ["0.5"], [null], [Number.NaN]])("drops a grade of %s rather than showing it", (score) => {
    expect(serverSaid(EMPTY_VIEW, { type: "grade", score })).toEqual(EMPTY_VIEW);
  });

  it("makes an ungraded turn a visible line, with a reason", () => {
    const view = serverSaid(EMPTY_VIEW, { type: "ungraded", reason: "malformed" });
    expect(view.lines).toEqual([{ kind: "ungraded", reason: "malformed" }]);
    expect(ungradedText("malformed")).toMatch(/Not graded: .*malformed/);
    expect(ungradedText("anything new")).toMatch(/^Not graded/);
  });

  it("keeps latency as numbers and blanks anything else", () => {
    const view = serverSaid(EMPTY_VIEW, { type: "latency", turn: 2, gap_ms: 901.9, stt_ms: "fast" });
    expect(view.latency[0]).toMatchObject({ turn: 2, gap_ms: 901.9, stt_ms: null, llm_first_ms: null });
  });

  it("explains an ending, with or without the server's own text", () => {
    expect(serverSaid(EMPTY_VIEW, { type: "ended", reason: "turn_cap" }).ended).toMatch(/turn limit/);
    expect(endText("idle", "From the server.")).toBe("From the server.");
    expect(endText("never heard of it")).toBe("Session ended.");
  });

  it.each([[null], ["text"], [{ type: "unknown" }], [{}]])("ignores %j", (message) => {
    expect(serverSaid(EMPTY_VIEW, message)).toBe(EMPTY_VIEW);
  });
});
