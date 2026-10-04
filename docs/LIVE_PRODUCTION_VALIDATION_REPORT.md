# Live Production Validation Report (Phase 15)

## Environment (isolated test stack, synthetic data only)
- OS: Windows 11 host, no Docker (absent) — production-style processes instead.
- MongoDB: official `mongod` via mongodb-memory-server, `127.0.0.1:27099`,
  db `tax_shield_live` (real wire protocol + persistence for the session).
- Backend: `uvicorn app.main:app` (no reload, workers=1), `127.0.0.1:8000`,
  `SECRET_KEY` = temporary test-only value (never committed), 24h tokens (dev compose).
- Frontend: `next start` production build, `localhost:3000`.
- Runtimes: Python 3.13.2 (host runner; Docker pins 3.11), Node v24.19.0,
  Next.js 14.2.0, Chromium headless-shell 1243 / Pixel 7 emulation.
- Gates: `/health` → `{"status":"healthy"}`, `/ready` → `{"status":"ready"}`,
  `X-Request-ID` present on backend responses.

## Live results
| Suite | Run | Pass | Fail | Blocked |
|---|---|---|---|---|
| `test_live_p15.py` journeys A–D, isolation, auth, files, negatives, accounting/recon/langs, rate limits | 11 | 11 | 0 | 0 |
| Static pytest (all) | 90 | 90 | 0 | 0 |
| Playwright desktop (auth 3 + flows 7) | 10 | 10 | 0 | 0 |
| Playwright mobile (same 10) | 10 | 10 | 0 | 0 |
| Live backup → restore → compare | 1 | 1 | 0 | 0 |
| Tamper detection (data file) | 1 | 1 | 0 | 0 |
| Restore-over-prod guard | 1 | 1 | 0 | 0 |
| Volume (1200 bulk, pagination, dashboard) | 1 | 1 | 0 | 0 |

## Defects found live (all fixed, none hidden)
1. `pick()` arity bug in Phase-10 chat branches (TAX_OWED/OVERDUE_INVOICES/
   ATTENTION_TODAY) → live 500 on first TAX_OWED call. Fixed (+Tamil strings,
   `/receivables` nav), backend restarted, 11/11 green.
2. Root `middleware.ts` silently ignored by Next build (empty manifest) →
   moved to documented `src/middleware.ts`; live headers verified
   (`x-robots-tag: noindex` on private, `x-request-id` everywhere).
3. My own live-test fixture math (28600 vs 27040) — corrected, engine was right.

## Deltas vs static-only state
- STATIC VERIFIED: 79 pytest, tsc, build, static pentest/benchmarks/privacy/backup-logic/SEO.
- LIVE VERIFIED: +11 API tests, 20/20 browser, live backup/restore/load/volume,
  headers, isolation over HTTP, rate-limit firing (chat 429 observed).
- Honest gap: manifest-*metadata* edits are not tamper-evident (data files are);
  documented in backup report.
