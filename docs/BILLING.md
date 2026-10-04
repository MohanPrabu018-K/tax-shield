# Billing

## Plans (config-driven, `backend/app/commerce.py`)
| Plan    | Price (INR/mo) | Key limits |
|---------|----------------|------------|
| Free    | 0              | 1k tx, 100 invoices, 100 docs, 5 clients |
| Starter | 499            | 10k tx, 1k invoices, GST, POS |
| Business| 1,499          | 100k tx, TDS, inventory, intelligence |
| Pro     | 3,999          | 1M tx, API access |
| CA      | 9,999          | everything + CA workspace, 5k clients |

Prices are stored in paise-integers (`price_inr`); formatting is frontend-only.
Plan edits are a config change — no schema migration.

## Checkout flow
`POST /api/billing/checkout {plan, provider}`:
- `provider: manual` (default) → subscription `pending_activation`,
  **no charge made**; operator activates after off-platform payment.
- `provider: test` → `test_activated`, message explicitly says TEST ADAPTER.
- any other provider → **422**. The API never pretends a real charge happened.

14-day trial: `POST /api/billing/trial/start {plan}` — one trial per account
(second attempt → 400). Cancel: `POST /api/billing/cancel` → effective plan
falls back to `free` (`_effective_plan`), history keeps `created → trial_started
→ cancelled`.

## Entitlement enforcement
`check_limit(db, user, key)` raises **403 `plan_limit_reached`** before insert
when usage ≥ plan limit (transactions/invoices/documents/clients/products/
storage). `require_feature(ent, feature)` gates GST/TDS/POS/API/CA features.
Hooked into `api.py` (transactions, bulk) and `saas_api.py` (invoice, POS bill,
client create). Response body tells the user the limit and that no paid usage
was triggered.

## Refunds
Provider `refund()` returns `manual_review` — processed by support, confirmed
to the user. Documented at `/refund-policy`.
