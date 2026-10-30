---
imported_hash: e8342c2ed13bf66d
title: Design an AI coding copilot (inline code completion like GitHub Copilot)
summary: coding-copilot-walkthrough · serving · hard
order: 93
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/coding-copilot.md
---

# Design an AI coding copilot (inline code completion like GitHub Copilot)

`coding-copilot-walkthrough` · serving · hard

## 1. clarify

**Interviewer:** What do you clarify first? Frame the product surface, latency bar, and what makes copilot different from a chatbot.

<details><summary>Reference</summary>

Clarify the surface and the constraints. (1) Which surface: INLINE completion (ghost
text mid-file) vs a chat/agent panel? They're different systems — inline is a
latency-obsessed completion server, chat is an orchestration problem. Assume inline
first. (2) Latency: inline completion is triggered constantly and must feel instant;
GitHub targets sub-300ms average end-to-end, and ghost text generally needs to be
under a second. Latency, not raw model quality, dominates the UX. (3) Cost: at
millions of developers and a request per typing pause, most requests must be cheap or
skipped entirely. (4) Quality: fill-in-the-middle correctness, matching the
surrounding code style, not just left-to-right generation. (5) Privacy/trust: code
is sensitive IP. State assumptions and confirm. [gh-inside, gh-understanding, cody-lifecycle]

</details>

## 2. high-level

**Interviewer:** Sketch the end-to-end path of one completion, from keystroke to ghost text.

<details><summary>Reference</summary>

Mostly client-driven. In the IDE: the user types -> DEBOUNCE (wait ~75ms so we don't
fire on every keystroke) -> a client-side GATE decides whether a completion is even
worth requesting -> gather CONTEXT (code before/after cursor + snippets from
neighboring open tabs) -> build the FILL-IN-THE-MIDDLE prompt -> send to the
completion service -> a fast, purpose-built completion model generates -> STREAM
tokens back, truncate early once we have a coherent suggestion -> render as ghost
text -> user accepts (Tab) or keeps typing (implicit reject). Server side: a thin
completion service behind a model gateway routing to GPU inference, plus caching and
light output filtering. The whole loop is optimized to add as little latency as
possible; snippet selection is done without stalling thanks to caching. [gh-inside, copilot-internals, cody-lifecycle]

</details>

## 3. deep-dive

**Interviewer:** Context assembly: how do you build a good prompt within a tiny latency and token budget?

<details><summary>Reference</summary>

Prompt crafting = building a "pseudo-document" that leads the model to the completion
the developer wants. Use FILL-IN-THE-MIDDLE: give the model the PREFIX (code before
the cursor) and the SUFFIX (code after), so it generates code that fits between them,
not just continues forward — GitHub measured ~10% relative acceptance lift from FIM.
Enrich with NEIGHBORING TABS: search other open files for text similar to the code
around the cursor and splice in the best matches (a deliberately LOW inclusion
threshold worked best, ~5% acceptance lift). All of this must fit a small context
budget — for a model fast enough to serve inline, usable context is only ~6000
characters — so you select, prioritize, and filter snippets in real time. Add file
path/language hints. [gh-understanding, gh-inside]

</details>

## 4. deep-dive

**Interviewer:** How do you decide whether to even call the model? (this is the main cost lever)

<details><summary>Reference</summary>

Don't call the model on every pause — most keystrokes don't warrant a completion, and
calls cost money and latency. Two gates: (1) SYNTACTIC suppression — use a parser
(e.g. Tree-sitter) to skip low-value positions, like right after a completed
statement. (2) A cheap CONTEXTUAL FILTER — a small logistic-regression model over
lightweight features (language, whether the last suggestion was accepted or rejected,
time since last accept/reject, last line length, char before the cursor) predicts
whether a suggestion is likely to be accepted; if it scores below a threshold (~15%),
skip the LLM call entirely. This filter is the primary cost/quality gate. Combine
with client DEBOUNCE (~75ms) and requesting only 1-3 candidates to stay fast.
[copilot-internals, cody-lifecycle]

</details>

## 5. deep-dive

**Interviewer:** Serving: why a purpose-built completion model, and how do you keep in-flight requests cheap?

<details><summary>Reference</summary>

Inline completion is a DIFFERENT serving problem from chat. Chat/agent models, used
for inline, produce cursor-misaligned inserts and duplicate the prefix or overwrite
the suffix. A model trained specifically for FIM completion is both more correct AND
much faster — GitHub's custom completion model cut latency ~35% and tripled
throughput. Keep the model small and fast; use continuous batching on GPUs for
utilization. On the client, aggressively CANCEL/RECYCLE in-flight requests: when the
user keeps typing, cancel the stale request (and sometimes reuse a request across
nearby keystrokes) so you're never paying for outdated completions. Cache model
results and even the suffix across calls. Stream and TRUNCATE EARLY once the
suggestion is a coherent unit rather than waiting for the full response. [gh-custom-model, copilot-internals, cody-lifecycle]

</details>

## 6. deep-dive

**Interviewer:** How do you evaluate a copilot, given there's no single 'correct' completion?

<details><summary>Reference</summary>

The north-star online metric is ACCEPTANCE RATE (did the developer keep the
suggestion via Tab) and, better, CHARACTERS RETAINED after some time (did the code
survive, not just get accepted then deleted). A/B test every change — FIM,
neighboring tabs, the contextual-filter threshold, and the custom model were all
validated by measured acceptance lifts. Watch latency percentiles (p50/p95 TTFT and
end-to-end) as a first-class quality metric, since slow completions get ignored.
Offline, use held-out code with masked spans to score FIM correctness. Segment by
language, since acceptance and useful context differ a lot across languages. [gh-understanding, gh-inside, gh-custom-model]

</details>

## 7. tradeoffs

**Interviewer:** What's the core tension, and how does a chat/agent mode differ from inline completion?

<details><summary>Reference</summary>

The central tension is LATENCY/COST vs QUALITY: a bigger model or more context raises
acceptance but blows the latency and cost budget that inline completion lives under —
so the whole design is 'smallest fast model + tightest useful context + skip when in
doubt.' A CHAT/AGENT mode flips the priorities: the user tolerates seconds of
latency, so you use a larger model, a much bigger context (repo-scale retrieval /
RAG over the codebase), multi-step tool use (read files, run tests, edit), and heavier
guardrails — that's an orchestration problem sitting behind a model gateway, not a
keystroke-latency problem. Same product, two very different backends. [gh-custom-model, chip-huyen-platform]

</details>

## 8. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does it degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Latency regressions: monitor p50/p95 end-to-end
and TTFT; degrade by shrinking context, dropping to a smaller model, or suppressing
completions when the backend is slow. (2) Cost blowup from over-triggering: watch
call rate vs acceptance and cache hit rate; tighten the contextual-filter threshold
and debounce. (3) Wasted spend on cancelled requests: ensure in-flight cancellation
actually stops GPU work. (4) Bad/insecure suggestions (leaking secrets, vulnerable
patterns): output filtering and public-code matching. (5) Privacy: don't retain code
you shouldn't; scope any retrieval to the user's own repos. Close with the biggest
risks and what you'd tune first (usually the trigger gate and the latency budget).
[copilot-internals, gh-inside, chip-huyen-platform]

</details>

## Sources

- [GitHub Blog — How GitHub Copilot is getting better at understanding your code](https://github.blog/ai-and-ml/github-copilot/how-github-copilot-is-getting-better-at-understanding-your-code/)
- [GitHub Blog — Inside GitHub: Working with the LLMs behind GitHub Copilot](https://github.blog/ai-and-ml/github-copilot/inside-github-working-with-the-llms-behind-github-copilot/)
- [GitHub Blog — The road to better completions: a new custom model](https://github.blog/ai-and-ml/github-copilot/the-road-to-better-completions-building-a-faster-smarter-github-copilot-with-a-new-custom-model/)
- [copilot-explorer — Copilot Internals (reverse-engineered client behavior)](https://thakkarparth007.github.io/copilot-explorer/posts/copilot-internals.html)
- [Sourcegraph — The lifecycle of a code AI completion](https://sourcegraph.com/blog/the-lifecycle-of-a-code-ai-completion)
- [Chip Huyen — Building a Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html)
