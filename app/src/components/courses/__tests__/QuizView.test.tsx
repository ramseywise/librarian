import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Quiz } from "../types";
import { quizOrder } from "../studyQueue";
import { QuizView } from "../QuizView";

const quiz: Quiz = {
  id: "c1/m1",
  title: "Module One",
  course: "c1",
  dueCount: 1,
  newCount: 1,
  questions: [
    { id: "q1", prompt: "Pick b", options: ["a", "b", "c"], lesson: "c1/m1/intro", lessonTitle: "Intro", box: 2, dueOn: "2020-01-01", status: "due" },
    { id: "q2", prompt: "Pick x", options: ["x", "y"], lesson: null, lessonTitle: null, box: null, dueOn: null, status: "new" },
    { id: "q3", prompt: "Later one", options: ["m", "n"], lesson: null, lessonTitle: null, box: 4, dueOn: "2099-01-01", status: "later" },
  ],
};

const answers: Record<string, { correct: boolean; answer: string; explanation: string; logged: boolean }> = {
  q1: { correct: true, answer: "b", explanation: "B is right.", logged: true },
  q2: { correct: false, answer: "x", explanation: "", logged: true },
};

function stub(over: Partial<Quiz> = {}, status = 200) {
  const fetchMock = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(async (_url, init) => {
    if (init?.method === "POST") {
      const { question } = JSON.parse(String(init.body)) as { question: string };
      return new Response(JSON.stringify(answers[question]));
    }
    return new Response(JSON.stringify({ ...quiz, ...over }), { status });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("quizOrder", () => {
  it("keeps due and new questions when asked for them, else all", () => {
    expect(quizOrder(quiz.questions, true).map((q) => q.id)).toEqual(["q1", "q2"]);
    expect(quizOrder(quiz.questions, false)).toHaveLength(3);
  });
});

describe("QuizView", () => {
  it("fetches the quiz and shows the first question without any answer", async () => {
    const fetchMock = stub();
    render(<QuizView quizId="c1/m1" />);
    expect(await screen.findByText("Pick b")).toBeInTheDocument();
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/quiz/c1/m1");
    expect(screen.getAllByRole("button", { pressed: false })).toHaveLength(3);
    expect(screen.getByText("1 of 3")).toBeInTheDocument();
    expect(screen.queryByText("B is right.")).toBeNull();
  });

  it("sends the choice for grading and shows the verdict, explanation and source lesson", async () => {
    const user = userEvent.setup();
    const fetchMock = stub();
    render(<QuizView quizId="c1/m1" />);
    await screen.findByText("Pick b");
    await user.click(screen.getByRole("button", { name: "b" }));
    expect(fetchMock).toHaveBeenCalledWith("/api/courses/quiz-results", expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ quiz: "c1/m1", question: "q1", choice: "b" }),
    }));
    expect(await screen.findByText("Correct.")).toBeInTheDocument();
    expect(screen.getByText("B is right.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Intro" })).toHaveAttribute("href", "#/courses/c1/m1/intro");
    // Locked after answering.
    expect(screen.getByRole("button", { name: "a" })).toBeDisabled();
  });

  it("a wrong answer names the right one, Next moves on, and the end shows the score", async () => {
    const user = userEvent.setup();
    stub();
    render(<QuizView quizId="c1/m1?due" />);
    await screen.findByText("Pick b");
    await user.click(screen.getByRole("button", { name: "b" }));
    await user.click(await screen.findByRole("button", { name: "Next" }));
    expect(screen.getByText("Pick x")).toBeInTheDocument();
    expect(screen.getByText("2 of 2")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "y" }));
    expect(await screen.findByText("Not quite.")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("The answer is x.");
    await user.click(screen.getByRole("button", { name: "Finish" }));
    expect(screen.getByText("Done: 1 of 2 right.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "All 3 questions" }));
    expect(screen.getByText("1 of 3")).toBeInTheDocument();
  });

  it("?due leaves out the questions that are not due", async () => {
    const fetchMock = stub();
    render(<QuizView quizId="c1/m1?due" />);
    await screen.findByText("Pick b");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/courses/quiz/c1/m1");
    expect(screen.getByText("1 of 2")).toBeInTheDocument();
  });

  it("lets the learner retry when the answer could not be saved", async () => {
    const user = userEvent.setup();
    const fetchMock = stub();
    render(<QuizView quizId="c1/m1" />);
    await screen.findByText("Pick b");
    fetchMock.mockRejectedValueOnce(new Error("offline"));
    await user.click(screen.getByRole("button", { name: "a" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("not saved");
    expect(screen.getByRole("button", { name: "b" })).toBeEnabled();
  });

  it("says so when there is no quiz", async () => {
    stub({}, 404);
    render(<QuizView quizId="c1/nope" />);
    expect(await screen.findByText("No quiz here")).toBeInTheDocument();
  });
});
