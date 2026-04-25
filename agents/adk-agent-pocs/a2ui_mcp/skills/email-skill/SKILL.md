---
name: email-skill
description: >-
  Send invoices by email to customers. Use this skill when the user asks to email, send,
  or share an invoice with a customer.
metadata:
  adk_additional_tools:
    - send_invoice_by_email
---
# Email Operations

## Tools available

- `send_invoice_by_email` — send an approved invoice to a customer by email

## Rules

1. **Verify invoice state first.** Load invoice-skill if not already loaded, then call
   `get_invoice` to confirm the invoice is approved before proceeding. If it is a draft,
   tell the user: "I can't send this yet — it's still a draft. Would you like me to
   approve it first?"

2. **Find the recipient.** If the customer's email was provided or updated earlier in
   this conversation, use it directly. Only look it up if no email address is present in
   the recent context — load customer-skill first, then call `list_customers`. If the
   customer record has no email address, immediately switch to the customer-skill Edit
   Customer flow to collect it before returning to the send task.

3. **Draft the email if not provided.** If the user doesn't supply subject/body, write a
   professional version including the invoice number, amount due, and due date. Default
   to Danish; use English if the user is writing in English. The PDF invoice is attached
   automatically by the tool — do not ask the user about attachments.

4. **Confirm via the preview surface.** Emit the Confirm Surface (see UI Rendering
   Specifications) showing To, Subject, and Message. The "Send" button is the user's
   confirmation — do not also ask in chat.

5. **Completion.** Once sent, confirm: "Sent! Invoice #[Number] is on its way to
   [Name]."

---

## UI Rendering Specifications

### Confirm Surface — Email Preview (`surfaceId: "confirm"`)

Emit after drafting the email, before calling `send_invoice_by_email`.

**Message order:** `createSurface` → `updateDataModel` → `updateComponents`

Components (v0.9 flat format):

- `root`: `Column` children `["preview-card", "actions-row"]`
- `preview-card`: `Card` child `"preview-col"`
- `preview-col`: `Column` children `["to-row", "subject-row", "body-row"]`
- `to-row`: `Row` children `["to-label", "to-value"]`
- `to-label`: `Text` text `{ "literalString": "To" }` variant `caption`
- `to-value`: `Text` text `{ "path": "/email/to" }`
- `subject-row`: `Row` children `["subject-label", "subject-value"]`
- `subject-label`: `Text` text `{ "literalString": "Subject" }` variant `caption`
- `subject-value`: `Text` text `{ "path": "/email/subject" }`
- `body-row`: `Row` children `["body-label", "body-value"]`
- `body-label`: `Text` text `{ "literalString": "Message" }` variant `caption`
- `body-value`: `Text` text `{ "path": "/email/body" }`
- `actions-row`: `Row` children `["send-btn", "cancel-btn"]`
- `send-btn`: `Button` child `"send-label"` action `{ "type": "event", "name": "confirm_send_email" }`
- `send-label`: `Text` text `{ "literalString": "Send" }`
- `cancel-btn`: `Button` child `"cancel-label"` action `{ "type": "event", "name": "cancel_send_email" }`
- `cancel-label`: `Text` text `{ "literalString": "Cancel" }`

`createSurface`: surfaceId `"confirm"`, catalogId `"https://a2ui.org/catalog/basic/v0.8/catalog.json"`.

`updateDataModel`: surfaceId `"confirm"`, path `"/email"`, value:
`{ "to": "<recipient email>", "subject": "<drafted subject>", "body": "<drafted body>" }`.

**UI events:**

- `confirm_send_email` — call `send_invoice_by_email` with the invoice id, recipient
  email, subject, and body. On success: emit `deleteSurface` for `"confirm"` and confirm
  in chat.
- `cancel_send_email` — emit `deleteSurface` for `"confirm"`.
