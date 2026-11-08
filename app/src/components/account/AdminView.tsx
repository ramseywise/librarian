import { useCallback, useEffect, useState } from "react";
import { apiJson, postJson } from "../../utils/api";
import { pageTitle, useDocumentTitle } from "../courses/useDocumentTitle";
import "./account.css";

interface AdminUser {
  id: string;
  email: string;
  name: string | null;
  role: "admin" | "member";
  last_seen_at: string | null;
  chat_spent_today_usd: number;
}
interface Invite { email: string; created_at: string | null; used_at: string | null }
interface AuditEvent { ts: string | null; email: string | null; action: string; target: string | null }

const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString() : "never");

/** Users with their spend and last visit, invites, and the audit trail. Admins only; the routes check. */
export function AdminView() {
  useDocumentTitle(pageTitle("Admin"));
  const [users, setUsers] = useState<AdminUser[] | null>(null);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [u, i, a] = await Promise.all([
        apiJson<AdminUser[]>("/api/admin/users"),
        apiJson<Invite[]>("/api/admin/invites"),
        apiJson<AuditEvent[]>("/api/admin/audit?limit=100"),
      ]);
      setUsers(u);
      setInvites(i);
      setAudit(a);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);
  useEffect(() => void load(), [load]);

  const invite = async (e: React.FormEvent) => {
    e.preventDefault();
    setNotice(null);
    try {
      const r = await postJson<{ email: string; added: boolean }>("/api/admin/invites", { email: email.trim() });
      setNotice(r.added ? `Invited ${r.email}.` : `${r.email} was already invited.`);
      setEmail("");
      await load();
    } catch (err) {
      setNotice((err as Error).message);
    }
  };

  const setRole = async (u: AdminUser, role: AdminUser["role"]) => {
    try {
      await postJson(`/api/admin/users/${encodeURIComponent(u.email)}/role`, { role });
      await load();
    } catch (err) {
      setNotice((err as Error).message);
    }
  };

  if (error) return <div className="course-centered"><div>Could not load the admin page: {error}</div></div>;
  if (!users) return <div className="course-centered"><div>Loading…</div></div>;

  return (
    <div className="course-scroll course-page">
      <div className="course-page-inner">
        <h1 className="course-page-title">Admin</h1>

        <section className="study-block" aria-label="Users">
          <h2 className="study-heading">Users ({users.length})</h2>
          <table className="account-table">
            <thead>
              <tr><th>Email</th><th>Name</th><th>Role</th><th>Chat today</th><th>Last seen</th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{u.name ?? ""}</td>
                  <td>
                    <select aria-label={`Role of ${u.email}`} value={u.role} onChange={(e) => void setRole(u, e.target.value as AdminUser["role"])}>
                      <option value="member">member</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td>${u.chat_spent_today_usd.toFixed(2)}</td>
                  <td>{when(u.last_seen_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="study-block" aria-label="Invites">
          <h2 className="study-heading">Invites</h2>
          <form onSubmit={invite} className="account-form account-form--inline">
            <label htmlFor="invite-email" className="sr-only">Email to invite</label>
            <input id="invite-email" type="email" required placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
            <button type="submit" className="round-btn">Invite</button>
          </form>
          {notice && <p role="status">{notice}</p>}
          <ul className="study-list">
            {invites.map((i) => (
              <li key={i.email}>
                <span className="study-module">{i.email}</span>
                <span className="study-meta">{i.used_at ? `joined ${when(i.used_at)}` : `invited ${when(i.created_at)}`}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="study-block" aria-label="Audit log">
          <h2 className="study-heading">Audit log</h2>
          <table className="account-table">
            <thead>
              <tr><th>When</th><th>Who</th><th>Action</th><th>Target</th></tr>
            </thead>
            <tbody>
              {audit.map((a, n) => (
                <tr key={n}>
                  <td>{when(a.ts)}</td>
                  <td>{a.email ?? ""}</td>
                  <td>{a.action}</td>
                  <td>{a.target ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}
