# Subscriptions

## Model (`subscriptions` collection, unique index on `user_id`)
```
{ user_id, plan, status, trial_ends_at, current_period_end, provider,
  created_at, updated_at, history: [{at, event, plan}] }
```
Statuses: `ACTIVE`, `TRIAL`, `CANCELLED`, `EXPIRED`, `SUSPENDED`,
`pending_activation` (manual checkout awaiting operator).

## Lifecycle
1. **Created** lazily on first read (`get_subscription`) as `free/ACTIVE`.
2. **Trial** (14 days): status `TRIAL`; expired trial degrades to free
   automatically in `_effective_plan` — no cron job required.
3. **Activation**: operator (manual) or test adapter flips to `ACTIVE`.
4. **Cancel**: `POST /billing/cancel` → `CANCELLED`; effective plan → `free`
   immediately; data is never deleted by cancellation.
5. **History** is append-only and shown in the billing portal
   (`/billing` page) and admin (`/admin/subscriptions`).

## Downgrade semantics
`_effective_plan()` returns `free` for `CANCELLED|EXPIRED|SUSPENDED` and for
trials past `trial_ends_at`. Existing rows above the new limit are kept (no
data loss); new writes are blocked with 403 until the user deletes or upgrades.

## Admin view
`GET /api/admin/subscriptions` lists every subscription with plan/status/
updated_at for support and finance reconciliation.
