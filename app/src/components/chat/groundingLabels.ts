// Wording of the grounding line, in one place so it can be changed without touching the logic.
export const SOURCES_LABEL = "sources";
export const UNGROUNDED_LABEL = "cited but not read";
/** The cited page was read, but the claim beside the citation was not found in it by the
 * quote/overlap check. Placeholder wording: the owner chooses the final text. */
export const UNSUPPORTED_LABEL = "read, support not found";
/** The cited page has other content now than when the answer was written. */
export const CHANGED_LABEL = "changed since this answer";
/** The cited page was deleted (or made private) after the answer was written. */
export const MISSING_LABEL = "no longer exists";
