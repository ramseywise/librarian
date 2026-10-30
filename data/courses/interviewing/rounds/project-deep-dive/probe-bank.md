---
imported_hash: 9c5e3c346cbf08b8
title: Project deep-dive probe bank
summary: 'The questions that pull a project apart: design choices, failures, metrics, ownership.'
order: 61
kind: reading
section: Project deep dive
source: sisyphus/interviewing/rounds/project-deep-dive/probe-bank.md
---

# Project deep-dive probe bank

The questions that pull a project apart: design choices, failures, metrics, ownership.

Source: [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym), converted 2026-10-29. Coaching material only —
the gym's sample answers are someone else's career and are deliberately not carried over.
Every answer you rehearse must trace to `jobs/materials/evidence/evidence-store.md`.

## project

### Walk me through a project you're proud of, end-to-end — what problem it solved and how the whole system fits together

`architecture-walkthrough` · easy

**Probes** — the follow-ups to expect

- What business problem were you solving, and who was the customer or user?
- What was your actual role, and what did you personally build versus the team?
- Trace one request or data flow from input to output through each component.
- Where does the model or core logic sit, and what feeds it context?
- Which single component was the riskiest, and why?

**What a strong answer does**

- Architecture is clear: names the components and how a request flows end-to-end, without losing the listener
- Frames around the business problem and impact first, not a list of tools
- Makes the candidate's own ownership and role explicit
- Can go one level deeper on any component when probed
- Cites at least one concrete metric (users served, latency, adoption, resolution rate)

<details><summary>Hints</summary>

- Start with the problem and the user before any technology. What breaks if this doesn't exist?
- Trace one single request from input to output. Name each hop.
- End on the outcome with a number, not a tool list.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real project details at runtime.
1. Business problem: who had the pain, why the old way fell short.
2. Solution at a high level: the end-to-end structure in one breath.
3. Request trace: input -> core processing -> output.
4. Your role: the pieces you personally owned and decided.
5. Outcome: one metric that shows it worked.
```

</details>

### Tell me about a nasty bug or production incident on your project — how did you find it and fix it?

`debugging-incident` · medium

**Probes** — the follow-ups to expect

- What was the symptom, and how did you first notice it?
- How did you form and test a hypothesis about the root cause?
- What tools or signals (logs, metrics, traces, reproduction) did you use?
- What was the fix, and how did you verify it actually worked?
- What did you change afterward so it couldn't happen again?

**What a strong answer does**

- Describes a clear debugging method: symptom -> hypothesis -> isolation -> root cause -> fix
- Names the concrete tools and signals used, not just 'I looked into it'
- Shows the candidate personally drove the investigation
- Verifies the fix with evidence, not assumption
- Reflects honestly: a prevention or systemic improvement that followed

<details><summary>Hints</summary>

- Lead with the symptom and blast radius, then narrate how you narrowed it down.
- Name the specific signal that cracked it (a log line, a metric spike, a repro).
- End with the guardrail you added so it never recurs.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real incident at runtime.
1. Symptom: what broke, who was affected, how you noticed.
2. Investigation: hypotheses you formed and how you isolated the cause.
3. Root cause: the actual bug, stated precisely.
4. Fix + verification: what you changed and how you confirmed it.
5. Prevention: the test, alert, or design change you added after.
```

</details>

### Why did you pick that design and tech stack for your project over the alternatives you considered?

`design-vs-alternatives` · medium

**Probes** — the follow-ups to expect

- What alternatives did you seriously consider and reject?
- What was the deciding constraint — latency, cost, team skill, time, or data?
- What would have made you pick a different option?
- Where did you follow a convention versus deviate, and why?
- Which choice are you least sure about in hindsight?

**What a strong answer does**

- Explains the reasoning behind the choice, not just the name of the tool
- Names concrete alternatives that were considered and rejected
- Ties the decision to a real constraint (cost, latency, team, data, time)
- Shows engineering judgment: 'we chose X over Y because Z' framing
- Acknowledges uncertainty honestly where it exists

<details><summary>Hints</summary>

- Never just name the tool — say what you rejected and why.
- Anchor on the one constraint that actually forced the decision.
- Use the 'X over Y because Z' shape for at least one choice.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real design rationale at runtime.
1. The choice: what you built and the key stack decisions.
2. Alternatives: the options you weighed and set aside.
3. Deciding constraint: the factor that broke the tie.
4. Judgment: 'X over Y because Z' for the load-bearing decision.
5. Honesty: the choice you're least certain about.
```

</details>

### How did you evaluate your project and measure success — was there a real eval framework, or was it vibes-based? What metrics did you track?

`evaluation` · hard

**Probes** — the follow-ups to expect

- What was your test or golden set, and how did you build it?
- Which metrics did you track, and why those?
- Did you use any automated or LLM-as-judge scoring, and how did you trust it?
- How did you catch a regression before it reached users?
- How did you monitor quality post-deployment for drift or degradation?

**What a strong answer does**

- Describes a real evaluation approach, not 'it looked good', using an offline set and/or online signal
- Names specific metrics tied to the project's goal, not generic ones
- Cites actual numbers or outcomes where possible
- Addresses regression detection and post-deploy monitoring, not just a one-time check
- Acknowledges limits of the eval (bias, small set), an honest self-assessment

<details><summary>Hints</summary>

- Separate offline eval (a fixed test set) from online signal (real user behavior).
- Name at least one quality metric and one business/impact metric.
- Say how you'd know if quality drifted after launch.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real eval details at runtime.
1. Offline: how you built a test/golden set and what you scored on it.
2. Metrics: the quality metric + the impact metric that mattered.
3. Online: the feedback signal you watched in production.
4. Regression + drift: how you caught problems before/after launch.
5. Honest caveat: where the eval was weak.
```

</details>

### What was the hardest technical trade-off you made on your project, and are you still comfortable with it?

`hardest-tradeoff` · hard

**Probes** — the follow-ups to expect

- What alternatives did you weigh, and what was the constraint forcing a choice?
- What did that choice cost you — latency, complexity, cost, or flexibility?
- How did you decide: with data, a prototype, or a judgment call?
- Are you still comfortable with it today, or would something change your mind?
- How did you explain the decision to teammates or stakeholders?

**What a strong answer does**

- Names a concrete, specific trade-off (not a generic 'speed vs quality')
- Explains the 'why' behind the decision and the alternative that was rejected
- Quantifies the cost or benefit with a metric where possible (latency, cost, SLA)
- Shows honest self-assessment: still comfortable, or would revisit, and why
- Demonstrates the candidate drove the decision, not just executed it

<details><summary>Hints</summary>

- Pick ONE real fork with two genuinely viable options.
- Say what you gave up, with a number attached.
- Close with whether you'd still make the same call and what would flip it.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real trade-off at runtime.
1. The fork: two viable options and the constraint forcing a choice.
2. The decision + the 'why': what you optimized for and what you sacrificed.
3. Evidence: the number or prototype that justified it.
4. Reflection: still comfortable? what signal would make you revisit?
```

</details>

### How would your project handle 10x the scale, and how did you think about cost?

`scale-and-cost` · hard

**Probes** — the follow-ups to expect

- What is the first bottleneck that breaks at 10x, and how do you know?
- What were your dominant cost drivers, and how did you measure them?
- Which levers would you pull first — caching, batching, tiering, or a redesign?
- How would you detect the degradation before users do?
- Where does cost trade against latency or quality, and how do you set the dial?

**What a strong answer does**

- Identifies a concrete bottleneck that fails first at higher scale
- Reasons about cost with real drivers and numbers, not hand-waving
- Names specific scaling levers and their order of application
- Connects scale to detection and monitoring, not just capacity
- Shows impact orientation: resource allocation, not only technical elegance

<details><summary>Hints</summary>

- Name the single component that breaks first — don't list everything.
- Attach a cost driver to a number you actually tracked or estimated.
- Say which lever you'd pull first and why, before redesigning.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real scale/cost analysis at runtime.
1. Bottleneck: what saturates first at 10x and the evidence.
2. Cost model: the dominant drivers and how you measured them.
3. Levers: caching/batching/tiering vs. redesign, in order.
4. Detection: the signal that warns you before users feel it.
5. Trade dial: where cost fights latency or quality.
```

</details>

### If you started your project over today, what would you do differently — and what would you explore next if you had more time?

`what-youd-do-differently` · medium

**Probes** — the follow-ups to expect

- Which specific decision would you reverse, and why?
- What did you learn only after shipping that you'd apply from day one now?
- Was the change a matter of new information, or a mistake you'd own?
- What would you explore or build next with more time?
- How would your answer change if the scale or requirements were different?

**What a strong answer does**

- Names a specific decision to change, not a vague 'more testing'
- Ties the reflection to a concrete lesson learned on this project
- Shows honest self-assessment without being self-flagellating
- Distinguishes new-information changes from genuine mistakes
- Points to a credible next step that shows forward thinking

<details><summary>Hints</summary>

- Pick one real decision and own it — vague regrets read as evasion.
- Separate 'I'd know better now' from 'that was the right call with what I knew'.
- Close with a concrete next thing you'd build or explore.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real reflection at runtime.
1. The decision you'd change and the trigger for rethinking it.
2. The lesson: what you learned only after shipping.
3. Honest framing: mistake vs. new information.
4. Next step: what you'd explore with more time.
```

</details>

### On your project, what did you personally own and decide, versus what the rest of the team did?

`your-contribution` · easy

**Probes** — the follow-ups to expect

- Which decisions were yours to make, and which did you influence but not own?
- What is one thing that would not have happened without you?
- How did you divide work with the rest of the team?
- Where did you disagree with the team, and how did it resolve?
- How did you communicate your part to stakeholders or teammates?

**What a strong answer does**

- Draws a clear line between 'I' and 'we' without over-claiming
- Names at least one decision the candidate personally owned
- Shows initiative and ownership, not just task execution
- Gives the team credit honestly where due
- Demonstrates it with a concrete artifact or outcome, not just a title

<details><summary>Hints</summary>

- Use 'I' for what you owned and 'we' for the rest — keep the line clean.
- Give one thing that wouldn't have happened without you, with proof.
- Credit the team honestly; over-claiming reads as a red flag.

</details>

<details><summary>Answer skeleton</summary>

```text
# Model STRUCTURE only — fill with your real contribution at runtime.
1. Scope: your area versus the team's, stated plainly.
2. Owned decision: one call that was yours and its outcome.
3. Initiative: something that happened because you pushed it.
4. Collaboration: how you split work and handled a disagreement.
5. Credit: what the team did that you don't claim.
```

</details>
