# UX Audit (frontend productization)

## Principles applied
- User never needs accounting knowledge: events first (invoice, bill, payment),
  journals visible as readable entries with plain-language narration.
- Progressive onboarding (4 steps, skippable detail, no 100-question signup);
  dashboard adapts via workspace profile; individuals don't see Practice/POS/Inventory.
- Every page: loading → content | empty (with next action) | error (with retry).
  No blank screens; destructive actions confirm; toasts confirm outcomes.

## Flows verified by construction
- Transaction → auto-journal → dashboard/tax refresh (quick actions deep-link
  with `?action=new` auto-opening the create modal).
- Invoice → totals preview → backend-computed record → lifecycle buttons →
  payment → receivables update → journal legs.
- POS → stock check → paid invoice + books + stock decrement in one response.
- Compliance → obligation/deadline detail → document upload/verify → re-analysis.

## Fixes
- Removed fake transaction "Edit" (created duplicates); removed fake settings
  saves; fixed `₹12 KB` file-size bug (now `12 KB`); fixed Badge-variant misuse
  (transactions, documents); added aria-labels on icon buttons, `role=status`
  live regions, dialog semantics, table captions via headers, focus-visible
  rings from base Button/Input/Select.

## Remaining
- Formal keyboard trap in Modal, virtualized tables >500 rows, offline draft
  queue (PWA shell), per-row receipt print view.
