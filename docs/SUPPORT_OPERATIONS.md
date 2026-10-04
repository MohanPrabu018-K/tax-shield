# Support Operations

## Channels
- **In-app desk** (`/support`): signed-in users create tickets, add replies,
  watch status. Reference format `SUP-XXXXXXXX` (ticket ObjectId prefix).
- **Admin console** (`/admin` → Support tab): all tickets, filters, reply,
  status transitions.
- No external helpdesk/ticketing dependency — tickets live in MongoDB.

## Ticket model
```
{ user_id, subject(≤200), priority, status, messages: [{from: user|support,
  body(≤4000), created_at}], created_at, updated_at }
```
- Priorities: `low | normal | high | urgent` (other → 422).
- Statuses: `open | pending | closed` (set by support reply; others → keep old).
- Rate limit: 20 creates / hour / user (429 beyond).
- Required fields enforced (422 when subject/body missing).

## Flows
- **User**: `POST /support` → ticket; `GET /support`, `GET /support/{id}`
  (owner-checked, 404 otherwise); `POST /support/{id}/reply` re-opens to `open`.
- **Support**: `GET /admin/support?status=`, `POST /admin/support/{id}/reply`
  with optional `status` — every admin reply also creates an **in-app
  notification** for the user (category `system`, link `/support`).
- Billing/deletion/privacy questions arrive here; refunds are confirmed by a
  human (see `BILLING.md`), deletion is self-serve (see `PRIVACY_OPERATIONS.md`).

## SLA targets (pilot)
| Priority | First response |
|----------|----------------|
| urgent   | 1 business day |
| high     | 2 business days |
| normal   | 3 business days |
| low      | 5 business days |

## Notifications
`GET /notifications` (9 categories: security, billing, compliance, tax,
invoice, payment, document, ca_review, system), `PATCH /notifications/{id}`
read toggle, `POST /notifications/read-all`. Unread count drives the bell.
