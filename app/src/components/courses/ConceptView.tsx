import { useConcept } from "../../hooks/useLearning";
import type { ConceptHub } from "../../schemas/learning";
import { Centered } from "./courseBits";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

/** How a lesson or drill is tied to the page. A neighbour by similar text must read as one. */
const LINK_LABEL: Record<string, string> = {
  explicit: "linked",
  mentioned: "names this page",
  semantic: "similar text",
  unit: "drill unit",
};



function Mastery({ concept }: { concept: ConceptHub }) {
  const m = concept.mastery;
  // Only what is on record: no evidence must not be worded as never having studied the page.
  if (!m) return <p className="concept-mastery">No study evidence recorded for this page.</p>;
  const lessons = m.counts?.lessons ?? 0;
  const drills = m.counts?.drills ?? 0;
  const cards = m.counts?.cards ?? 0;
  const seen = m.lastSeen ? new Date(m.lastSeen).toLocaleDateString() : null;
  return (
    <p className="concept-mastery">
      {m.due && <strong className="concept-due">Due. </strong>}
      Strength {Math.round(m.strength * 100)}%{seen && `, last seen ${seen}`}, from {lessons} lesson
      {lessons === 1 ? "" : "s"}, {drills} drill{drills === 1 ? "" : "s"} and {cards} card{cards === 1 ? "" : "s"}.
      {m.evidence === "weak" && " Weak evidence only: nothing that links this page directly has been studied, so this is capped."}
    </p>
  );
}

function Spoke({ title, empty, children }: { title: string; empty: string | null; children: React.ReactNode[] }) {
  return (
    <section className="concept-spoke">
      <h2 className="section-label">{title}</h2>
      {children.length ? children : empty && <p className="practice-status">{empty}</p>}
    </section>
  );
}

function LessonRow({ spoke, onOpen }: { spoke: ConceptHub["lessons"][number]; onOpen: (path: string) => void }) {
  const label = spoke.link ? LINK_LABEL[spoke.link] ?? spoke.link : null;
  return (
    <div className="concept-row">
      <button onClick={() => onOpen(`/courses/${spoke.id}`)} className="practice-link" title={spoke.summary}>
        {spoke.title}
      </button>
      <span className="concept-row-note">
        {spoke.course}
        {label && ` · ${label}`}
      </span>
    </div>
  );
}

function Hub({ concept, navigate, onShowInGraph }: {
  concept: ConceptHub; navigate: (path: string) => void; onShowInGraph: (id: string) => void;
}) {
  useDocumentTitle(pageTitle(concept.title));
  const { lessons, drills, decks, catalogReady } = concept;
  const nothing = catalogReady && !lessons.length && !drills.length && !decks.length;
  // While the courses build, "no lessons" is not known, so the course spokes stay quiet.
  const none = (text: string) => (catalogReady ? text : null);
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--practice">
        {concept.domain && <div className="concept-domain">{concept.domain}</div>}
        <h1 className="course-page-title">{concept.title}</h1>
        {concept.summary && <p className="course-page-lede">{concept.summary}</p>}
        <div className="concept-actions">
          <button onClick={() => onShowInGraph(concept.id)} className="round-btn">Show in graph</button>
        </div>
        <Mastery concept={concept} />
        {!catalogReady && (
          <p className="practice-status" role="status">
            The courses are still being built, so lessons, drills and decks may be missing here for now.
          </p>
        )}
        {nothing ? (
          <p className="practice-status">
            Nothing links to this page yet: no lesson, drill or deck. It is a wiki page only, which the graph can
            show in context.
          </p>
        ) : (
          <>
            <Spoke title="Taught by" empty={none("No lesson links this page.")}>
              {lessons.map((l) => <LessonRow key={l.id} spoke={l} onOpen={navigate} />)}
            </Spoke>
            <Spoke title="Drilled by" empty={none("No drill links this page.")}>
              {drills.map((d) => <LessonRow key={d.id} spoke={d} onOpen={navigate} />)}
            </Spoke>
            <Spoke title="Recall" empty={none("No flashcard deck covers this page.")}>
              {decks.map((d) => (
                <div key={d.id} className="concept-row">
                  <a href={`#/flashcards/${d.id}`} className="practice-link">{d.title}</a>
                </div>
              ))}
            </Spoke>
          </>
        )}
      </div>
    </div>
  );
}

function Message({ children }: { children: React.ReactNode }) {
  useDocumentTitle(pageTitle("Concept"));
  return <Centered>{children}</Centered>;
}

/** `#/concept/<id>`: a public wiki page and what teaches, drills and recalls it. The graph is one click away. */
export function ConceptView({ id, navigate, onShowInGraph }: {
  id: string; navigate: (path: string) => void; onShowInGraph: (pageId: string) => void;
}) {
  const { data, error, notFound, retry } = useConcept(id);
  if (notFound) return <Message>No such page.</Message>;
  if (error) {
    return (
      <Message>
        Could not load this page: {error}
        <div className="course-retry">
          <button onClick={retry} className="btn-primary">Retry</button>
        </div>
      </Message>
    );
  }
  if (!data) return <Message>Loading…</Message>;
  return <Hub concept={data} navigate={navigate} onShowInGraph={onShowInGraph} />;
}
