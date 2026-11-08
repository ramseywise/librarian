import { useState } from "react";
import { useAuthConfig, type LoginMethod } from "../../hooks/useAuth";
import { postJson, setToken } from "../../utils/api";
import { pageTitle, useDocumentTitle } from "../courses/useDocumentTitle";
import "./account.css";

/** What `/#/login?error=<code>` means; the codes come from the server's sign-in refusals. */
const LOGIN_ERRORS: Record<string, string> = {
  not_invited: "That account is not invited to this Librarian. Ask its owner for an invite.",
  cancelled: "Sign-in was cancelled.",
  expired: "The sign-in took too long. Try again.",
  provider: "The sign-in provider could not be reached. Try again.",
  link_expired: "That sign-in link has expired or was already used. Ask for a new one.",
};

const PROVIDERS: Partial<Record<LoginMethod, string>> = { google: "Google", github: "GitHub" };

/** `/login?next=/courses/x&error=...` → its query values. */
function parse(route: string): { next: string; error: string | null } {
  const q = new URLSearchParams(route.split("?")[1] ?? "");
  const next = q.get("next");
  return { next: next && next.startsWith("/") && !next.startsWith("/login") ? next : "/", error: q.get("error") };
}

export function LoginView({ route }: { route: string }) {
  useDocumentTitle(pageTitle("Sign in"));
  const config = useAuthConfig();
  const { next, error } = parse(route);
  // The server redirects to a path; the app's routes live in the hash.
  const serverNext = `/#${next}`;
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [token, setTokenInput] = useState("");

  const sendLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError(null);
    try {
      await postJson("/auth/email", { email: email.trim(), next: serverNext });
      setSent(true);
    } catch (err) {
      setEmailError((err as Error).message);
    }
  };

  const useToken = (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;
    setToken(token.trim());
    window.location.hash = next;
  };

  if (!config) return <div className="course-centered"><div>Loading…</div></div>;

  const providers = config.methods.filter((m) => PROVIDERS[m]);
  return (
    <div className="course-scroll course-page">
      <div className="account-card">
        <h1 className="course-page-title">Sign in to Librarian</h1>
        {error && (
          <p role="alert" className="account-error">
            {LOGIN_ERRORS[error] ?? "Sign-in failed. Try again."}
          </p>
        )}
        {config.open && <p>This Librarian is open: no sign-in is needed. <a href="#/">Go to the graph</a>.</p>}

        {providers.map((p) => (
          <a key={p} className="round-btn account-provider" href={`/auth/login/${p}?next=${encodeURIComponent(serverNext)}`}>
            Continue with {PROVIDERS[p]}
          </a>
        ))}

        {config.methods.includes("email") &&
          (sent ? (
            <p role="status">If {email.trim()} may sign in, a link is on its way. It works once and expires soon.</p>
          ) : (
            <form onSubmit={sendLink} className="account-form">
              <label htmlFor="login-email">Email me a sign-in link</label>
              <input id="login-email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <button type="submit" className="round-btn">Send link</button>
              {emailError && <p role="alert" className="account-error">{emailError}</p>}
            </form>
          ))}

        <details className="account-token" open={!config.open && config.methods.length === 0}>
          <summary>Use an API token</summary>
          <form onSubmit={useToken} className="account-form">
            <label htmlFor="login-token">Bootstrap token or personal key (lk_…)</label>
            <input id="login-token" type="password" autoComplete="off" value={token} onChange={(e) => setTokenInput(e.target.value)} />
            <button type="submit" className="round-btn">Use token</button>
          </form>
          <p className="account-hint">Kept in this browser only. Signing out forgets it.</p>
        </details>

        <p className="account-hint"><a href="#/privacy">Privacy and terms</a></p>
      </div>
    </div>
  );
}
