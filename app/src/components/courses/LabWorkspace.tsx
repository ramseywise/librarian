import { python } from "@codemirror/lang-python";
import CodeMirror from "@uiw/react-codemirror";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { LabChatContext } from "../../hooks/useChatStream";
import { outputText, useLabRun, type LabRunMode } from "../../hooks/useLabRun";
import { useTheme } from "../../hooks/useTheme";
import { apiJson } from "../../utils/api";
import { changedFiles, languageLabel, moduleLabel, runVerdict } from "../../utils/labs";
import type { LabDetail } from "./types";
import { pageTitle, useDocumentTitle } from "./useDocumentTitle";
import "./courses.css";

interface Props {
  labId: string;
  onOpenLesson: (lessonId: string) => void;
  onBack: () => void;
  /** Open the chat and send a question; the chat carries this lab's context while it is open. */
  onAsk: (question: string) => void;
  /** Register what the chat is told about the open lab (null on leaving it). */
  onChatContext: (get: (() => LabChatContext) | null) => void;
}

const DRAFT_KEY = (labId: string) => `librarian.lab.${labId}`;

function loadDraft(labId: string): Record<string, string> {
  try {
    const raw = window.localStorage.getItem(DRAFT_KEY(labId));
    const parsed: unknown = raw ? JSON.parse(raw) : null;
    return parsed && typeof parsed === "object" ? (parsed as Record<string, string>) : {};
  } catch {
    return {};
  }
}

function saveDraft(labId: string, edits: Record<string, string>) {
  try {
    if (Object.keys(edits).length) window.localStorage.setItem(DRAFT_KEY(labId), JSON.stringify(edits));
    else window.localStorage.removeItem(DRAFT_KEY(labId));
  } catch {
    // storage blocked: the draft lasts for this page only
  }
}

/** A lab's workspace: its files in an editor, Run and Check on this machine, the output and figures, and the chat. */
export function LabWorkspace({ labId, onOpenLesson, onBack, onAsk, onChatContext }: Props) {
  const [lab, setLab] = useState<LabDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState("");
  const [edits, setEdits] = useState<Record<string, string>>(() => loadDraft(labId));
  const { run, start, stop } = useLabRun(labId);
  const theme = useTheme();
  useDocumentTitle(pageTitle(lab?.title ?? "Lab"));

  // App keys this component by lab id, so the state above is always this lab's.
  useEffect(() => {
    let live = true;
    apiJson<LabDetail>(`/api/courses/labs/${labId}`).then(
      (d) => {
        if (!live) return;
        setLab(d);
        setActive(d.files[0]?.path ?? "");
      },
      (e: unknown) => live && setError(e instanceof Error ? e.message : String(e)),
    );
    return () => { live = false; };
  }, [labId]);

  useEffect(() => saveDraft(labId, lab ? changedFiles(lab, edits) : edits), [labId, lab, edits]);

  // The chat reads the latest editor and run through refs, so registering once is enough.
  const stateRef = useRef({ lab, edits, run });
  stateRef.current = { lab, edits, run };
  useEffect(() => {
    onChatContext(() => {
      const { lab: l, edits: e, run: r } = stateRef.current;
      return { id: labId, files: l ? changedFiles(l, e) : {}, output: outputText(r), exit: r?.exit ?? null };
    });
    return () => onChatContext(null);
  }, [labId, onChatContext]);

  const file = lab?.files.find((f) => f.path === active);
  const text = file ? (edits[file.path] ?? file.text) : "";
  const changed = lab ? changedFiles(lab, edits) : {};
  const extensions = useMemo(() => (active.endsWith(".py") ? [python()] : []), [active]);

  const onChange = useCallback(
    (value: string) => {
      if (!file) return;
      setEdits((prev) => ({ ...prev, [file.path]: value }));
    },
    [file],
  );

  const resetFile = () => {
    if (!file) return;
    setEdits((prev) => {
      const next = { ...prev };
      delete next[file.path];
      return next;
    });
  };

  const go = (mode: LabRunMode) => lab && start(mode, changedFiles(lab, edits));

  const review = () =>
    onAsk(
      run
        ? `Review my run of this lab. Say whether the output shows what the lab is meant to demonstrate, explain any error and what caused it, and suggest one change to try next.`
        : `Walk me through this lab: what it demonstrates, how the code does it, and what to look for when I run it.`,
    );

  if (error) {
    return (
      <div className="course-scroll course-page">
        <div className="course-page-inner">
          <button onClick={onBack} className="practice-link">← All labs</button>
          <div className="practice-error">Could not load this lab: {error}</div>
        </div>
      </div>
    );
  }
  if (!lab) return <div className="app-loading">Loading lab…</div>;

  const runnable = lab.canRun && (lab.run || lab.check);
  const verdict = run ? runVerdict(run) : null;
  const dirty = Object.keys(changed).length;

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner lab-page">
        <button onClick={onBack} className="practice-link">← All labs</button>
        <h1 className="course-page-title">{lab.title}</h1>
        <div className="lab-crumbs">
          {lab.course} · {moduleLabel(lab.module)} · <code>{lab.path}</code> · {languageLabel(lab.language)}
        </div>
        {lab.purpose && <p className="course-page-lede">{lab.purpose}</p>}
        {lab.notes.length > 0 && (
          <div className="chip-row lab-notes">
            <span className="section-label">Notes</span>
            {lab.notes.map((n) => (
              <button key={n.id} onClick={() => onOpenLesson(n.id)} title={n.summary} className="concept-chip">
                ▤ {n.title}
              </button>
            ))}
          </div>
        )}

        <div className="lab-toolbar">
          {lab.canRun && lab.run && (
            <button onClick={() => go("run")} disabled={run?.running} className="round-btn round-btn--primary" title={lab.run}>
              ▶ Run
            </button>
          )}
          {lab.canRun && lab.check && (
            <button onClick={() => go("check")} disabled={run?.running} className="round-btn" title={lab.check}>
              ✓ Check
            </button>
          )}
          {run?.running && <button onClick={stop} className="round-btn">■ Stop</button>}
          <button onClick={review} className="round-btn">{run ? "Review my run ↗" : "Explain this lab ↗"}</button>
          <span className="grow" />
          {file && file.path in changed && (
            <button onClick={resetFile} className="practice-link" title="Discard your edits to this file">
              Reset {file.path}
            </button>
          )}
        </div>
        {!runnable && (
          <div className="lab-callout">
            {!lab.canRun ? (
              <>Running labs is local only. With the API started by <code>make api</code>, Run and Check appear here; or run it yourself from <code>{lab.course}/{lab.module}/practice</code> in the course repo:</>
            ) : (
              <>This app runs Python labs only. Run it yourself from <code>{lab.course}/{lab.module}/practice</code> in the course repo:</>
            )}{" "}
            <code>{lab.run ?? lab.check ?? (lab.verifiedBy || "see the lab's README")}</code>
          </div>
        )}

        {lab.files.length > 1 && (
          <div className="lab-tabs" role="tablist" aria-label="Lab files">
            {lab.files.map((f) => (
              <button
                key={f.path}
                role="tab"
                aria-selected={f.path === active}
                onClick={() => setActive(f.path)}
                className={`lab-tab${f.path === active ? " is-active" : ""}`}
              >
                {f.path}{f.path in changed ? " •" : ""}
              </button>
            ))}
          </div>
        )}
        {file ? (
          <div className="lab-editor">
            <CodeMirror
              value={text}
              onChange={onChange}
              extensions={extensions}
              theme={theme}
              basicSetup={{ foldGutter: false }}
              aria-label={`Editor: ${file.path}`}
            />
          </div>
        ) : (
          <div className="practice-status">This lab has no files to edit here (a notebook or a large folder).</div>
        )}
        {dirty > 0 && (
          <div className="lab-dirty">
            {dirty} file{dirty === 1 ? "" : "s"} edited · runs use your edits in a scratch copy; the course files are never changed.
          </div>
        )}

        {run && (
          <div className="lab-output" aria-live="polite">
            <div className="lab-output-head">
              <code>$ {run.command || "…"}</code>
              {run.running && <span className="lab-running">running…</span>}
              {verdict && <span className={verdict.ok ? "lab-verdict text-success" : "lab-verdict lab-verdict--fail"}>{verdict.text}</span>}
            </div>
            {run.output.length > 0 && (
              <pre className="lab-stream">
                {run.output.map((c, i) => (
                  <span key={i} className={c.stream === "stderr" ? "lab-stderr" : undefined}>{c.text}</span>
                ))}
              </pre>
            )}
            {run.truncated && <div className="lab-dirty">Output cut off at the server's limit.</div>}
            {run.images.map((img) => (
              <figure key={img.path} className="lab-figure">
                <img src={`data:${img.mime};base64,${img.data}`} alt={`Figure written by the run: ${img.path}`} />
                <figcaption>{img.path}</figcaption>
              </figure>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
