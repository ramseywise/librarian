# Revoke a user

Use when someone must lose access now: a leaver, a leaked laptop, an abusive account. `disable` does all of it in
one step; the owner (`LIBRARIAN_OWNER_EMAIL`) cannot be disabled, because that would lock out the account that can
undo it.

## Symptoms

A person's access must end; or the audit log (`/api/admin/audit`) shows activity you did not expect for an account.

## Checks

```
lb users list                       # role, last seen, "disabled" marker
lb keys list <email>                # their API keys, with last use
```

## Fix

```
lb users disable <email>
```

This sets `disabled_at`, deletes every session of that user and revokes every live API key, in one transaction. A
disabled user cannot sign in again by any method (Google, GitHub, email link) and a still-held cookie or key is
refused on the next request. The same from the browser: `POST /api/admin/users/<email>/disable` as an admin (returns
`sessions_ended` and `keys_revoked`).

To demote instead of lock out: `lb users promote <email> --member`. A role change also ends that user's sessions
(they sign in again and get the new role); keys follow the live role at once.

If the account was an admin and you suspect misuse, also rotate what an admin could read or use: API keys they made
(`lb keys list <email>` before disabling), then `rotate-secrets.md` for anything they could have seen in `.env`.

Undo: `lb users enable <email>`. Keys stay revoked; issue new ones.

## Verify

```
lb users list                       # shows disabled
lb keys list <email>                # all revoked
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer <their old key>" https://<domain>/api/me   # 401
```

Then the audit trail: `curl -s -H "Authorization: Bearer <admin key>" "https://<domain>/api/admin/audit?limit=50"`
must show `user_disable` with your admin as actor and the target email. Review earlier events for the same account
(`login`, `key_create`, `promote`) to see what they did before. Their chat spend for the day is under `/api/admin/users`.
