# Commercial SaaS Architecture (Phase 16)

## Scope
How TaxShield became a sellable multi-tenant SaaS without touching the
deterministic tax/accounting core and without paid dependencies.

## Layers
```
frontend (Next.js 14)
  marketing (/) pricing/billing/support/admin/trust pages
  app pages  (dashboard, tax, gst, tds, compliance, ...)
       │ axios Bearer JWT
backend (FastAPI, single uvicorn worker in pilot)
  api.py        core product (transactions, tax, GST, reports, ...)
  saas_api.py   POS, invoices, clients (limit-enforced)
  commerce_api.py  identity, billing, privacy, support, admin, ITR prep
  commerce.py   PLANS / entitlements / providers / retention / notify
  auth.py       bcrypt + JWT (v claim = token_version)
  database.py   tenant-scoped collections + commercial indexes
       │ pymongo
MongoDB (persistent volume in prod; memory-server in tests)
```

## Commercial endpoints (all under `/api`)
- Identity: `password-change`, `password-reset/request|confirm`, `sessions`,
  `logout-all`, `PATCH /me`
- Billing: `plans`, `subscription`, `entitlement`, `history`, `checkout`,
  `cancel`, `trial/start`
- Privacy: `consents`, `retention/policy`, `account/deletion/request|status|execute`
- Support: `support` CRUD + reply, `notifications` list/patch/read-all
- Admin: `overview`, `users`, `subscriptions`, `support`, `audit`, `health`,
  `incidents`, `rules/activate` (all `_require_admin` gated)
- ITR: `itr/preparation` — status `READY_FOR_AUTHORIZED_INTEGRATION`

## Invariants
1. **Server-authoritative entitlements.** Plans/limits live in `commerce.py`;
   limits enforced by `check_limit()`/`require_feature()` inside API handlers.
   Frontend hides features as UX only — editing the client grants nothing.
2. **Never fake money.** `manual` provider → `pending_activation`, `test`
   provider → `test_activated` with "TEST ADAPTER: no real payment occurred."
   Unknown providers are rejected (422), not silently defaulted.
3. **Never fake compliance.** ITR prep never says "filed"; rule activation
   requires `TESTED` status; backups are HMAC-sealed.
4. **Deterministic core untouched.** Statutory tax/GST/TDS/accounting math and
   its 90-test suite unchanged by Phase 16.
5. **Zero paid dependencies.** Only npm/pip packages already in the repo.
