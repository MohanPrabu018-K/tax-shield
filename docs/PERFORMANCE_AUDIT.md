# Performance Audit — TaxShield (Phase 0)

## 1. Backend load (biggest cost)
- `analyze_user_data` on every mutation (`api.py`: transactions, bulk, CSV, delete, investments, deductions, documents, payments, AIS/26AS, seed) AND on reads (dashboard, readiness, tax-detail, chat snapshot). Each run: 4 collection scans + `reconcile_user` (3 more) + per-obligation `replace_one` + deadline inserts.
- Chat `build_snapshot` ≈ 7 DB round-trips per message.
- Mitigation path (Phase 1+): keep behavior identical now; add `?analyze=false` support already on single-create; later move to event → mark-affected → incremental recompute + cached summaries + background jobs. Never recompute history on unrelated writes.

## 2. Query patterns
- `to_list(None)` unbounded on all list endpoints; chat caps inconsistent (200/100/50). Add optional `skip/limit` (default = all, backward compatible) + compound/date/status indexes.
- Missing indexes: `investments {user_id}`, `deductions {user_id}`, `{user_id, transaction_type}` (recon), `{user_id, title}` (obligation upsert), `{user_id, title, due_date}` (deadline dedup). Added in Phase 1.
- Stale deadlines accumulate (insert-only). Add retention note + future cleanup job (never delete regulatory evidence silently).
- Per-row writes: CSV `insert_one` per row; compare loop `find_one` per scenario; obligation `replace_one` per item. Batch where safe.

## 3. Frontend weight
- `recharts` (~300KB+) imported synchronously on dashboard/scenarios/reports — lazy-load via `next/dynamic ssr:false`.
- Dead `date-fns` dep; `axios` vs fetch (keep axios, fine); lucide barrel imports (use per-icon paths where easy).
- 10 parallel requests on reports regime toggle; dashboard `Promise.all` all-or-nothing; client-side filter/slice instead of server pagination; `window.location.href` full reloads; charts rebuilt per render (memoize).
- No `loading.tsx`/`error.tsx` skeletons; spinners only.

## 4. Infra
- Dev servers in containers (`--reload`, `npm run dev`); no `.dockerignore`, healthcheck only on mongo, no resource limits. Fine for zero-cost dev; document prod build (`next build`/`next start`, gunicorn-style workers) without requiring paid infra.

## 5. Targets
- p95 dashboard read < 500ms on demo data; chat < 1.5s; CSV 1k rows without blocking (background job later); JS payload down via dynamic charts; API lists paginated by default in v2 (`/api/v1` keeps compat).

## 6. Frontend productization (update)
- Server pagination on transactions/parties/receivables/journals (`skip/limit` +
  pager); debounced search (400ms); lists capped in attention/search views.
- One parallel `Promise.all` per dashboard load with isolated errors; `useAsync`
  prevents refetch storms; no polling; manual reload after mutations.
- No tax math in React (preview only); CSV import uses one `/transactions/bulk`
  call. No new dependencies. `tsc` clean. Next: `next/dynamic` Recharts,
  virtualized tables, timing harness with `X-Request-ID`.
