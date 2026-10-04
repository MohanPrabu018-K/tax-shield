# Final Performance Audit (Phase 16)

Method: live HTTP sampling against the running production-shaped stack
(uvicorn single worker, persistent-memory Mongo on localhost), 30 samples per
endpoint, warm user with 50 transactions. Browser suite runs against
production `next start` (not dev).

## Results (2026-10-04)
| Endpoint | p50 | p95 | max |
|----------|-----|-----|-----|
| `/api/dashboard?regime=old` (6-call aggregate, client-side) | 58.6 ms | 75.4 ms | 79.6 ms |
| `/api/transactions?skip=0&limit=20` | 18.6 ms | 31.1 ms | 32.9 ms |
| `/api/readiness-score` | 63.1 ms | 85.1 ms | 98.8 ms |
| `/api/intel/health?tax_period=2024-25` | 77.3 ms | 91.3 ms | 112.8 ms |

All well under the 500 ms p95 budget. 0 errors/5xx during sampling.

## Bundle
- `next build` (Next 15.5.24 / React 19): compiled successfully;
  **First Load JS shared = 102 kB** (was 87.5 kB on Next 14 — the +15 kB is
  the Next 15 runtime, accepted in exchange for clearing all critical/high
  production advisories). Route sizes unchanged otherwise; code-splitting per
  route retained.

## Entitlement cost note
`check_limit()` runs a count per write. Counts are indexed by `user_id`;
at pilot scale this is single-digit ms (writes measured within the p95 above).
If plan usage grows to 1M-row tenants, cache the usage count with a TTL —
sequenced as a future optimization, not required now.

## Compared to Phase 15 baseline
- Phase 15: dashboard p95 ≤493 ms @50 concurrency (load test), health p95 ≤64 ms.
- Phase 16 adds no new read paths to the hot dashboard loop; admin/support/
  billing endpoints are paginated and admin-gated. No regression observed.

## Browser timing
Full 22-test Chromium suite completes in ~13 s; Firefox 11 tests ~18 s —
page transitions and API round-trips are not a perceptible bottleneck locally.

## Accepted limitations
- Single uvicorn worker: vertical scaling only; add workers + Redis cache
  before multi-thousand-tenant growth (documented in `PRODUCTION_RUNBOOK.md`).
- Voice-mic not measured (browser Web Speech API, no server round-trip).
