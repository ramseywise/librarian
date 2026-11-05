---
name: quiz
description: "Test what you actually retained from wiki pages. Asks questions from named pages or a domain, half recall and half application, grades each answer against the page, and reports problems found in the pages. Read-only: problems are reported, never fixed. Use when asked to quiz me, test me on a wiki page or domain, or check what I remember from the wiki. Do NOT use for answering a question from the wiki (/query), authoring drills or interview rounds (/practice), studying course flashcards, reviewing course content (/review), or wiki health checks (/lint)."
allowed-tools:
  - Read
  - Glob
  - Grep
---

You are quizzing Ramsey from his own wiki pages. The page is the answer key, not your general knowledge of the subject.

## Core rule

Every question comes from a page that was opened, every grade is against what that page says, and no file is changed.

## Workflow

`$ARGUMENTS` is page names, a domain (a directory under `data/wiki/`), or both. Empty: ask which, and stop until told.

1. **Pick the pages.** For a domain, list `data/wiki/<domain>/` and take up to five, preferring pages with `updated` furthest back. Never open `data/wiki/private/`: if the request names a page there, say private pages are out of scope for this skill and carry on with the rest. Skip tombstones and files starting with `_`.

2. **Read each page in full.** If a page cannot be read, say so and leave it out.

3. **Write the questions.** Six by default, or the number asked for, with at most one per named section. Half are `[recall]`: what does the page state. Half are `[application]`: use the page's idea on a new case the page does not describe. With an odd number, the extra one is application. Each question names its page, so the answer can be checked afterwards.

4. **Print the questions and stop.** Do not show answers. Wait for the replies.

5. **Grade against the page.** `correct`, `partial` or `wrong`, each with what the page says. If the answer is right about the world and the page says otherwise, grade it `wrong` and put the disagreement under `Page problems found`. A skipped question is `wrong`.

6. **Check the pages for problems.** While grading, note each of these:
   - `vague`: the page's wording could not settle a grade, or could not support an application question.
   - `unsupported`: a claim used in a question is not in any file in the page's `sources:`. Open only the sources for claims the quiz used.
   - `copied`: a run of 8 or more consecutive words is shared with a source, not counting names, code and marked quotations.

   If a source file is missing, write `not checked (source unavailable)` for that claim, not a verdict.

7. **Report and stop.** Do not edit the page, do not offer to fix it in this run, and do not log anything. `/ingest` or a normal edit session is where a fix happens.

## Output format

Print the first block, wait for the answers, then print the second.

```
Quiz: <n> questions from <n> pages

1. [recall] <question> (→ [[Page]])
2. [application] <question> (→ [[Page]])
```

```
Results: <n> correct, <n> partial, <n> wrong

1. <correct | partial | wrong>: <what the page says> (→ [[Page]])
2. <correct | partial | wrong>: <what the page says> (→ [[Page]])

Reread: [[Page]], [[Page]]
Page problems found:
- [[Page]] — vague: <the wording that could not settle it>
- [[Page]] — unsupported: <the claim>, not in <source path>
- [[Page]] — copied: <the first few words of the run>, from <source path>
- [[Page]] — not checked (source unavailable): <the claim>
```

`Reread` lists the pages behind partial and wrong answers, or `none`. `Page problems found:` is followed by `none` when there are none. It is never omitted.

## Calibration

Too easy is the common failure: recall questions that repeat a page's heading test recognition, and a clean score means nothing. An application question should need the page's mechanism, on a case the page does not mention. Too hard is the opposite failure: a question the page cannot settle grades Ramsey on your general knowledge. If you could not write the expected answer from the page alone, drop the question.

Six questions over one to five pages is one sitting. Twenty questions over a whole domain is a job nobody finishes, so narrow the scope instead.

A long list of page problems is not the goal. Report what the quiz actually ran into: a full audit of a page is `/lint` and `ingest-reviewer` work. Zero problems is a fine result when nothing got in the way.
