import { useEffect, useState } from "react";
import { apiFetch } from "../../utils/api";
import { MyFeedback } from "./MyFeedback";
import { Markdown } from "../courses/Markdown";
import { pageTitle, useDocumentTitle } from "../courses/useDocumentTitle";
import "./account.css";

/** What this deployment keeps about its users, the terms of use, and the third-party material notice.
 *  Keep it true: it is checked against `src/librarian/db/tables.py` and the chat telemetry. */
export function PrivacyView() {
  useDocumentTitle(pageTitle("Privacy and terms"));
  const [thirdParty, setThirdParty] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/api/legal/third-party")
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error())))
      .then((t) => !cancelled && setThirdParty(t))
      .catch(() => !cancelled && setThirdParty(""));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner account-legal">
        <h1 className="course-page-title">Privacy and terms</h1>

        <h2>What is stored about you</h2>
        <ul>
          <li><strong>Your account:</strong> email address, the name your sign-in provider gives, role, time zone, when you joined and when you were last seen.</li>
          <li><strong>Sign-in:</strong> session and API key records (only a hash of each key), sign-in links until they expire, and invites.</li>
          <li><strong>An audit log</strong> of sign-ins, refused sign-ins, invites, role changes and key changes.</li>
          <li><strong>Study history:</strong> lessons opened and finished, flashcard grades, quiz answers and drill runs, so your reviews can be scheduled.</li>
          <li><strong>Feedback:</strong> ratings, reports and notes you send.</li>
          <li><strong>Chat usage:</strong> a count per day of requests, tokens and estimated cost, used for the daily budget.</li>
        </ul>

        <p>
          Feedback you send (ratings of answers, notes on pages and lessons, and questions the wiki could not
          answer) is stored with your account, kept for 180 days, and visible to the site admin without your email
          or name. You can delete your own entries here at any time. Anonymised notes may be added to the wiki's
          sources after personal details are removed.
        </p>

        <MyFeedback />

        <h2>What is not stored</h2>
        <ul>
          <li>Chat transcripts. Answers are not kept, and your conversation lives only in your browser tab.</li>
          <li>Passwords: there are none. Google, GitHub or an emailed link confirms who you are.</li>
        </ul>
        <p>
          The text of questions and searches is written to the server's quality logs, with no account attached, to measure
          how well search works. To answer a chat question, the question and the wiki pages it needs are sent to
          Anthropic's API. Error reports and traces, if the owner turns them on, carry no question or answer text unless
          the owner enables that too.
        </p>
        <p>No advertising or analytics trackers are used. The only cookies are the sign-in session and its CSRF token.</p>
        <p>To have your account and history removed, ask the owner of this Librarian.</p>

        <h2>Terms of use</h2>
        <ul>
          <li>This is a personal study tool shared by invitation, provided as it is, with no warranty and no promise of availability.</li>
          <li>Keep your API keys to yourself; revoke a key you no longer use. Chat has a daily spending cap.</li>
          <li>Do not use it to attack the service or other users. The owner may remove any account.</li>
          <li>Course material is for your own study. Third-party material keeps its own licence, listed below.</li>
        </ul>

        <h2>Third-party material</h2>
        {thirdParty === null ? (
          <p>Loading…</p>
        ) : thirdParty ? (
          <Markdown body={thirdParty} lessonId="" onOpenLesson={() => {}} onOpenConcept={() => {}} />
        ) : (
          <p>The third-party notice is not available on this server.</p>
        )}
      </div>
    </div>
  );
}
