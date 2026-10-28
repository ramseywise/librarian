---
title: Server Shell, Client Leaf
tags: [patterns, infra, pattern]
summary: "To move a Next.js layout or page off 'use client', resolve data in the server route and pass it down as a prop, extract only the hook-dependent JSX (usePathname, useActionState) into the smallest client island, and make the new prop optional with the old client fetch as fallback so call sites outside the issue's scope see no behaviour change."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis56-server-client-boundary.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-consumer-page-latency.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-consumer-page-latency.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-consumer-page-latency.md
---

# Server Shell, Client Leaf

Two parallel refactors in akira's Next.js App Router frontend, run in the same week,
removed whole-file `'use client'` from layouts, pages and forms. One moved session and
list data server-side. The other moved forms to Server Actions. They used the same
shape, and the same few decisions came up in both.

## The shape

1. **Resolve data in the route's own server file.** `page.tsx` or `layout.tsx` calls the
   server-side data seam that already exists (a server client plus the product module)
   and passes the result down as a prop. A server page calls `lib/` or `products/`
   directly. It does not call its own API route over HTTP.
2. **Extract the smallest client island.** Both layouts were `'use client'` only because
   they called `usePathname()` for a nav active state or a back link. A server layout has
   no equivalent. So that JSX alone moved, verbatim, into a new `AdminNav` and
   `SettingsBackLink`, and the layouts became plain server functions. The new files hold
   relocated code, not new behaviour.
3. **Prop in, fetch out.** A client component that fetched on mount (saved-item ids, a
   list of events for a picker) now takes `initialX` as a prop. The skeleton-then-flash
   and the empty-then-populated gap disappear, because the server already had the data
   before it sent HTML.
4. **Copy the existing route's contract exactly.** The server page that replaced a
   client `fetch('/api/events?limit=50')` reproduced the route's *defaults*: the same
   date window, the same visibility filter, the same order and limit. The defaults were
   the contract the client had been getting, so the plan was not free to invent a
   different one. An anonymous visitor gets `[]`, which is what the route already
   returned with a 200 rather than a 401.

## Optional prop, original fallback

A shared avatar component had three call sites. Only one of them, the settings layout,
was in the issue's scope. The rejected option was to make `session` required and pass
`null` from the two login and register forms. That would silently show an
already-signed-in visitor the logged-out icon on those pages, which is a behaviour change
a refactor must not introduce.

The chosen option made `session` an **optional** prop. When it is passed, the component
uses it with no fetch and no flash. When it is omitted, the component keeps its original
`useEffect` and client session fetch unchanged. The out-of-scope call sites need zero
edits and see zero change. This is what made "these files and nothing else" literally
true.

## Server Actions follow the same split

- **Server page plus client `*Form.tsx` island.** The action lives in a colocated
  `actions.ts` with `'use server'` at the top. It needs its own file because a client
  component imports it for `useActionState`, and a server component file cannot be
  imported into a client one.
- **Client-only side effects run off action state.** Sign-out, `router.push` and
  `sessionStorage` writes cannot run in a Server Action. A thin client wrapper runs them
  in a `useEffect` on `state.success`. This keeps the change a swap of mechanism rather
  than a change of behaviour.
- **Share the schema, not the implementation.** The form's zod schema is imported by both
  the Server Action and the old API route. The action calls the database directly,
  exactly as the route does. It does not call the route, and the route does not delegate
  to the action. On the auth surface, two independent call sites aligned on one schema
  carry less risk than one rewired path.
- **Shape validation only.** The schema replaces type, required-field and format checks.
  Branches that depend on a database read (not found, already closed, duplicate option,
  token check, re-authentication) stay hand-written in the route.
- **Don't tighten a deliberately lenient route.** A password-reset route returns 200 even
  for a malformed or unknown email. That is a no-enumeration property, not a validation
  gap. Putting a rejecting schema there would be a security regression. The shared schema
  is still used client-side for early inline feedback.
- **A workaround can be removed rather than moved.** A page wrapped in `Suspense` only so
  `useSearchParams()` could work on the client. As a server component it reads its own
  `searchParams` prop and passes one boolean to the island, and the wrapper goes away.
- **Keep the existing refresh behaviour.** `window.location.reload()` after a mutation
  stayed as it was. `revalidatePath()` would be more idiomatic but changes how the page
  refreshes, so it was recorded as a named follow-up.

### Round-trip rules from an admin CRUD tab (akira, 2026-09-15)

A later registry-CRUD tab built on the same split found four details that a create/edit
form only shows once it runs against real data:

- **Echo the submitted values on failure.** React 19 resets an uncontrolled
  `<form action>` after every action call, errors included. Without a `values?` field on
  the action state, a duplicate-URL error also wiped what the operator had typed.
- **A judgment field opens on a disabled empty option, marked `required`.** A select
  that defaults to its first vocabulary value records a silent guess.
- **Render stored values that fall outside the vocabulary.** The `TEXT[]` column had no
  CHECK, so some rows held values the form didn't offer. They render as extra checked
  boxes labelled "not read by the importer", and the schema refuses them with a message
  that names the vocabulary. Otherwise editing such a row silently drops the value.
- **The update patch has an exact key list, and a test asserts it.** Asserting exactly 8
  patch keys guards against a later edit that spreads raw `formData` and lets a
  pipeline-owned or posture column through. It is a regression test for a defect class,
  not for a bug present today.

The same plan checked the schema before building the form. The issue's six "load-bearing"
columns left out `priority`, which was `NOT NULL` with no default, so every insert would
have failed. A typo-prone `TEXT[]` became a fixed checkbox group, which makes the typo
impossible rather than validating it after the fact.

## Testing an async server component

There was no precedent in the repo. The pattern that worked was to call the exported
default function, await the element it returns, and render that:
`render(await SettingsLayout({ children: <div/> }))`, with the server data client mocked
by the existing fake. The plan named a fallback in case this failed on the repo's exact
React and Next versions: test the island and the data resolution as two separate units.
It also said to stop and report rather than work around a failure silently.

## What review found

Both reviews raised the same class of defect. A degrade-to-empty path was added with no
logging. A profile query and a saved-ids loader each dropped the returned `error`, and
three Server Actions swallowed email-send errors. The fix was to log the error and still
return the same safe value. That keeps the no-throw render path, and for auth keeps the
no-enumeration response unchanged. Two more recurring defects:

- **Duplicate per-request queries.** After the layout became a server component, the
  layout and its child page both queried the same profile row. One colocated `data.ts`
  loader wrapped in React `cache()` now serves both.
- **Untested actions.** All eight new Server Actions had been mocked in every component
  test, so none was tested directly. Each got its own colocated test that mocks the
  database client instead of the action, the same technique the route tests use.

The refactor also left stale doc citations: a line-range reference into a component that
had moved, and an architecture diagram showing the removed client fetch. They were found
by grepping every spec for the changed symbols. Citations that were already wrong before
the change were flagged, not fixed.

## See Also
- [[Hydration Gap Silent Input Loss]] — related (the client-mount gap this removes, seen from the input side)
- [[Silent Failure Catalogue]] — instance-of (degrade-to-empty without a log line)
- [[Single-Definition Grep Guard]] — extends (the same forms issue's proof that one password policy exists)
- [[Audit the Class, Not the Instance]] — related (every converted form got the same assertion)
- [[Adoption Ban Needs an Escape Hatch]] — related (the `<form onSubmit>` lint ban needed named exceptions for the two forms kept client-direct)
- [[SSR Auth Fan-Out]] — related (per-render auth calls across proxy, layout and page)
