# Performance — TaxShield

## Done (Phase 1)
New indexes: investments/deductions by user, transactions(user,type),
obligations(user,title), deadlines(user,title,due_date), audit/tax-rules/org
indexes. Optional `skip/limit` on all lists (default full = compatible).
`tsc --noEmit` clean; `robots.ts`/`sitemap.ts`; edge `middleware.ts`
(headers + private-page noindex).

## Next (incremental, no behavior change first)
Event → mark-affected → recompute only affected modules; cached dashboard
summaries; debounce/batch analysis; background jobs for CSV/OCR/recon/reports;
`next/dynamic` for recharts; memoized charts; server pagination default in v2;
projections + aggregation instead of `to_list(None)` scans.
Targets: dashboard p95 <500ms demo data, chat <1.5s, 1k-row CSV non-blocking.
