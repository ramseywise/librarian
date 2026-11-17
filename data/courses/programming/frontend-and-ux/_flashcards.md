---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- programming/frontend-and-ux/slides/deck.yaml
cards:
- front: What are the three parts of this lecture, in order?
  back: The lecture moves from how a page holds state, to how people receive it, to an answer that arrives a word at a time.
  lesson: programming/frontend-and-ux/readme
- front: Name three things this lecture teaches you to do with an interface.
  back: You will be able to say what state an interface is in, check that people can tell, and handle an answer that may be wrong.
  lesson: programming/frontend-and-ux/readme
- front: What does a browser build from your page?
  back: A DOM from the HTML, a CSSOM from the CSS and an accessibility tree, then style, layout, paint and composite.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: Which CSS rule wins?
  back: Origin and importance, then layer, specificity and source order. One ID beats any number of classes, so keep selectors flat.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: What happens when React state changes?
  back: An event sets state, React calls your function for a new description, and it changes only what differs in the DOM.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Why do three setter calls add only 1?
  back: State is constant within a render, and the setter only schedules the next one. When the next value depends on the last, use the function form.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: How do you make impossible states unrepresentable?
  back: Replace booleans with one status union, and keep transitions in a pure reducer. It tests with no browser and can drop events from old requests.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: When is an Effect the wrong tool?
  back: Compute derived values while rendering and act on clicks in handlers. An Effect with cleanup is only for keeping something outside React in step.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Which planted faults did axe 4.14 report?
  back: In the lab, axe reported only the contrast and page-structure faults. Whether a control works or a name is true needs someone to try it.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What does WCAG 2.2 ask of an application interface?
  back: Keyboard access, names and roles, more than colour, 4.5:1 text contrast, visible focus, and status changes announced without moving focus.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: How do you check what axe can't?
  back: After axe, do the main task by keyboard, zoom to 400%, and do one task with a screen reader. Then involve people who use one daily.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What does each response time limit demand?
  back: Under 0.1 s feels instant, under 1 s keeps flow, and past 10 s attention wanders, so show progress and a way to stop. Look at your p95 and find its band.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: What makes a good error message?
  back: Near the source, in plain language, with the precise problem and what to do next, no blame, and the user's input kept.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: What does "five users" actually claim?
  back: With `L` at 31% and one user group, Nielsen's model has five users finding about 85% of problems. It's for finding problems in rounds, not measurement.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: Why does a stream parser need a buffer?
  back: Chunks don't align with events, so buffer until a blank line and decode UTF-8 in stream mode. Chat clients use `fetch`, because `EventSource` can't POST.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What should a screen reader hear during a stream?
  back: No settled answer. The lab keeps the answer out of any live region and announces transitions in a status region, which still needs testing with users.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: How do you know a stream actually finished?
  back: A 200 means it started, and only a terminal event means it finished. Treat a clean close as a failure, and keep and label the partial text.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: How often do citations support the answer?
  back: In that 2023 audit, 74.5% of citations supported their sentence and 51.5% of sentences were fully supported. A supported sentence can still be false.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What can you check about a citation in code?
  back: Show only what the answer refers to, and check that markers exist and numbers appear in the quote. Whether a passage supports a paraphrase needs a grader.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Does showing uncertainty help?
  back: It can help, wording matters, and hedging didn't remove overreliance, so test it. Show a reason and an action in words, from a signal outside the model.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What must a handoff to a person do?
  back: Be reachable from every finished state, carry the context, confirm what happened and what was shared, and survive its own failure.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: How do you keep model output from attacking the page?
  back: Model output is untrusted input to your page. Render it as text, allow-list URL schemes, and set a Content Security Policy as the backstop.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What rules hold for any streaming AI answer?
  back: Trust only a terminal event, check citations, show uncertainty in words, keep a route to a person, and render model output as text.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Where do you go after this track?
  back: Do the lab, read application patterns for which interface to build, and read the threat model for what output handling sits inside.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What does a browser build from a page?
  back: A DOM from the HTML, a CSSOM from the CSS and an accessibility tree. Then style, layout, paint and composite.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: Why choose `<button>` over `<div onclick>`?
  back: Focus, Space and Enter, and form behaviour come built in, and a screen reader announces it as a button. A `div` has none, and you would have to write them all.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: What does specificity compare?
  back: IDs, then classes, then types, column by column. It only applies after origin, importance and layers, and source order breaks ties.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: '`content-box` against `border-box`?'
  back: Whether `width` excludes or includes padding and border.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: Flexbox or grid?
  back: 'One direction: flexbox. Rows and columns together: grid.'
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: What's wrong with `innerHTML`?
  back: It parses a string as markup, so untrusted text can become elements. Use `textContent` for text.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: What causes reflow?
  back: Anything that changes geometry, such as added text or an image arriving with no declared size.
  lesson: programming/frontend-and-ux/notes/01-html-css-and-the-dom
- front: What triggers a render?
  back: A state change in this component or a parent. Rendering means calling your function.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Why doesn't a value update right after `setState`?
  back: State is a snapshot for that render. The setter asks for the next one.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: How do you decide something is state?
  back: It isn't state if it doesn't change, comes from props or can be computed.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Why `useReducer` for a stream?
  back: One place for every transition, testable with no browser, and it can drop events from old requests.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: What's an Effect for?
  back: Keeping something outside React in step. Not for derived values, and not for reacting to a click.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Why does Strict Mode run Effects twice?
  back: To expose a missing cleanup during development.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: How do you handle out-of-order responses?
  back: Ignore stale ones with a flag or request id, and abort them too.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Why does `key` matter?
  back: It's identity across renders, so state stays with the right row. A changed `key` resets a subtree.
  lesson: programming/frontend-and-ux/notes/02-react-and-state
- front: Which WCAG level should you aim for?
  back: AA is the usual default, in our judgement, and the W3C calls the choice a policy decision. It advises against blanket AAA.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What's the first rule of ARIA?
  back: Prefer native HTML. No ARIA is better than bad ARIA, because a role promises behaviour it doesn't supply.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What contrast does body text need?
  back: 4.5:1, and 3:1 for large text.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What share of problems does axe find?
  back: Its README says 57% of issues on average, which is the vendor's own figure. Whether a control works or a name is true is outside what it can check.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: How do you announce a status change?
  back: A `role="status"` element, present from page load, updated with text.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What should happen to focus when a button disappears?
  back: Move it somewhere sensible first, or it falls to `<body>`.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: What can't you learn from a screen reader test by a sighted developer?
  back: How someone who uses one daily would experience it. Involve those users.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: How do you test keyboard use automatically?
  back: Drive real key events in a browser and assert on `document.activeElement` and the result, as the lab's tests do.
  lesson: programming/frontend-and-ux/notes/03-accessibility
- front: Name the three response time limits.
  back: 0.1 s feels instant, 1 s keeps flow, 10 s is the limit of attention.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: What are the parts of usability?
  back: Learnability, efficiency, memorability, errors, satisfaction.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: Why is recognition better than recall?
  back: The interface supplies the cues, so memory has less to do.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: What's a mental model?
  back: What the user believes the system does. It steers behaviour whether or not it's true.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: Why five users?
  back: Nielsen's model has them finding about 85% of problems in one group. It's for finding problems in rounds, not for measurement.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: How would you review a screen fast?
  back: Name the user and task, do it, force the bad states, time it, check the exits, read the errors, try the keyboard.
  lesson: programming/frontend-and-ux/notes/04-ux-principles
- front: How do you know a stream succeeded?
  back: A terminal event. A 200 and a clean close prove nothing.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Why `fetch` and not `EventSource` for chat?
  back: '`EventSource` takes a URL and a credentials option, so no POST body or custom headers.'
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What's the framing bug in a stream parser?
  back: Chunks don't align with events, so buffer until a boundary, and decode UTF-8 across chunks.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: How do you tell slow from dead?
  back: A watchdog reset by any byte, including keep-alive comments.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Should streaming text go in a live region?
  back: There's no settled answer. It announces every change. Announcing state changes instead is reasonable, but test with real screen reader users.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What does citation precision mean here?
  back: The share of citations that support their sentence. Liu et al. averaged 74.5% across four 2023 engines, ranging from 63.6 to 89.5, with recall at 51.5%.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Do users check citations?
  back: NN/g's research says rarely, and their presence itself builds trust. So verify in code.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Should an interface show confidence?
  back: Only if it helps decisions. Prefer a reason and an action, using a signal from outside the model, evaluated on your own data.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Do explanations reduce overreliance?
  back: Not reliably. Bansal found no significant net accuracy gain over confidence alone. Buçinca found forcing helped when the AI was wrong, with no overall gain, on a low-stakes task.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Name a Markdown attack on a chat UI.
  back: An injected image URL holding conversation data. It's fetched on display, with no click.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: What must a handoff do?
  back: Be reachable from any finished state, carry context, confirm what happened and survive its own failure.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
- front: Why keep partial text?
  back: The person may be mid-sentence and it can still be useful, so keep it and label it incomplete.
  lesson: programming/frontend-and-ux/notes/05-ai-interfaces
---
