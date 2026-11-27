import { describe, expect, it } from "vitest";
import { bankToSegments, isQuestionBank, parseQuestionBank, withheldNote } from "../questionBank";
import { dictationAllowed } from "../policy";

const LABELLED = `# Round questions

Some preamble that is no question.

## Group of questions

### Q1: "Why do you like invented queues?"

**What they're testing:** spoiled-signal words.

**60-second answer:** Because they are orderly.

**One level deeper:** They also back off.

**Red flags:** rambling words.

### Q2: What is a made-up cache?

**Model answer structure:**

1. It stores things.
2. It forgets things.

### A narrative section with no questions

Just some advice words.

## Sources

- A link somewhere
`;
const COLLAPSED = `# Bank

## Part one

<details>
<summary><b>Q: What does an invented index do?</b></summary>

It finds the hidden row.

</details>

<details><summary>Q: What is a fictional join?</summary>
Hidden join words.
</details>
`;
const MCQ = `# Bank

## Section A

### A1

Which invented shape is round?

- A) Square
- B) Circle

### A2

Which is three-sided?

- A) Triangle
- B) Line

**Answers A1-A2** B A

**Rationale notes**

Hidden rationale words.
`;

describe("parseQuestionBank", () => {
  it("pairs questions with their labelled answers and skips the coaching around them", () => {
    const { exchanges, unparsed } = parseQuestionBank(LABELLED);
    expect(exchanges).toHaveLength(2);
    expect(exchanges[0].question).toBe("Why do you like invented queues?");
    expect(exchanges[0].answer).toContain("Because they are orderly.");
    expect(exchanges[0].answer).toContain("They also back off.");
    expect(exchanges[0].answer).not.toMatch(/spoiled-signal|rambling/);
    expect(exchanges[1].question).toBe("What is a made-up cache?");
    expect(exchanges[1].answer).toContain("It forgets things.");
    expect(unparsed).toEqual(["A narrative section with no questions", "Sources"]);
  });

  it("withholds collapsed answers", () => {
    const bank = parseQuestionBank(COLLAPSED);
    expect(bank.exchanges.map((e) => e.question)).toEqual(["What does an invented index do?", "What is a fictional join?"]);
    expect(bank.exchanges.every((e) => e.answer === null && e.withheld === "collapsed")).toBe(true);
    expect(JSON.stringify(bank)).not.toMatch(/hidden/i);
    expect(withheldNote(bank)).toMatch(/collapsed/);
  });

  it("withholds an MCQ answer key and its rationale", () => {
    const bank = parseQuestionBank(MCQ);
    expect(bank.exchanges).toHaveLength(2);
    expect(bank.exchanges[0].question).toContain("Which invented shape is round?");
    expect(bank.exchanges[1].question).toContain("Triangle");
    expect(JSON.stringify(bank)).not.toMatch(/Rationale|Hidden|B A/);
    expect(withheldNote(bank)).toMatch(/answer key/);
  });

  it("finds nothing in a page with no question shape", () => {
    expect(parseQuestionBank("# Title\n\nJust words.\n\n## Part\n\nMore words.")).toEqual({ exchanges: [], unparsed: ["Part"] });
  });
});

describe("bankToSegments", () => {
  it("gives each role its label and keeps a question and its answer in one skip group", () => {
    const segments = bankToSegments(parseQuestionBank(LABELLED));
    expect(segments.map((s) => [s.role, s.label, s.group])).toEqual([
      ["interviewer", "Question", 0],
      ["candidate", "Answer", 0],
      ["interviewer", "Question", 1],
      ["candidate", "Answer", 1],
    ]);
    expect(segments[0].groupLabel).toBe("Question 1 of 2");
  });

  it("leaves thinking time after a question with a withheld answer, and says why first", () => {
    const [note, first] = bankToSegments(parseQuestionBank(COLLAPSED));
    expect(note.text).toMatch(/only the questions/);
    expect(note.group).toBeUndefined();
    expect(first.pauseAfterMs).toBeGreaterThan(2000);
  });
});

describe("isQuestionBank", () => {
  it.each<[string, string, boolean]>([
    ["interviewing/rounds/behavioral/questions", "reading", true],
    ["interviewing/rounds/technical-questions/mcq-bank", "reading", true],
    ["interviewing/rounds/behavioral/overview", "reading", false],
    ["programming/x/questions", "reading", false],
    ["interviewing/rounds/behavioral/questions", "drill", false],
  ])("%s as %s: %s", (id, kind, expected) => {
    expect(isQuestionBank({ id, kind: kind as "reading" })).toBe(expected);
  });
});

describe("dictationAllowed", () => {
  it.each<[string, boolean]>([
    ["interviewing", false],
    ["interviewing/rounds/behavioral/questions", false],
    ["/interviewing/rounds", false],
    ["Interviewing/rounds", false],
    ["interviewing%2Frounds", false],
    ["%69nterviewing/rounds", false],
    ["programming/drills", true],
    ["interviewing-adjacent/x", true],
  ])("%s: %s", (id, allowed) => {
    expect(dictationAllowed(id)).toBe(allowed);
  });
});
