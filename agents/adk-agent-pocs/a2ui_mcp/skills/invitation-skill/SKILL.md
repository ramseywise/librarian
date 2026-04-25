---
name: invitation-skill
description: >-
  Invite new users to the Billy organisation. Use this skill when the user asks to
  invite, add, or onboard a new team member or collaborator.
metadata:
  adk_additional_tools:
    - invite_user
---

# Invitation Operations

## Tools available

- `invite_user` — send an invitation email to a new collaborator

## Functional Rules

1. **Require a valid email address.** If not provided, ask for it: "What is [Name]'s
   email address?"

2. **Explain the role.** All invites use the "collaborator" role. Include this in the
   confirmation so the user knows what access they are granting: "I'll send an invite to
   [email] as a collaborator, which gives them access to your Billy organisation."
   Collaborators can view invoices, customers, and reports — they cannot change
   organisation settings or billing. If the user asks what a collaborator can do, explain
   this.

3. **The invite form is the confirmation.** Emit the detail surface (see UI Rendering
   Specifications) and wait for the `confirm_invite` event. The send button click is the
   user's approval — no additional chat prompt needed.

4. **Completion.** After a successful call, confirm and set expectations: "Done! I've
   sent the invitation. They just need to click the link in their email to get started."

5. **Bridge after completion.** If the context suggests it (e.g. inviting an
   accountant), offer a relevant follow-up: "Now that they're invited, do you want me to
   list any overdue invoices they should look at?"

---

## UI Rendering Specifications

These are technical rendering requirements. Follow them exactly whenever a tool is
called or a UI event is received.

### Detail Surface — Invitation Form (`surfaceId: "detail"`)

Emit as soon as the user wants to invite someone (before calling `invite_user`). If the
email is already known, pre-populate `/form/email`.

**Message order:** `createSurface` → `updateDataModel` → `updateComponents`

Components (v0.9 flat format):

- `root`: `Column` children `["inv-title", "email-field", "role-note", "actions-row"]`
- `inv-title`: `Text` text `{ "literalString": "Invite Collaborator" }` variant `h2`
- `email-field`: `TextField` value `{ "path": "/form/email" }` type `shortText` label `{ "literalString": "Email address" }` validationRegexp `"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"`
- `role-note`: `Text` text `{ "literalString": "They will be added as a Collaborator" }`
- `actions-row`: `Row` children `["send-btn", "cancel-btn"]`
- `send-btn`: `Button` child `"send-label"` action `{ "type": "event", "name": "confirm_invite", "context": [{"key":"email","value":{"path":"/form/email"}}] }`
- `send-label`: `Text` text `{ "literalString": "Send Invitation" }`
- `cancel-btn`: `Button` child `"cancel-label"` action `{ "type": "event", "name": "cancel_invite" }`
- `cancel-label`: `Text` text `{ "literalString": "Cancel" }`

`createSurface`: surfaceId `"detail"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"detail"`, path `"/form"`, value `{ "email": "<pre-populate if known, else empty string>" }`.

**UI events:**

- `confirm_invite` — call `invite_user` with the `email` from the event context. On
  success: emit `deleteSurface` for `"detail"`. On error (e.g. invalid email): re-emit
  the full `detail` surface with the erroneous email pre-populated in `/form/email` and
  explain the error in chat — do **not** just speak the raw API error.
- `cancel_invite` — emit `deleteSurface` for `"detail"`.
