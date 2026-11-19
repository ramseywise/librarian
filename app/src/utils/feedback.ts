import type { z } from "zod";
import { feedbackCreatedSchema, type myFeedbackSchema } from "../schemas/account";
import { apiFetch, postJson } from "./api";

export type FeedbackKind = "answer" | "page" | "lesson";
export const MAX_NOTE = 2000;

export interface FeedbackInput {
  kind: FeedbackKind;
  target: string;
  rating?: 1 | -1;
  body?: string;
}

export type MyFeedback = z.output<typeof myFeedbackSchema>;

/** POST /api/feedback. Returns the new row id; throws ApiError on failure. */
export async function sendFeedback(input: FeedbackInput): Promise<string> {
  const r = await postJson(feedbackCreatedSchema, "/api/feedback", input);
  return r.id;
}

/** DELETE /api/feedback/{id}. Throws on a non-2xx answer. */
export async function deleteFeedback(id: string): Promise<void> {
  const resp = await apiFetch(`/api/feedback/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
}
