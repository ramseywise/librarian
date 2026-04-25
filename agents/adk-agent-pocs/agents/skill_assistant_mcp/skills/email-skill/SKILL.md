---
name: email-skill
description: >
  Send invoices by email to customers. Use this skill when the user asks to
  email, send, or share an invoice with a customer.
---

# Email Operations

## Tools available
- `send_invoice_by_email` — send an approved invoice to a customer by email

## Rules

1. **Verify invoice state first.** Call `get_invoice` to confirm the invoice is
   approved before proceeding. If it is a draft, tell the user:
   "I can't send this yet — it's still a draft. Would you like me to approve it first?"

2. **Find the recipient.** If the customer's email was provided or updated earlier
   in this conversation, use it directly — do not call `list_customers` again.
   Only look it up if no email address is present in the recent context.

3. **Draft the email if not provided.** If the user doesn't supply subject/body,
   write a professional version including the invoice number, amount due, and due date.
   Default to Danish; use English if the user is writing in English.

4. **Confirm before sending.** Show a preview block:
   - To: [email]
   - Subject: [subject]
   - Message: [body]

   Then ask "Shall I send it?" before calling `send_invoice_by_email`.

5. **Completion.** Once sent, confirm: "Sent! Invoice #[Number] is on its way to [Name]."
