import type { ReactElement } from "react";
import { act, cleanup, fireEvent, render as rtlRender, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Course, FlashcardDeck, Lesson } from "../../courses/types";
import { resetProgressStoreForTests } from "../../../hooks/useCourseProgress";
import { resetCourseCachesForTests } from "../../../hooks/useCourses";
import { resetLearningForTests } from "../../../hooks/useLearning";
import { FakeRecognition, installFakeRecognition, installFakeSynth } from "../../../test/fakeSpeech";
import { DICTATION_BLOCKED_NOTICE, DICTATION_NOTICE } from "../../../voice/policy";
import { ChatPanel } from "../../ChatPanel";
import { CoursesView } from "../../courses/CoursesView";
import { FlashcardsView } from "../../courses/FlashcardsView";
import { LessonView } from "../../courses/LessonView";

const render = (ui: ReactElement) => rtlRender(ui);
const hold = () => fireEvent.pointerDown(screen.getByRole("button", { name: /Hold to/ }), { button: 0 });
/** Lift the mic after a hold long enough not to be a tap. */
const release = () => {
  vi.spyOn(performance, "now").mockReturnValue(performance.now() + 1000);
  fireEvent.pointerUp(screen.getByRole("button", { name: /release to finish/ }));
};

class FakeObserver {
  observe() {}
  disconnect() {}
  unobserve() {}
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  resetProgressStoreForTests();
  resetCourseCachesForTests();
  resetLearningForTests();
  vi.stubGlobal("IntersectionObserver", FakeObserver);
  Element.prototype.scrollIntoView = vi.fn();
  Element.prototype.scrollTo = vi.fn() as unknown as Element["scrollTo"];
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("chat dictation", () => {
  const setup = (props: { dictationAllowed?: boolean; streaming?: boolean } = {}) => {
    const onSend = vi.fn();
    const utils = render(<ChatPanel messages={[]} onSend={onSend} onClearHighlights={() => {}} {...props} streaming={props.streaming ?? false} />);
    return { onSend, ...utils };
  };
  const box = () => screen.getByLabelText("Ask the librarian") as HTMLTextAreaElement;

  it("offers no mic where the API is absent", () => {
    setup();
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();
    expect(screen.queryByText(DICTATION_NOTICE)).toBeNull();
  });

  it("shows the interim transcript inline and sends on release, with the cloud notice visible", () => {
    installFakeRecognition();
    const { onSend } = setup();
    expect(screen.getByText(DICTATION_NOTICE)).toBeVisible();
    hold();
    FakeRecognition.last.hear("what is ", "a que");
    expect(box().value).toBe("what is a que");
    release();
    expect(onSend).not.toHaveBeenCalled();
    FakeRecognition.last.hear("what is ", "a queue");
    FakeRecognition.last.end();
    expect(onSend).toHaveBeenCalledExactlyOnceWith("what is a queue");
    expect(box().value).toBe("");
  });

  it("adds to what was already typed", () => {
    installFakeRecognition();
    const { onSend } = setup();
    fireEvent.change(box(), { target: { value: "first part" } });
    hold();
    FakeRecognition.last.hear("second part");
    expect(box().value).toBe("first part second part");
    release();
    FakeRecognition.last.end();
    expect(onSend).toHaveBeenCalledExactlyOnceWith("first part second part");
  });

  it.each([
    ["nothing heard", (r: FakeRecognition) => r.end()],
    ["only silence", (r: FakeRecognition) => { r.hear("   "); r.end(); }],
    ["no-speech", (r: FakeRecognition) => { r.fail("no-speech"); }],
  ])("never sends an empty transcript: %s", (_name, finish) => {
    installFakeRecognition();
    const { onSend } = setup();
    hold();
    const rec = FakeRecognition.last;
    release();
    finish(rec);
    expect(onSend).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: /Hold to/ })).toHaveAttribute("aria-pressed", "false");
  });

  it("a session that ended without a release leaves the words to review, unsent", () => {
    installFakeRecognition();
    const { onSend } = setup();
    hold();
    FakeRecognition.last.hear("half a thought");
    FakeRecognition.last.end();
    expect(onSend).not.toHaveBeenCalled();
    expect(box().value).toBe("half a thought");
  });

  it("shows a recognition error and turns the mic off", () => {
    installFakeRecognition();
    setup();
    hold();
    FakeRecognition.last.fail("not-allowed");
    expect(screen.getByRole("alert")).toHaveTextContent(/Microphone access is blocked/);
    expect(screen.getByRole("button", { name: /Hold to/ })).toHaveAttribute("aria-pressed", "false");
  });

  it("offers no mic on a page that does not allow it, says so, and ends a live one", () => {
    installFakeRecognition();
    const { rerender } = setup();
    hold();
    FakeRecognition.last.hear("not for here");
    rerender(<ChatPanel messages={[]} onSend={() => {}} onClearHighlights={() => {}} streaming={false} dictationAllowed={false} />);
    expect(FakeRecognition.last.aborted).toBe(true);
    expect(screen.queryByRole("button", { name: /Hold to|Listening/ })).toBeNull();
    expect(screen.getByText(DICTATION_BLOCKED_NOTICE)).toBeVisible();
    expect(box().value).toBe("");
  });

  it("is disabled while a reply streams", () => {
    installFakeRecognition();
    setup({ streaming: true });
    expect(screen.getByRole("button", { name: /Hold to/ })).toBeDisabled();
  });
});

const deck: FlashcardDeck = {
  id: "c1/m1", title: "Module One", course: "c1",
  cards: [
    { id: "0", front: "What is **first**?", back: "BACK-OF-FIRST", lesson: null, lessonTitle: null },
    { id: "1", front: "What is second?", back: "BACK-OF-SECOND", lesson: null, lessonTitle: null },
  ],
};

function stubDeck(d: FlashcardDeck = deck) {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify(d), { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("flashcard voice", () => {
  const card = () => document.querySelector("button.flashcard")!;
  const shuffleSafe = async () => {
    await screen.findByRole("button", { name: "Next" });
  };

  it("offers nothing where the APIs are absent", async () => {
    stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await shuffleSafe();
    expect(screen.queryByRole("button", { name: /Read question/ })).toBeNull();
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();
  });

  it("reads the front only, on every card and across every flip", async () => {
    const synth = installFakeSynth();
    stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await shuffleSafe();

    await userEvent.click(screen.getByRole("button", { name: /Read question/ }));
    expect(synth.spoken).toMatch(/What is (first|second)\?/);
    expect(synth.spoken).not.toContain("**");
    await userEvent.click(card());
    expect(synth.current).toBeNull(); // flipping stops it
    expect(screen.queryByRole("button", { name: /Read question/ })).toBeNull(); // no way to read while flipped
    await userEvent.click(card());
    await userEvent.click(screen.getByRole("button", { name: /Read question/ }));
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(synth.current).toBeNull(); // the next card stops it
    await userEvent.click(screen.getByRole("button", { name: /Read question/ }));
    synth.drain();

    expect(synth.spoken).not.toContain("BACK-OF");
  });

  it("shows a spoken answer before the reveal, grades nothing and sends nothing", async () => {
    installFakeRecognition();
    const fetchMock = stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await shuffleSafe();
    const calls = fetchMock.mock.calls.length;
    expect(screen.getByText(DICTATION_NOTICE)).toBeVisible();

    hold();
    FakeRecognition.last.hear("my spoken ", "ans");
    expect(screen.getByText(/my spoken ans/)).toBeInTheDocument();
    release();
    FakeRecognition.last.hear("my spoken ", "answer");
    FakeRecognition.last.end();
    expect(screen.getByText(/my spoken answer/)).toBeInTheDocument();
    expect(screen.getByText(/not graded/)).toBeInTheDocument();
    expect(screen.queryByText(/BACK-OF/)).toBeNull();

    await userEvent.click(card());
    expect(screen.getByText(/BACK-OF/)).toBeInTheDocument();
    expect(screen.getByText(/my spoken answer/)).toBeInTheDocument(); // kept to compare
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();

    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.queryByText(/my spoken answer/)).toBeNull(); // does not carry over
    expect(fetchMock.mock.calls.length).toBe(calls);
  });

  it("flipping while listening ends the mic", async () => {
    installFakeRecognition();
    stubDeck();
    render(<FlashcardsView deckId="c1/m1" />);
    await shuffleSafe();
    hold();
    fireEvent.click(card());
    expect(FakeRecognition.last.stopped).toBe(true);
  });

  it.each([
    ["course", { ...deck, course: "interviewing" }],
    ["deck id", { ...deck, id: "interviewing/rounds" }],
  ])("offers no mic in interviewing, by %s, and still reads the front", async (_name, d) => {
    installFakeRecognition();
    installFakeSynth();
    stubDeck(d);
    render(<FlashcardsView deckId={d.id} />);
    await shuffleSafe();
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();
    expect(screen.queryByText(DICTATION_NOTICE)).toBeNull();
    expect(screen.getByRole("button", { name: /Read question/ })).toBeInTheDocument();
  });
});

const lessonBase = {
  section: "", summary: "", course: "c1", module: "c1/m1", source: "", concepts: [], prev: null, next: null,
};
const realShapedDrill: Lesson = {
  ...lessonBase, id: "c1/m1/d", title: "Invented drill", kind: "drill",
  drill: { track: "python", difficulty: "easy", timebox_min: 10 },
  body: `# Invented drill

## Prompt

Build an invented widget.

## Starter

\`\`\`python
def starter_code(): ...
\`\`\`

## Tests

The widget must pass TESTS-SPOILER.

## Hints

<details>
<summary>Hint 1</summary>

HINT-SPOILER

</details>

## Solution

<details>
<summary>Solution: reference approach</summary>

SOLUTION-SPOILER

</details>

## Notes

NOTES-SPOILER
`,
};

function renderLesson(lesson: Lesson) {
  return rtlRender(
    <LessonView lesson={lesson} courseTitle="C" done={false} onMarkDone={vi.fn()} onOpen={vi.fn()}
      onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
  );
}

describe("lesson read-aloud", () => {
  const reading: Lesson = {
    ...lessonBase, id: "c1/m1/l", title: "Reading", kind: "reading",
    body: "Opening words.\n\n## First part\n\nFirst words.\n\n```python\nprint('x')\n```\n\n## Second part\n\nSecond words.",
  };

  it("is hidden where speech is absent", () => {
    renderLesson(reading);
    expect(screen.queryByRole("button", { name: /Read aloud/ })).toBeNull();
    cleanup();
    renderLesson(realShapedDrill);
    expect(screen.queryByRole("button", { name: /Read prompt/ })).toBeNull();
    expect(screen.queryByText(/Read-aloud is off/)).toBeNull();
  });

  it("reads per heading, skips to the next, stops at the end, and never spells code", async () => {
    const synth = installFakeSynth();
    renderLesson(reading);
    await userEvent.click(screen.getByRole("button", { name: /Read aloud/ }));
    expect(synth.current?.text).toBe("Opening words.");
    expect(screen.getByRole("status")).toHaveTextContent("Reading: Reading");
    await userEvent.click(screen.getByRole("button", { name: "Next section" }));
    expect(synth.current?.text).toContain("First part");
    expect(screen.getByRole("status")).toHaveTextContent("Reading: First part");
    await userEvent.click(screen.getByRole("button", { name: "Next section" }));
    expect(synth.current?.text).toContain("Second part");
    await userEvent.click(screen.getByRole("button", { name: "Next section" }));
    expect(synth.current).toBeNull();
    expect(screen.getByRole("button", { name: /Read aloud/ })).toBeInTheDocument();
  });

  it("stop works, and moving to another lesson stops speech", async () => {
    const synth = installFakeSynth();
    const { rerender } = renderLesson(reading);
    await userEvent.click(screen.getByRole("button", { name: /Read aloud/ }));
    await userEvent.click(screen.getByRole("button", { name: /Stop reading/ }));
    expect(synth.current).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: /Read aloud/ }));
    rerender(
      <LessonView lesson={{ ...reading, id: "c1/m1/other" }} courseTitle="C" done={false} onMarkDone={vi.fn()} onOpen={vi.fn()}
        onOpenConcept={vi.fn()} onAsk={vi.fn()} onToc={vi.fn()} onActiveHeading={vi.fn()} />,
    );
    expect(synth.current).toBeNull();
  });

  it("a drill reads its prompt and nothing else, whether or not the solution was revealed", async () => {
    const synth = installFakeSynth();
    renderLesson(realShapedDrill);
    expect(screen.queryByRole("button", { name: /Read aloud/ })).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: "▶ Read prompt" }));
    synth.drain();
    expect(synth.spoken).toBe("Build an invented widget.");
    const reveal = screen.queryByRole("button", { name: "Show solution" });
    if (reveal) await userEvent.click(reveal);
    await userEvent.click(screen.getByRole("button", { name: "▶ Read prompt" }));
    synth.drain();
    expect(synth.spoken).not.toMatch(/SPOILER|starter_code/);
  });

  it("a drill in a shape it cannot recognise reads nothing and says why", () => {
    const synth = installFakeSynth();
    renderLesson({ ...realShapedDrill, body: "## Task\n\nInvented task.\n\n## Walkthrough\n\nSOLUTION-SPOILER" });
    expect(screen.queryByRole("button", { name: /Read/ })).toBeNull();
    expect(screen.getByText(/Read-aloud is off for this drill: it has no Prompt section/)).toBeVisible();
    expect(synth.utterances).toHaveLength(0);
  });

  it("offers no mic on a lesson page at all", () => {
    installFakeRecognition();
    installFakeSynth();
    renderLesson(reading);
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();
  });
});

describe("question bank Listen", () => {
  const bankOutline = { id: "interviewing/rounds/mock/questions", title: "Questions", section: "Mock round", kind: "reading", summary: "" };
  const plainOutline = { id: "interviewing/rounds/mock/overview", title: "Overview", section: "Mock round", kind: "reading", summary: "" };
  const course: Course = {
    id: "interviewing", title: "Interviewing", summary: "", order: 1, lessonCount: 2,
    modules: [{ id: "interviewing/rounds", title: "Rounds", summary: "", order: 1, readings: [], references: [], lessons: [plainOutline, bankOutline] }],
  };
  const bank: Lesson = {
    ...lessonBase, ...bankOutline, course: "interviewing", module: "interviewing/rounds",
    body: '## Q1: "Why invented queues?"\n\n**60-second answer:** Because of order.\n\n## Q2: "What else?"\n\n<!-- x -->\n\n## Collapsed\n\n<details><summary>Q: A hidden one?</summary>\nHIDDEN-ANSWER\n</details>\n\n## Advice\n\nGeneral words.',
  };

  const stub = (lesson: Lesson | null) =>
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      if (url === "/api/courses") return Response.json([course]);
      if (url.startsWith("/api/courses/lessons/")) return lesson ? Response.json(lesson) : new Response("no", { status: 500 });
      if (url === "/api/learning/state") return Response.json({ concepts: {}, modules: {}, lessonsDone: [], catalogReady: true });
      return Response.json([]);
    }));
  const open = () => render(<CoursesView route="interviewing/interviewing/rounds" navigate={vi.fn()} onOpenConcept={vi.fn()} onAsk={vi.fn()} />);
  const listen = () => screen.findByRole("button", { name: "Listen to Mock round: Questions" });

  it("is offered for a bank only, and not where speech is absent", async () => {
    stub(bank);
    open();
    await screen.findByText("Rounds");
    expect(screen.queryByRole("button", { name: /Listen to/ })).toBeNull();
    cleanup();
    installFakeSynth();
    open();
    await listen();
    expect(screen.queryByRole("button", { name: /Listen to Mock round: Overview/ })).toBeNull();
    expect(screen.queryByRole("button", { name: /Hold to/ })).toBeNull();
  });

  it("speaks inside the click, then the bank in two voices, and withholds a collapsed answer", async () => {
    const synth = installFakeSynth();
    stub(bank);
    open();
    await userEvent.click(await listen());
    expect(synth.current?.text).toBe("Mock round.");
    synth.end();
    await waitFor(() => expect(synth.current).not.toBeNull());
    expect(screen.getByText(/only the questions are read/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Next question" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Stop listening to Mock round: Questions" }));
    expect(synth.current).toBeNull();
    expect(synth.spoken).not.toContain("HIDDEN-ANSWER");
  });

  it("speaks nothing of a bank with no questions, and says so", async () => {
    const synth = installFakeSynth();
    stub({ ...bank, body: "# Title\n\nWords only." });
    open();
    await userEvent.click(await listen());
    expect(await screen.findByText(/No questions could be found/)).toHaveAttribute("role", "alert");
    expect(synth.current).toBeNull();
  });

  it("says so when the bank cannot be loaded", async () => {
    installFakeSynth();
    stub(null);
    open();
    await userEvent.click(await listen());
    expect(await screen.findByText(/Could not load this question bank/)).toHaveAttribute("role", "alert");
  });

  it("hash navigation stops it with the page still mounted", async () => {
    const synth = installFakeSynth();
    stub(bank);
    open();
    await userEvent.click(await listen());
    act(() => {
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    expect(synth.current).toBeNull();
    expect(await listen()).toBeInTheDocument();
  });
});
