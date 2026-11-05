---
generated_by: tools/slides/flashcards.py
decks:
- programming/frontend-and-ux/slides/deck.yaml
cards:
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
---
