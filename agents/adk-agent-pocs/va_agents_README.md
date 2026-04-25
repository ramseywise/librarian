This is a [Next.js](https://nextjs.org) project.

## Installation
First, install the dependencies:

```bash
npm install
```

## Getting Started

First, run the development server:

```bash
aws-vault exec stg -- docker compose up --build
```

Open [http://localhost:3000/va-agents/bot](http://localhost:3000/va-agents/bot) with your browser to see the result.


## Logging to the container

```bash
aws-vault exec stg -- aws ecs execute-command \
    --cluster billy-staging \
    --task $taskId \
    --container va-agents-service \
    --interactive \
    --command "/bin/sh"
```

---

## Features

### Invoices
| Feature | Example message |
|---|---|
| Invoice summary with chart | `Show me the invoice summary for this year` |
| List all invoices | `List all invoices` |
| List filtered invoices | `Show me all overdue invoices` / `List draft invoices from this month` |
| View a single invoice | `Show me invoice #1042` |
| Create a new invoice | `I want to create a new invoice` |
| Create invoice pre-filled | `Create an invoice for Acme Corp with 5 hours of Web Development` |
| Edit a draft invoice | `Update the due date on invoice #1042 to next Friday` |
| Send invoice by email | `Send invoice #1042 to the customer by email` |
| Convert quote to invoice | `I want to create an invoice from an existing quote` |

### Quotes
| Feature | Example message |
|---|---|
| List all quotes | `List all quotes` |
| List filtered quotes | `Show me all accepted quotes` |
| Create a new quote | `I want to create a new quote for Acme Corp` |
| Send quote by email | `Send the quote to the customer by email` |

### Customers
| Feature | Example message |
|---|---|
| List all customers | `List all customers` |
| Create a new customer | `Create a customer named Acme Corp with email info@acme.com` |
| Edit a customer | `Update the phone number for Acme Corp` |

### Products
| Feature | Example message |
|---|---|
| List all products | `List all products` |
| Create a new product | `Create a product called Consulting at 1500 DKK per hour` |
| Edit a product | `Change the price of Web Development to 2000 DKK` |

### Organization
| Feature | Example message |
|---|---|
| Invite a collaborator | `Invite john@example.com as a collaborator` |

### Charts & Visualizations
The assistant automatically includes visual charts alongside summaries and data tables.

| Chart type | When it appears | Example message |
|---|---|---|
| Pie chart | Invoice status breakdown (paid/unpaid/overdue) | `Show me the invoice summary for this year` |
| Bar chart | Monthly or quarterly revenue | `Show me monthly revenue for this year` |
| Line chart | Revenue trend across periods | `Compare 2025 vs 2026 revenue by quarter` |

### Navigation Buttons
After every action, the assistant surfaces clickable buttons that open the relevant page directly in the Billy app.

| Scenario | Button shown |
|---|---|
| After creating/viewing an invoice | "View invoice in Billy" |
| After creating a customer | "View customer in Billy" |
| After listing invoices | "Go to Invoices" |
| After listing quotes | "Go to Quotes" |
| After listing customers | "Go to Customers" |
| When guiding you to a Billy feature | "Go to Transactions", "Go to VAT Declarations", etc. |

### Page Context Awareness
When the assistant is embedded in Billy, it reads the current URL and gives more relevant responses automatically — no extra input needed.

### Suggested Follow-ups
After every response, the assistant suggests 2–4 contextual next actions as clickable chips.

| Scenario | Suggestions shown |
|---|---|
| After listing invoices | "Create a new invoice", "Show invoice summary" |
| After creating a customer | "Create an invoice for this customer", "List all customers" |
| After showing a summary | "List unpaid invoices", "List overdue invoices" |
| After creating an invoice | "Send the invoice by email", "Create another invoice" |
| After creating a quote | "Send the quote by email", "Create invoice from this quote" |
| When more pages exist | "Show next page of invoices / customers / products" |

### Support Knowledge Fallback
When a request is outside the assistant's direct tools (e.g., bank reconciliation, VAT, reports), it searches the Billy support documentation and walks you through it step by step, with source links and navigation buttons.

| Feature | Example message |
|---|---|
| Expense management | `How do I register expenses in Billy?` |
| Bank reconciliation | `How does bank reconciliation work?` |
| VAT reporting | `How do I handle VAT reporting in Billy?` |
| Upload a receipt | `How to upload a receipt?` |
| Reports | `How do I view a profit and loss report?` |
| Chart of accounts | `How do I set up my chart of accounts?` |

### Contact Support Escalation
The assistant automatically shows a **Contact Customer Service** button when:
- It cannot help after multiple attempts
- The user expresses frustration (e.g. `"this is not working"`, `"you're useless"`)
- The same question is asked 3+ times without resolution
- The user asks to speak to a human (e.g. `"I want to talk to someone"`)
