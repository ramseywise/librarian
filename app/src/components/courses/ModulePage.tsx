import { useEffect, useState } from "react";
import type { Course, CourseModule, Deck, LessonOutline, SlideDeck } from "./types";
import { SlideFrame } from "./SlideFrame";
import { courseColor } from "../../theme/domains";
import { useLabs, useStudyProgress } from "../../hooks/useCourses";
import { Check } from "./Check";
import { Markdown } from "./Markdown";
import { isPractice, lessonSections, moduleNotes, subsectionOf, submodules } from "./sections";
import { StudyLevels } from "./StudyLevels";
import { useLearning } from "../../hooks/useLearning";
import { lessonSchema, slideDeckSchema } from "../../schemas/courses";
import { useSpeech } from "../../hooks/useSpeech";
import { bankToSegments, isQuestionBank, parseQuestionBank, withheldNote } from "../../voice/questionBank";
import { apiFetch, parseJson } from "../../utils/api";
import { moduleFacet } from "../../utils/curriculum";
import { mapPath } from "../../utils/mapRoute";
import { splitOverview } from "./courseLogic";
import { MasteryBar, SourceList } from "./courseBits";
import { useOverview } from "./useOverview";

/** A lecture as a card: its first slide as a preview, and one button that opens it. */
function DeckCard({ deck, course, kind }: { deck: Deck; course: string; kind: string }) {
  const [slides, setSlides] = useState<SlideDeck | null>(null);
  useEffect(() => {
    let cancelled = false;
    apiFetch(`/api/courses/slides/${deck.id}`)
      .then((r) => (r.ok ? parseJson(r, slideDeckSchema) : null))
      .then((d) => !cancelled && setSlides(d))
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [deck.id]);
  const first = slides?.id === deck.id ? slides.frames?.[0] : undefined;
  const count = slides?.id === deck.id ? (slides.frames?.length || slides.slides.length) : 0;
  return (
    <div className="deck-card">
      <a href={`#/slides/${deck.id}`} className="deck-card-peek" aria-hidden="true" tabIndex={-1}>
        {first && <SlideFrame frame={first} total={count} courseColor={courseColor(course)} />}
      </a>
      <div className="deck-card-text">
        <span className="deck-card-kind">{kind}{count ? ` · ${count} slides` : ""}</span>
        <span className="deck-card-title">{deck.title}</span>
        {deck.subtitle && <span className="deck-card-sub">{deck.subtitle}</span>}
        <a href={`#/slides/${deck.id}`} className="btn-primary deck-card-open" aria-label={deck.title}>Open the lecture</a>
      </div>
    </div>
  );
}

/** One topic, opening on its lecture and its readme (what the module teaches and its syllabus), then everything it
 * has in the order it is used: test yourself (the three levels, with how far you are), the notes in reading order
 * grouped by submodule (the deck's parts after the overview: this page is the intro), each with its slides,
 * hands-on (labs, practice files and drills), the wiki pages its lessons cite, its references, and the module
 * that follows. A part the module lacks says so. */
/** "Listen" for each question bank in a module. Renders nothing where the browser cannot speak. */
function QuestionBanks({ lessons }: { lessons: LessonOutline[] }) {
  const banks = lessons.filter(isQuestionBank);
  const { supported } = useSpeech();
  if (!banks.length || !supported) return null;
  return (
    <div className="bank-list">
      <div className="section-label">Listen to a mock interview</div>
      {banks.map((bank) => <BankListen key={bank.id} bank={bank} />)}
    </div>
  );
}

function BankListen({ bank }: { bank: LessonOutline }) {
  const speech = useSpeech();
  const [note, setNote] = useState<string | null>(null);
  const name = [bank.section, bank.title].filter(Boolean).join(": ");

  // Something is spoken inside the click, because Safari only starts speech from a user gesture;
  // the bank follows when it has loaded.
  const listen = () => {
    setNote(null);
    const more = apiFetch(`/api/courses/lessons/${bank.id}`)
      .then((r) => (r.ok ? parseJson(r, lessonSchema) : Promise.reject(new Error("Could not load this question bank."))))
      .catch(() => Promise.reject(new Error("Could not load this question bank.")))
      .then((lesson) => {
        const parsed = parseQuestionBank(lesson.body);
        if (!parsed.exchanges.length) throw new Error("No questions could be found in this bank, so nothing was read.");
        const skipped = parsed.unparsed.length ? ` Not read, because their shape was not recognised: ${parsed.unparsed.join(", ")}.` : "";
        setNote(`${parsed.exchanges.length} questions. ${withheldNote(parsed) ?? ""}${skipped}`.trim());
        return bankToSegments(parsed);
      });
    speech.speak([{ text: `${bank.section || bank.title}.` }], { more });
  };

  return (
    <div className="bank-row">
      <span className="bank-title">{name}</span>
      <div className="voice-controls">
        {speech.speaking ? (
          <>
            <button type="button" onClick={speech.stop} aria-label={`Stop listening to ${name}`} className="round-btn voice-btn voice-btn--active">■ Stop</button>
            <button type="button" onClick={speech.skip} className="round-btn voice-btn">Next question</button>
          </>
        ) : (
          <button type="button" onClick={listen} aria-label={`Listen to ${name}`} className="round-btn voice-btn">▶ Listen</button>
        )}
        <span role="status" className="voice-status">{speech.speaking ? speech.groupLabel ?? "" : ""}</span>
        {speech.error && <span role="alert" className="voice-error">{speech.error}</span>}
      </div>
      {note && <div className="voice-notice">{note}</div>}
    </div>
  );
}

export function ModulePage({ course, module: m, done, onOpen, onOpenConcept }: {
  course: Course; module: CourseModule; done: Set<string>; onOpen: (p: string) => void; onOpenConcept: (id: string) => void;
}) {
  const { data: labsData } = useLabs();
  const { data: studyProgress } = useStudyProgress();
  const { data: learning } = useLearning();
  const id = `${course.id}/${m.id}`;
  const labs = (labsData?.labs ?? []).filter((l) => l.course === course.id && l.module === m.id);
  const readme = m.lessons.find((l) => l.id === `${id}/readme`);
  const overview = useOverview(readme?.id ?? null);
  const references = m.lessons.find((l) => l.id === `${id}/references`);
  const notes = moduleNotes(id, m);
  // Notes kept in folders of their own (an interview round, a track's part) are listed folder by folder.
  const sections = lessonSections(notes);
  // A notebook or practice file a lab already opens is listed once, as the lab.
  const practice = m.lessons.filter((l) => isPractice(id, l)
    && !labs.some((lab) => lab.id.replace(/\.md$/, "") === l.id || l.id.startsWith(`${lab.id}/`)));
  const drills = m.lessons.filter((l) => l.kind === "drill");
  const following = course.modules[course.modules.indexOf(m) + 1];
  // A readme with a syllabus states the objectives row by row, so the module's own list would repeat it.
  const { lead, rest } = overview ? splitOverview(overview) : { lead: "", rest: "" };
  const prose = (body: string) => overview && (
    <Markdown body={body} lessonId={overview.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} sourceLinks={overview.sourceLinks} />
  );
  const hasSyllabus = overview ? /^## Syllabus\s*$/m.test(overview.body) : !!readme;
  const next = notes.find((l) => !done.has(l.id));
  // The deck's parts are the module's submodules; a note none of them teaches is listed after them.
  const subs = submodules(id, m).filter((s) => s.lessons.length > 0);
  const loose = notes.filter((l) => !subs.some((s) => s.lessons.includes(l)));
  const step = next ? subs.find((s) => s.lessons.includes(next)) : undefined;
  const wiki = m.wiki ?? [];
  const moreWiki = Math.max((m.wikiCount ?? wiki.length) - wiki.length, 0);
  const graph = `#${mapPath({ level: "all", tags: [moduleFacet(course.id, m.id)] })}`;
  // A non-object (an unsigned or failed request) means no progress, not a broken page.
  const progress = studyProgress && !Array.isArray(studyProgress) ? studyProgress[id] : undefined;
  // A lecture series names its own overview, so the module's single deck follows it as the short version.
  const series = (m.decks ?? []).some((d) => d.overview);
  const decks = series ? [...(m.decks ?? [])].sort((a, b) => Number(a.id === id) - Number(b.id === id)) : m.decks ?? [];
  const deckKind = (d: Deck) => d.overview || (d.id === id && !series) ? "Overview lecture"
    : d.id === id ? "Whole module in one deck" : "Lecture";
  const noteRow = (l: LessonOutline) => (
    <div key={l.id} className="course-row">
      <Check on={done.has(l.id)} />
      <span className="course-row-no">{notes.indexOf(l) + 1}</span>
      <a href={`#/courses/${l.id}`} className="course-row-title">{l.title}</a>
      {sections.length > 0 && subsectionOf(l) && <span className="course-row-section">{subsectionOf(l)}</span>}
      {l.quizCount ? <a href={`#/quiz/${l.id}?choice`} className="course-row-test">{l.quizCount} questions</a> : null}
      {l.flashcardCount ? <a href={`#/flashcards/${l.id}`} className="course-row-test">{l.flashcardCount} flashcards</a> : null}
      {l.problemCount ? <a href={`#/quiz/${l.id}?worked`} className="course-row-test">{l.problemCount} problems</a> : null}
      {l.kind === "notebook" && <span className="kind-badge">notebook</span>}
      {done.has(l.id) ? <span className="course-row-state">read</span> : l === next ? <span className="course-row-state course-row-state--next">next</span> : null}
    </div>
  );
  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner course-page-inner--overview">
        <button onClick={() => onOpen(course.id)} className="link-btn">← {course.title}</button>
        <h1 className="course-page-title course-page-title--overview">{m.title}</h1>
        <MasteryBar mastery={learning?.modules[id]} />
        {lead.trim() ? <div className="lesson-prose course-module-lead">{prose(lead)}</div>
          : m.summary && <p className="course-overview-summary">{m.summary}</p>}

        <h2 className="section-label course-module-label">Lecture</h2>
        {m.decks?.length ? (
          <div className="deck-cards">
            {decks.map((d) => <DeckCard key={d.id} deck={d} course={course.id} kind={deckKind(d)} />)}
          </div>
        ) : <p className="course-none">No lecture deck yet.</p>}

        {m.objectives?.length && !hasSyllabus ? (
          <>
            <h2 className="section-label course-module-label">After this module you can</h2>
            <ol className="course-objectives">
              {m.objectives.map((o) => <li key={o}>{o}</li>)}
            </ol>
          </>
        ) : null}

        {rest.trim() && <div className="lesson-prose course-module-overview">{prose(rest)}</div>}

        <h2 className="section-label course-module-label">Test yourself</h2>
        {(m.quizCount || m.flashcardCount || m.problemCount) ? (
          <StudyLevels id={id} quizCount={m.quizCount} flashcardCount={m.flashcardCount} problemCount={m.problemCount} progress={progress} />
        ) : <p className="course-none">No questions or flashcards yet.</p>}

        <QuestionBanks lessons={m.lessons} />

        <h2 className="section-label course-module-label">Notes</h2>
        {notes.length === 0 ? <p className="course-none">No notes yet.</p>
          : subs.length ? (
            <>
              {subs.map((sub) => (
                <section key={sub.n} aria-label={sub.title} className="course-submodule">
                  <h3 className="course-section-title">
                    <a href={`#/courses/${sub.lessons[0].id}`}>{sub.title}</a>
                    <a href={`#/slides/${id}?part=${sub.n}`} className="course-section-slides">Slides</a>
                  </h3>
                  {sub.summary && <p className="course-submodule-summary">{sub.summary}</p>}
                  <div className="course-module-list">{sub.lessons.map(noteRow)}</div>
                </section>
              ))}
              {loose.length > 0 && (
                <section aria-label="More notes" className="course-submodule">
                  <h3 className="course-section-title">More notes</h3>
                  <div className="course-module-list">{loose.map(noteRow)}</div>
                </section>
              )}
            </>
          )
          : sections.length ? sections.map((sec) => (
            <section key={sec.title} aria-label={sec.title}>
              <h3 className="course-section-title">
                <a href={`#/courses/${sec.first.id}`}>{sec.title}</a>
              </h3>
              <div className="course-module-list">{sec.lessons.map(noteRow)}</div>
            </section>
          ))
          : <div className="course-module-list">{notes.map(noteRow)}</div>}

        {/* A syllabus links each step's labs and sources, so the page does not list them again. */}
        {!hasSyllabus && (
          <>
          <h2 className="section-label course-module-label">Hands-on</h2>
          {labs.length > 0 || practice.length > 0 || drills.length > 0 ? (
            <div className="course-module-list">
              {labs.map((lab) => (
                <div key={lab.id} className="course-row course-row--stack">
                  <a href={`#/labs/${lab.id}`} className="course-row-title">{lab.title}</a>
                  <span className="course-row-section">{lab.purpose}</span>
                </div>
              ))}
              {practice.map((l) => (
                <div key={l.id} className="course-row">
                  <a href={`#/courses/${l.id}`} className="course-row-title">{l.title}</a>
                  <span className="course-row-section">{l.kind === "notebook" ? "Notebook" : "Practice"}</span>
                </div>
              ))}
              {drills.map((d) => (
                <div key={d.id} className="course-row">
                  <a href={`#/courses/${d.id}`} className="course-row-title">{d.title}</a>
                  <span className="course-row-section">Drill{d.drill?.difficulty ? ` · ${d.drill.difficulty}` : ""}</span>
                </div>
              ))}
            </div>
          ) : <p className="course-none">No labs or drills yet.</p>}

          <h2 className="section-label course-module-label">Wiki</h2>
          {wiki.length > 0 ? (
            <>
              <div className="course-module-list">
                {wiki.map((p) => (
                  <div key={p.id} className="course-row course-row--stack">
                    <button onClick={() => onOpenConcept(p.id)} className="course-row-title course-wiki-title" title="Open this page">{p.title}</button>
                    {p.summary && <span className="course-row-section">{p.summary}</span>}
                  </div>
                ))}
              </div>
              <p className="course-wiki-more">
                {moreWiki > 0 && <>{moreWiki} more cited by these lessons. </>}
                <a href={graph}>Show on the graph</a>
              </p>
            </>
          ) : <p className="course-none">No wiki pages cover this yet.</p>}

          {(!!references || m.references?.length > 0 || m.readings?.length > 0 || !!m.readingsCount) && (
            <>
              <h2 className="section-label course-module-label">References</h2>
              {references && (
                <div className="course-module-list">
                  <div className="course-row course-row--stack">
                    <a href={`#/courses/${references.id}`} className="course-row-title">References</a>
                    <span className="course-row-section">{references.summary || "The books, papers and courses behind this module"}</span>
                  </div>
                </div>
              )}
              <SourceList label="Readings" items={m.readings} count={m.readingsCount} />
              <SourceList label="Reference material (not imported)" items={m.references} />
            </>
          )}
          </>
        )}

        <h2 className="section-label course-module-label">What's next</h2>
        <div className="course-next">
          {next ? (
            <a href={`#/courses/${next.id}`} className="btn-primary course-next-go">
              {done.size && notes.some((l) => done.has(l.id)) ? "Continue" : "Start"}: {next.title}
            </a>
          ) : following ? (
            <a href={`#/courses/${course.id}/${following.id}`} className="btn-primary course-next-go">Next module: {following.title}</a>
          ) : null}
          {next && step && <span className="course-next-step">In {step.title}</span>}
          {next && following && (
            <span className="course-next-after">Then: <a href={`#/courses/${course.id}/${following.id}`}>{following.title}</a></span>
          )}
        </div>
      </div>
    </div>
  );
}
