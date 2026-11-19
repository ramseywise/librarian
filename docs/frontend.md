# Frontend styling and conventions

What is true in `app/` today (Vite, React 18, TypeScript). If code and this page disagree, the code wins; fix the page.

## Tokens

- `app/src/theme/tokens.css` holds every colour, radius (`--radius-*`), spacing step (`--space-1`..`--space-9`) and type size (`--fs-*`) the UI repeats. Dark values are the default on `:root`; `[data-theme="light"]` overrides the colours. `utils/theme.ts` sets `data-theme` on `<html>`.
- **The rule:** no hex colour outside `tokens.css`. Rules use `var(--token)`. Colours that come from data (a domain, a lecture beat) are set inline by the component as the `--c` custom property, and the domain palette lives in `theme/domains.ts`.
- `theme/__tests__/stylesheets.test.ts` enforces this: it fails on a hex colour in any other stylesheet (comments excluded) and on a repeated `/* ---- Title ---- */` section header within one stylesheet. `theme/__tests__/tokens.test.ts` checks the contrast of both themes.

## Stylesheet import order

- `main.tsx` imports `theme/tokens.css`, then `theme/ui.css`, then `App`. Nothing else imports those two (the test checks `main.tsx` and `App.tsx`).
- Component styles sit beside their component and are imported by it: `components/graph.css`, `filter.css`, `card.css`, `clusterInset.css`, `chat/chat.css`, `courses/*.css` (`courses.css`, `slides.css`, ...), and `theme/atlas.css` for the atlas.
- Because tokens and `ui.css` load first, a component sheet may rely on them and may override a primitive only by being more specific.

## Primitives in `theme/ui.css`

The catalogue is at the top of the file.

| Group | Classes |
| --- | --- |
| Utilities | `.grow`, `.text-success`, `.text-concept`, `.sr-only` |
| Buttons | `.pill-btn` (`--accent`), `.toggle-btn`, `.seg > .seg-btn`, `.btn-row` |
| Notices | `.resource-notice`: a failed load with its Retry button (`ResourceNotice`) |
| Labels | `.panel-label` (`--spaced`), `.float-panel`, `.check` (`.is-on`) |
| Shell | `.app`, `.app-header`, `.app-body`, `.app-sidenav` (`.is-open`, `.is-hidden`), `.app-main`, `.app-course-layer`, `.app-graph-layer`, `.app-loading`, `.app-chat`, `.app-map-dock`, `.map-browse` |

## Breakpoints

- **1100px** is the shell breakpoint. At 1099px and below the navigation is a drawer behind the Menu button and the chat overlays the main area; at 1100px and above the Menu button slides the navigation away. The CSS (`ui.css`) and `NARROW_QUERY = "(max-width: 1099px)"` in `App.tsx` must change together.
- **759px** is the component breakpoint for narrow cards and panels (`card.css`, `clusterInset.css`, `courses.css`, `atlas.css`); **640px** is used by `slides.css` and the course deck cards.
- `ui.css` also has one height query (`max-height: 820px`), and `tokens.css` honours `prefers-reduced-motion`.

## Loading and errors

- Data hooks (`useCurriculum`, `useGlossary`, `useCourseProgress`, `useWikiData`, and the course hooks in `useCourses`) return `{ data, error, loading, retry }` (`hooks/resource.ts`). Consumers show `ResourceNotice` when `error` is set.
- A failed background refresh keeps the data on screen; the error shows only while there is nothing to show.
- API replies are validated with zod at one boundary: `apiJson(schema, url)`, `postJson(schema, url, body)` or `parseJson(response, schema)` in `utils/api.ts`. Schemas are in `src/schemas/`, and the TypeScript types are inferred from them. A reply that fails validation throws `ApiError("Unexpected reply from the server (...)")`, which takes the normal error path.
- `ErrorBoundary` wraps the lazy course views in `App.tsx` and resets when the route changes.

## Checks

`npm run typecheck`, `npm run lint` (includes `jsx-a11y` and `@typescript-eslint/no-floating-promises`), `npm test`, `npx vite build`. Dependency versions in `package.json` are exact and match `package-lock.json`.
