/**
 * Wire shapes of the account, admin, feedback, citation and wiki-health routes
 * (`librarian.api.routers.account`, `feedback`, `chat`, `auth`, `wiki_health`).
 */
import { z } from "zod";

export const loginMethodSchema = z.enum(["google", "github", "email"]);

/** GET /api/auth/config. `open`: no token and no login configured, so everyone is the owner (local use). */
export const authConfigSchema = z.object({ methods: z.array(loginMethodSchema), open: z.boolean() });

/** GET /api/me. The server also sends `progress` and `intake`; the client does not read them. */
export const meSchema = z.object({
  id: z.string(),
  email: z.string(),
  name: z.string().nullable(),
  role: z.enum(["admin", "member"]),
  timezone: z.string(),
  scopes: z.array(z.string()),
  /** Active experiment variant for this user; may be empty. */
  experiment: z.string().optional(),
  chat: z.object({ spent_today_usd: z.number(), daily_budget_usd: z.number().nullable() }),
});

/** GET /api/admin/users. */
export const adminUserSchema = z.object({
  id: z.string(),
  email: z.string(),
  name: z.string().nullable(),
  role: z.enum(["admin", "member"]),
  last_seen_at: z.string().nullable(),
  chat_spent_today_usd: z.number(),
});
export const adminUsersSchema = z.array(adminUserSchema);

/** GET /api/admin/invites. */
export const inviteSchema = z.object({
  email: z.string(),
  created_at: z.string().nullable(),
  used_at: z.string().nullable(),
});
export const invitesSchema = z.array(inviteSchema);

/** POST /api/admin/invites. */
export const inviteResultSchema = z.object({ email: z.string(), added: z.boolean() });

/** GET /api/admin/audit. */
export const auditEventSchema = z.object({
  ts: z.string().nullable(),
  email: z.string().nullable(),
  action: z.string(),
  target: z.string().nullable(),
});
export const auditEventsSchema = z.array(auditEventSchema);

/** GET /api/feedback/mine. The server also sends `release` and `experiment`. */
export const myFeedbackSchema = z.object({
  id: z.string(),
  ts: z.string(),
  kind: z.string(),
  target: z.string(),
  rating: z.number().nullable(),
  body: z.string().nullable(),
});
export const myFeedbackListSchema = z.array(myFeedbackSchema);

/** POST /api/feedback. */
export const feedbackCreatedSchema = z.object({ id: z.string() });

/** One row of a reader-feedback list; which fields are set depends on the list. */
export const feedbackSummaryRowSchema = z.object({
  target: z.string(),
  count: z.number().optional(),
  notes: z.array(z.string()).optional(),
  misses: z.number().optional(),
  miss_rate: z.number().optional(),
  read: z.number().optional(),
  cited: z.number().optional(),
  ungrounded: z.number().optional(),
});
/** GET /api/admin/feedback/summary: signal name → its top rows. */
export const feedbackSummarySchema = z.record(z.string(), z.array(feedbackSummaryRowSchema));

/** POST /api/chat/citations/check: one entry per citation sent, in order. */
export const citationCheckSchema = z.object({
  citations: z.array(
    z.object({ id: z.string(), status: z.enum(["current", "changed", "missing"]), now: z.string().optional() }),
  ),
});

/** GET /api/wiki/health: the newest telemetry row. `date` is null when there is none yet. */
export const healthSnapshotSchema = z.object({
  date: z.string().nullable(),
  metrics: z.record(z.string(), z.object({ value: z.number(), status: z.string() })),
});
