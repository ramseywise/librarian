import type { Flashcard, QuizQuestion } from "./types";

/** Questions to go through: only those due or never seen when `dueOnly`, otherwise all in file order. */
export function quizOrder(questions: QuizQuestion[], dueOnly: boolean): QuizQuestion[] {
  return dueOnly ? questions.filter((q) => q.status === "due" || q.status === "new") : questions;
}

export type StudyMode = "all" | "due";

/** To study today: reviewed cards that have come due, plus cards never seen, minus this session's grades. */
export function isToStudy(card: Flashcard, graded: ReadonlySet<string>): boolean {
  return (card.status === "due" || card.status === "new") && !graded.has(card.id);
}

/** Positions in the deck to go through, in deck order. */
export function studyOrder(cards: Flashcard[], mode: StudyMode, graded: ReadonlySet<string>): number[] {
  const all = cards.map((_, i) => i);
  return mode === "all" ? all : all.filter((i) => isToStudy(cards[i], graded));
}
