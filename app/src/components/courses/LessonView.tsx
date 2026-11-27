import { ResourceNotice } from "../ResourceNotice";
import { useEffect, useMemo, useRef, useState, type ComponentProps, type MouseEvent } from "react";
import type { Lesson, Deck, LabOutline } from "./types";
import { useGlossary } from "../../hooks/useGlossary";
import { ReportButton } from "../feedback/ReportButton";
import { DrillTimer } from "./DrillTimer";
import { Markdown } from "./Markdown";
import { openingRepeatsSummary, splitLesson, stripDuplicateH1 } from "./lessonParts";
import { CLOBBER_PREFIX, splitSolution } from "./markdownUtils";
import { StudyLevels } from "./StudyLevels";
import { useSpeech } from "../../hooks/useSpeech";
import { dictationAllowed } from "../../voice/policy";
import { drillPromptSpeech, lessonSections } from "../../voice/speechText";
import { ReadAloud } from "../voice/ReadAloud";
import { VoiceDrawer } from "../voice/VoiceDrawer";

interface Props {
  lesson: Lesson;
  courseTitle: string;
  /** The lecture decks of the lesson's module; the Lecture tab opens with the one for this lesson. */
  decks?: Deck[];
  done: boolean;
  onMarkDone: () => void;
  onOpen: (path: string) => void;
  onOpenConcept: (pageId: string) => void;
  onAsk: (question: string) => void;
  onToc: (toc: TocEntry[]) => void;
  onActiveHeading: (id: string | null) => void;
}

export interface TocEntry { id: string; text: string; level: number }

const TABS = [
  { id: "lecture", label: "Lecture" },
  { id: "study", label: "Study" },
  { id: "labs", label: "Labs" },
] as const;
type Tab = (typeof TABS)[number]["id"];


export function DrillBadges({ drill }: { drill: NonNullable<Lesson["drill"]> }) {
  const tone = ["easy", "medium", "hard"].includes(drill.difficulty ?? "") ? drill.difficulty : "other";
  return (
    <span className="drill-badges">
      <span className="drill-track">{drill.track}</span>
      {drill.difficulty && <span className={`drill-difficulty drill-difficulty--${tone}`}>{drill.difficulty}</span>}
      {drill.timebox_min && <span>{drill.timebox_min} min</span>}
      {drill.tags?.map((t) => (
        <span key={t} title="Concept with no wiki page yet" className="drill-tag">#{t}</span>
      ))}
    </span>
  );
}

/** A drill reads its Prompt section or nothing, and says which. See drillPromptSpeech. */
function DrillReadAloud({ body }: { body: string }) {
  const speech = useSpeech();
  if (!speech.supported) return null;
  const prompt = drillPromptSpeech(body);
  if (!prompt.ok) return <p className="voice-notice">Read-aloud is off for this drill: {prompt.reason}.</p>;
  return <ReadAloud speech={speech} label="Read prompt" segments={() => [{ text: prompt.text }]} />;
}

/** A lesson, one heading at a time. */
function LessonReadAloud({ body, title }: { body: string; title: string }) {
  const speech = useSpeech();
  const segments = () => lessonSections(body, title).map((s, group) => ({ text: s.text, group, groupLabel: s.heading }));
  return <ReadAloud speech={speech} label="Read aloud" segments={segments} skipLabel="Next section" />;
}

export function LessonView({ lesson, courseTitle, decks = [], done, onMarkDone, onOpen, onOpenConcept, onAsk, onToc, onActiveHeading }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const proseRef = useRef<HTMLDivElement>(null);
  const body = stripDuplicateH1(lesson.body, lesson.title);
  const parts = lesson.kind === "drill" ? splitSolution(body) : null;
  // A note is read, then tested, then run: its questions open the lecture as its objectives, their answers are
  // its flashcards, and its code sits on its own tab. A drill is one exercise, shown whole.
  const split = useMemo(() => (lesson.kind === "drill" ? null : splitLesson(body)), [lesson.kind, body]);
  const hasStudy = !!(split?.review || lesson.quizCount || lesson.flashcardCount || lesson.problemCount);
  const hasLabs = !!(split?.exercises || split?.code || lesson.labs?.length);
  // Every note has the three parts, so the tabs are always there; an empty one says so.
  const tabbed = !!split;
  const [tab, setTab] = useState<Tab>("lecture");
  const [anchor, setAnchor] = useState<string | null>(null);
  const [showSolution, setShowSolution] = useState(false);
  // A lecture is named after its note (`lectures/01-x.yaml` for `notes/01-x.md`) or lists it in `covers`
  // (one lecture per submodule); a note without one gets the module's own deck, whose id is the module.
  const stem = lesson.id.split("/").pop();
  const deck = decks.find((d) => d.id.split("/").pop() === stem)
    ?? decks.find((d) => !!stem && d.covers?.includes(stem))
    ?? decks.find((d) => lesson.id.startsWith(`${d.id}/`));
  const exercises = split?.exercises ? splitSolution(split.exercises) : null;
  const { data: glossary, error: glossaryError, retry: retryGlossary } = useGlossary(null, true);
  useEffect(() => {
    setShowSolution(false);
    setTab("lecture");
    setAnchor(null);
  }, [lesson.id]);
  const levels = { id: lesson.id, quizCount: lesson.quizCount, flashcardCount: lesson.flashcardCount, problemCount: lesson.problemCount };
  const md = (text: string) => (
    <Markdown body={text} lessonId={lesson.id} onOpenLesson={onOpen} onOpenConcept={onOpenConcept} terms={glossary?.terms} sourceLinks={lesson.sourceLinks} />
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
  }, [lesson.id]);

  // A "Code N in Labs" link in the lecture opens the Labs tab at that block.
  const openCode = (e: MouseEvent) => {
    const id = (e.target as HTMLElement).closest?.('a[href^="#code-"]')?.getAttribute("href")?.slice(1);
    if (!id) return;
    setTab("labs");
    setAnchor(id);
  };
  useEffect(() => {
    if (tab !== "labs" || !anchor) return;
    (document.getElementById(CLOBBER_PREFIX + anchor) ?? document.getElementById(anchor))?.scrollIntoView?.();
    setAnchor(null);
  }, [tab, anchor]);

  // Build the on-page TOC from rendered headings, and track the one in view. Re-run when the tab
  // changes or the drill solution is shown or hidden, since that adds or removes headings.
  useEffect(() => {
    const root = proseRef.current;
    if (!root) return;
    const hs = Array.from(root.querySelectorAll<HTMLElement>("h2, h3"));
    onToc(hs.filter((h) => h.id).map((h) => ({ id: h.id, text: h.innerText ?? h.textContent ?? "", level: Number(h.tagName[1]) })));
    onActiveHeading(null);
    if (typeof IntersectionObserver === "undefined") return;
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) onActiveHeading(visible[0].target.id);
      },
      { root: scrollRef.current, rootMargin: "0px 0px -70% 0px" }
    );
    hs.forEach((h) => obs.observe(h));
    return () => obs.disconnect();
  }, [lesson.id, tab, showSolution, onToc, onActiveHeading]);

  const ask = () => onAsk(`I'm studying the lesson "${lesson.title}" (${courseTitle}). Explain its key ideas and how they connect to the rest of the wiki.`);

  return (
    <div ref={scrollRef} className="course-scroll course-page">
        <article className="lesson">
          <div className="lesson-crumbs">
            <button onClick={() => onOpen(lesson.course)} className="link-btn lesson-crumb">{courseTitle}</button>
            {lesson.section && <> · {lesson.section}</>}
          </div>
          <h1 className="lesson-title">{lesson.title}</h1>
          {glossaryError && <ResourceNotice what="The glossary" error={glossaryError} onRetry={retryGlossary} />}
          {lesson.drill && (
            <div className="lesson-drill">
              <DrillBadges drill={lesson.drill} />
              {lesson.drill.timebox_min ? <DrillTimer lessonId={lesson.id} timeboxMin={lesson.drill.timebox_min} /> : null}
            </div>
          )}
          {lesson.summary && !openingRepeatsSummary(body, lesson.summary) && <p className="lesson-summary">{lesson.summary}</p>}
          {lesson.kind === "drill" || lesson.drill ? (
            <DrillReadAloud key={`read-${lesson.id}`} body={body} />
          ) : (
            <LessonReadAloud key={`read-${lesson.id}`} body={body} title={lesson.title} />
          )}
          {lesson.kind === "drill" || lesson.drill ? (
            <VoiceDrawer key={`voice-${lesson.id}`} subject={lesson.id} target={{ mode: "approach", lesson: lesson.id }} />
          ) : !dictationAllowed(lesson.id) ? (
            <VoiceDrawer key={`voice-${lesson.id}`} subject={lesson.id} target={{ mode: "interview", lesson: lesson.id }} />
          ) : null}
          {tabbed ? (
            <div className="lab-tabs lesson-tabs" role="tablist" aria-label="Parts of this lesson">
              {TABS.map((t) => (
                <button key={t.id} role="tab" id={`lesson-tab-${t.id}`} aria-selected={tab === t.id} aria-controls="lesson-panel"
                  onClick={() => setTab(t.id)} className={`lab-tab${tab === t.id ? " is-active" : ""}`}>
                  {t.label}
                </button>
              ))}
            </div>
          ) : (
            <StudyLevels {...levels} />
          )}

          <div ref={proseRef} id="lesson-panel" role={tabbed ? "tabpanel" : undefined}
            aria-labelledby={tabbed ? `lesson-tab-${tab}` : undefined} className="lesson-panel">
            {!split || !tabbed ? (
              <div className="lesson-prose">
                {parts ? (
                  <>
                    {md(parts[0])}
                    <button onClick={() => setShowSolution((s) => !s)} aria-expanded={showSolution} className="round-btn lesson-solution-btn">
                      {showSolution ? "Hide solution" : "Show solution"}
                    </button>
                    {showSolution && md(parts[1])}
                    {md(parts[2])}
                  </>
                ) : (
                  md(body)
                )}
              </div>
            ) : tab === "lecture" ? (
              <>
                {deck && (
                  <a href={`#/slides/${deck.id}`} className="lesson-lab lesson-deck">
                    <span className="lesson-lab-title">▶ Lecture deck: {deck.title}</span>
                    <span className="lesson-lab-purpose">{deck.subtitle || "The idea and the objectives, as slides. Start here."}</span>
                  </a>
                )}
                {split.objectives && (
                  <section className="lesson-objectives" aria-label="Objectives">
                    <h2 className="section-label">After this note you can answer</h2>
                    <div className="lesson-prose">{md(split.objectives)}</div>
                  </section>
                )}
                {/* Delegated click: the "Code N" links inside are real anchors, so the keyboard already reaches them. */}
                {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */}
                <div className="lesson-prose" onClick={openCode}>{md(split.lecture)}</div>
              </>
            ) : tab === "study" ? (
              <>
                <StudyLevels {...levels} />
                {/* The rows are the note's flashcards; without any, the table is the only place the answers are. */}
                {split.review && !lesson.flashcardCount && <div className="lesson-prose">{md(split.review)}</div>}
                {!hasStudy && <p className="lesson-empty">No review questions for this lesson yet.</p>}
              </>
            ) : (
              <>
                {lesson.labs && lesson.labs.length > 0 && (
                  <div className="lesson-labs">
                    <h2 className="section-label">Labs to run</h2>
                    {lesson.labs.map((lab) => (
                      <a key={lab.id} href={`#/labs/${lab.id}`} className="lesson-lab" title={lab.path}>
                        <span className="lesson-lab-title">▶ {lab.title}</span>
                        {lab.purpose && <span className="lesson-lab-purpose">{lab.purpose}</span>}
                      </a>
                    ))}
                  </div>
                )}
                {split.exercises && (
                  <div className="lesson-prose">
                    {exercises ? (
                      <>
                        {md(exercises[0])}
                        <button onClick={() => setShowSolution((s) => !s)} aria-expanded={showSolution} className="round-btn lesson-solution-btn">
                          {showSolution ? "Hide answers" : "Show answers"}
                        </button>
                        {showSolution && md(exercises[1])}
                        {md(exercises[2])}
                      </>
                    ) : md(split.exercises)}
                  </div>
                )}
                {split.code && <div className="lesson-prose">{md(split.code)}</div>}
                {!hasLabs && <p className="lesson-empty">No code or labs for this lesson yet.</p>}
              </>
            )}
          </div>

          {lesson.concepts.length > 0 && (
            <div className="lesson-concepts">
              <div className="section-label">Concepts in the graph</div>
              <div className="chip-row">
                {lesson.concepts.map((c) => (
                  <button key={c.id} onClick={() => onOpenConcept(c.id)} title={`${c.domain} · ${c.summary}`} className="concept-chip">
                    <span className="text-concept">◆</span> {c.title}
                  </button>
                ))}
              </div>
            </div>
          )}

          {tabbed && <LessonStudyEnd levels={levels} labs={lesson.labs} showLevels={tab !== "study"} showLabs={tab !== "labs"} />}

          <div className="lesson-actions">
            <button onClick={onMarkDone} disabled={done} className={`round-btn${done ? " round-btn--done" : ""}`}>
              {done ? "✓ Completed" : "Mark as complete"}
            </button>
            <button onClick={ask} className="round-btn">Ask the librarian ↗</button>
          </div>

          <ReportButton key={lesson.id} kind="lesson" target={lesson.id} />

          <div className="lesson-pager">
            {lesson.prev ? <PagerLink dir="prev" title={lesson.prev.title} onClick={() => onOpen(lesson.prev!.id)} /> : <span className="grow" />}
            {lesson.next ? <PagerLink dir="next" title={lesson.next.title} onClick={() => onOpen(lesson.next!.id)} /> : <span className="grow" />}
          </div>

          <div className="lesson-source">
            data/courses/{lesson.id}.md{lesson.source && <> · from {lesson.source}</>}
          </div>
        </article>
    </div>
  );
}

/** The end of a note: its own questions, flashcards and worked problems, then the labs that back it. A part the
 * open tab already shows is left out; with nothing to show the block is not drawn. */
function LessonStudyEnd({ levels, labs, showLevels, showLabs }: {
  levels: ComponentProps<typeof StudyLevels>;
  labs?: LabOutline[];
  showLevels: boolean;
  showLabs: boolean;
}) {
  const hasLevels = showLevels && !!(levels.quizCount || levels.flashcardCount || levels.problemCount);
  const hasLabs = showLabs && !!labs?.length;
  if (!hasLevels && !hasLabs) return null;
  return (
    <section className="lesson-end" aria-label="Test yourself and practise">
      {hasLevels && (
        <>
          <h2 className="section-label">Test yourself on this note</h2>
          <StudyLevels {...levels} />
        </>
      )}
      {hasLabs && (
        <>
          <h2 className="section-label">Labs for this note</h2>
          {labs!.map((lab) => (
            <a key={lab.id} href={`#/labs/${lab.id}`} className="lesson-lab" title={lab.path}>
              <span className="lesson-lab-title">▶ {lab.title}</span>
              {lab.purpose && <span className="lesson-lab-purpose">{lab.purpose}</span>}
            </a>
          ))}
        </>
      )}
    </section>
  );
}

function PagerLink({ dir, title, onClick }: { dir: "prev" | "next"; title: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`pager-link pager-link--${dir}`}>
      <div className="pager-link-dir">{dir === "next" ? "Next →" : "← Previous"}</div>
      <div className="pager-link-title">{title}</div>
    </button>
  );
}
