# Accounting Engine (Phase 3 — BUILT + TESTED)

## Implementation
- `backend/app/accounting.py`: 33-account CoA seed, `validate_journal`
  (balanced, known accounts, debit-xor-credit), trial balance, P&L,
  balance sheet (balanced incl. net profit), cash-flow buckets
  (operating/investing/financing), `journals_for_transaction` auto-posting map.
- API (`backend/app/saas_api.py`, mounted at `/api`): `POST /accounts/ensure-seed`,
  `GET /accounts`, `POST /journals` (idempotency-key, 409-safe duplicate return),
  `GET /journals`, `POST /journals/{id}/reverse` (offsetting entry, trail kept),
  `GET /ledger/{code}`, `GET /trial-balance`, `GET /reports/profit-loss|balance-sheet|cash-flow`.
- `POST /transactions` auto-posts its accounting leg best-effort (`tx:{id}` key).
- Unique indexes: `accounts(user,code)`, `journals(user,idempotency_key)`.
- Tests: 8 accounting tests in `backend/tests/test_saas.py` (balance invariant,
  reversal netting, P&L/BS math, cash buckets, auto-post map). Flag: `FEATURE_ACCOUNTING=on`.
