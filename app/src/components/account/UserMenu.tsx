import { useEffect, useRef, useState } from "react";
import type { AuthConfig, Me } from "../../hooks/useAuth";
import { useSignOut } from "../../hooks/useAuth";
import "./account.css";

/** Who is signed in, their chat spend today, and the links an account needs. */
export function UserMenu({ me, config }: { me: Me | null; config: AuthConfig | null }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const signOut = useSignOut();

  useEffect(() => {
    if (!open) return;
    const close = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === "Escape" : !ref.current?.contains(e.target as Node)) {
        if (e instanceof KeyboardEvent) e.preventDefault();
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);

  if (!me) return config && !config.open ? <a className="pill-btn" href="#/login">Sign in</a> : null;
  // Open (local, no sign-in) mode has one implicit owner: nothing to show or sign out of.
  if (config?.open) return null;

  const budget = me.chat.daily_budget_usd;
  return (
    <div className="user-menu" ref={ref}>
      <button className="pill-btn" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
        {me.name || me.email}
      </button>
      {open && (
        <div className="user-menu-pop" role="menu">
          <div className="user-menu-who">
            <strong>{me.email}</strong>
            <span>{me.role}</span>
          </div>
          <div className="user-menu-spend">
            Chat today: ${me.chat.spent_today_usd.toFixed(2)}
            {budget != null && ` of $${budget.toFixed(2)}`}
          </div>
          {me.role === "admin" && (
            <a role="menuitem" href="#/admin" onClick={() => setOpen(false)}>Admin</a>
          )}
          <a role="menuitem" href="#/privacy" onClick={() => setOpen(false)}>Privacy and terms</a>
          {!config?.open && (
            <button role="menuitem" onClick={() => void signOut()}>Sign out</button>
          )}
        </div>
      )}
    </div>
  );
}
