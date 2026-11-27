/**
 * Where dictation may be offered (D10). Browser recognition sends audio to the browser vendor's
 * cloud service, and interviewing answers carry personal history, so that course waits for
 * local Whisper in the conversational tier. Speech synthesis has no such limit: it only reads
 * course text, which is public.
 */
const LOCAL_ONLY_COURSES = new Set(["interviewing"]);

/** Shown beside every microphone. */
export const DICTATION_NOTICE = "Dictation in this browser uses its cloud speech service.";
export const DICTATION_BLOCKED_NOTICE = "Dictation is off in the interviewing course: answers there stay on this machine.";

function decode(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

/** `id` is a course, module, lesson or deck id, as raw or encoded as the hash spells it. */
export function dictationAllowed(id: string): boolean {
  const course = decode(id).split("/").find(Boolean) ?? "";
  return !LOCAL_ONLY_COURSES.has(course.toLowerCase());
}
