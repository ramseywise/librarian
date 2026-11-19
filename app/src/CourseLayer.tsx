import { lazy, Suspense } from "react";
import { ErrorBoundary } from "./components/ErrorBoundary";
import type { LabChatContext, StudyChatContext } from "./hooks/useChatStream";
import type { CoursePage } from "./routes";

// Courses, Practice and Labs pull in react-markdown + KaTeX (Labs, CodeMirror); load them only when opened.
const CoursesView = lazy(() =>
  import("./components/courses/CoursesView").then((m) => ({ default: m.CoursesView }))
);
const FlashcardsView = lazy(() =>
  import("./components/courses/FlashcardsView").then((m) => ({ default: m.FlashcardsView }))
);
const SlidesView = lazy(() =>
  import("./components/courses/SlidesView").then((m) => ({ default: m.SlidesView }))
);
const QuizView = lazy(() =>
  import("./components/courses/QuizView").then((m) => ({ default: m.QuizView }))
);
const StudyHome = lazy(() =>
  import("./components/courses/StudyHome").then((m) => ({ default: m.StudyHome }))
);
const PracticeView = lazy(() =>
  import("./components/courses/PracticeView").then((m) => ({ default: m.PracticeView }))
);
const LabsView = lazy(() =>
  import("./components/courses/LabsView").then((m) => ({ default: m.LabsView }))
);
const LabWorkspace = lazy(() =>
  import("./components/courses/LabWorkspace").then((m) => ({ default: m.LabWorkspace }))
);
const LoginView = lazy(() => import("./components/account/LoginView").then((m) => ({ default: m.LoginView })));
const AdminView = lazy(() => import("./components/account/AdminView").then((m) => ({ default: m.AdminView })));
const PrivacyView = lazy(() =>
  import("./components/account/PrivacyView").then((m) => ({ default: m.PrivacyView }))
);

interface Props {
  /** The page to draw, from `parseRoute`. */
  page: CoursePage;
  /** The raw hash route; the login page reads its `?next=`. */
  route: string;
  navigate: (path: string) => void;
  openLesson: (lessonId: string) => void;
  openLab: (id: string) => void;
  openConcept: (pageId: string) => void;
  askAbout: (question: string) => void;
  setLabContext: (get: (() => LabChatContext) | null) => void;
  setStudyContext: (get: (() => StudyChatContext | null) | null) => void;
}

/** Every page drawn over the graph, behind one error boundary (reset by the route) and one Suspense. */
export function CourseLayer({
  page, route, navigate, openLesson, openLab, openConcept, askAbout, setLabContext, setStudyContext,
}: Props) {
  return (
    <div className="app-course-layer">
      <ErrorBoundary what="This page" resetKey={route}>
        <Suspense fallback={<div className="app-loading">Loading…</div>}>
          {renderPage()}
        </Suspense>
      </ErrorBoundary>
    </div>
  );

  function renderPage() {
    switch (page.page) {
      case "login":
        return <LoginView route={route} />;
      case "admin":
        return <AdminView />;
      case "privacy":
        return <PrivacyView />;
      case "study":
        return <StudyHome />;
      case "slides":
        return <SlidesView deckId={page.deckId} onAsk={askAbout} />;
      case "quiz":
        return <QuizView quizId={page.quizId} onChatContext={setStudyContext} />;
      case "lab":
        return (
          <LabWorkspace
            key={page.labId}
            labId={page.labId}
            onOpenLesson={openLesson}
            onBack={() => navigate("/labs")}
            onAsk={askAbout}
            onChatContext={setLabContext}
          />
        );
      case "labs":
        return <LabsView onOpenLab={openLab} onOpenLesson={openLesson} onOpenDrills={() => navigate("/practice")} />;
      case "practice":
        return <PracticeView onOpenLesson={openLesson} onOpenConcept={openConcept} />;
      case "flashcards":
        return <FlashcardsView deckId={page.deckId} onChatContext={setStudyContext} />;
      case "courses":
        return <CoursesView route={page.path} navigate={navigate} onOpenConcept={openConcept} onAsk={askAbout} />;
    }
  }
}
