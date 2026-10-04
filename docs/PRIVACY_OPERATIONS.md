# Privacy Operations

## User-facing controls (all live)
- **Consents** (`POST/GET /api/consents`): purposes = `essential`,
  `communications`, `ai_processing`, `analytics`, `marketing`. Server-side
  history is kept; unknown purpose → 422. UI: Settings → Privacy panel.
- **Retention policy** (`GET /api/retention/policy`): mirrors `RETENTION` in
  `commerce.py` — financial/tax evidence never auto-purged; audit events 12m;
  chat/notifications 12m; support 24m; billing records 7y.
- **Deletion workflow**:
  1. `POST /account/deletion/request` → 7-day grace, user data intact.
  2. `GET /account/deletion/status` shows the pending window.
  3. `POST /account/deletion/execute` requires `{"confirm":"DELETE"}`;
     during grace also `skip_grace:true`. Purges 28 user collections +
     uploaded files from disk; **retains** `audit_events` (security),
     `subscriptions` (billing 7y), `tax_rules` (regulatory) — each returned
     in the response with its reason. User document is deleted; login then 401s.

## Processing defaults
- Assistant answers are deterministic and tool-backed — **no external LLM
  calls at all** (see `AI_POLICY.md`); the `ai_processing` consent is recorded
  for future model-based flows but nothing shipped sends data to third
  parties. No paid API is ever called automatically.
- No analytics/ad trackers; cookie notice documents "essential sign-in session
  plus on-device preferences".
- Fixtures/demo data are PII-free; exports are tenant-scoped.

## Data-subject requests in practice
Support ticket (`/support`) is the intake channel; the deletion endpoints are
self-serve. Deletion is verified live in
`backend/tests/test_live_commercial.py::test_deletion_workflow_live`.
