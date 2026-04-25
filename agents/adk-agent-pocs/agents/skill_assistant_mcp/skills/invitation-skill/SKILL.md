---
name: invitation-skill
description: >
  Invite new users to the Billy organisation. Use this skill when the user
  asks to invite, add, or onboard a new team member or collaborator.
---

# Invitation Operations

## Tools available
- `invite_user` — send an invitation email to a new collaborator

## Rules

1. **Require a valid email address.** If not provided, ask for it:
   "What is [Name]'s email address?"

2. **Explain the role.** All invites use the "collaborator" role. Include this
   in the confirmation so the user knows what access they are granting:
   "I'll send an invite to [email] as a collaborator, which gives them access
   to your Billy organisation."

3. **Confirm before inviting.** Show a summary:
   - Inviting: [email]
   - Role: Collaborator

   Then ask "Send the invite now?" before calling `invite_user`.

4. **Completion.** After a successful call, confirm and set expectations:
   "Done! I've sent the invitation. They just need to click the link in their
   email to get started."

5. **Bridge after completion.** If the context suggests it (e.g. inviting an
   accountant), offer a relevant follow-up:
   "Now that they're invited, do you want me to list any overdue invoices they
   should look at?"
