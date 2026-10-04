# Frontend Product Audit (Stage A–O complete)

## What was built
- **Shell**: grouped nav (HOME/MONEY/SELL/ACCOUNTING/TAX/COMPLIANCE/MANAGE) with
  user-type gating (`workspace.ts`), fixed Header (no double offset, full titles,
  real search/notifications links, no fake badge count), `middleware.ts` headers.
- **Shared**: `useApi` hooks (no refetch storms), `State` (loading/empty/error/
  retry/skeleton), `Pager` (server pagination), fixed `TableCell colSpan`.
- **Screens (all backed by real APIs, zero dead buttons)**:
  onboarding (progressive, local profile), dashboard (health, 8 KPIs, quick
  actions, attention, readiness, income, cash), transactions (server pagination,
  search/filters, add/delete; fake edit removed), banking (CSV analyze with
  dup/invalid counts + mapped bulk import, AIS/26AS recon detail),
  customers/vendors (CRUD + per-party outstanding + invoice drill-down),
  receivables/payables (ageing + record-payment), invoices (GST-aware create,
  lifecycle transitions, detail), accounting (CoA/journals/TB/P&L/BS/cash +
  manual balanced journals + reversals + ledger lookup), GST (GSTR-1/3B prep,
  GSTIN check, books↔portal), TDS (calculator + record + list), tax (position +
  calculation-details, planning with evidence, gains estimator), AIS page,
  compliance center (urgency groups), month-end close, intelligence (health,
  anomalies, assumption-stated forecast), inventory, POS (cart→paid bill),
  practice (clients/tasks/doc-requests/reviews), search (5 collections),
  notifications (in-app only), settings (rewritten — see below), assistant/voice
  (pre-existing, extended intents), reports/scenarios/obligations/deadlines kept.
- **Settings honesty pass**: removed fake "demo mode" saves, fake Change
  Password/2FA, dead export/import buttons, mislabeled danger zone. Profile is
  read-only (no PATCH /me endpoint exists); exports are real downloads
  (`/exports/*`); AI/alert prefs are device-local and labeled so.

## Deltas to backend
- Added `GET /reviews` (practice UI needed it), `verifyDocument`,
  `gstReconcile`, `forecastCash`, TDS/party/practice client methods,
  `getTransactionsPaginated`. Backend `doc_verify` maps `complete→verified`.
- No deterministic logic duplicated in React: tax/GST/TDS/journal math stays
  server-side; invoice form shows a client-side preview but the created record
  uses backend-computed totals.

## Known limitations (honest)
- No PATCH /me (profile read-only), no change-password/2FA/delete-account
  endpoints (absent from UI, documented in Settings), no recurring invoices or
  quotations UI (no backend models), month-end close is advisory (no locked
  close yet), POS is online-only, notifications in-app only.
