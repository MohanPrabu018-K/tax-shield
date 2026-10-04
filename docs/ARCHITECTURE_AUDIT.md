# Architecture Audit — TaxShield (Phase 0)

Date: 2026-10-02. Scope: full repo as found (Windows-converted, commit baseline before SaaS transformation).

## 1. System shape
- Monolith: Next.js 14 App Router (client-rendered pages) + FastAPI + MongoDB (Motor async). No queue, no worker, no cache, no CI.
- Backend entry: `backend/app/main.py` — lifespan connects Mongo, CORS single origin, router at `/api` (`app/api.py`, 47 routes, ~815 lines).
- Deterministic core: `backend/app/analysis.py` `TaxAnalysisEngine` (slabs, rebate, surcharge, cess, obligations, deadlines, readiness, reconciliation). Offline `backend/app/chat.py` assistant (EN/TA/HI + code-mix, 17 intents, browser speech passthrough).
- Data: Pydantic models with `extra="allow"` persisted as raw dicts; 12 collections; indexes for most but not `investments`/`deductions`.

## 2. Request lifecycle
`Browser → Next.js (rewrite /api/* or NEXT_PUBLIC_API_URL) → FastAPI → Motor → Mongo → re-run analyze_user_data on nearly every write → response (full lists, no pagination).`

## 3. Strengths (preserve)
- Deterministic tax math with known slab tables + 87A/surcharge/cess; readiness weights match persona fixtures.
- Tenant isolation consistent (`user_id` filter everywhere except one hole: `upload_document → transactions.update_one` without `user_id`).
- E2E suites strong: 67-assert production sweep + 3-persona suite with cross-user isolation checks.
- Zero paid dependencies; offline assistant; Windows-safe paths/venv after conversion.

## 4. Structural risks
1. Fat router (`api.py`) mixes auth/CRUD/recon/chat/seed — needs boundary split as SaaS grows.
2. `analyze_user_data` runs synchronously on every mutation AND on reads (dashboard/readiness/chat) — 7+ queries per call, unbounded `to_list(None)`.
3. No multi-tenancy (single `user_id` ownership; no org/workspace/roles), no audit log, no request IDs, no error envelope.
4. Tax rules hardcoded (`analysis.py` slabs/thresholds/dates); `datasets/01_tax_rules` not loaded at runtime; responses carry no `rule_version`.
5. Dead weight: empty `alembic/`, `backend/tests/`, `frontend/tests/`, `src/hooks/`; unused `OPENAI_API_KEY`, `httpx`, `faker`, `date-fns`.
6. Frontend client-only auth guard (flash + crawlable), `reports/page.tsx` syntax bug, Badge-variant misuse, triple-hardcoded localhost.

## 5. Target direction (no rewrite)
Keep engine + API contract stable. Add additive layers: request-ID/error middleware, audit log, feature flags, tax-period abstraction, pagination params (default = all, backward compatible), versioned rule registry shadowing hardcoded values, org models for future migration. See `docs/RULE_ENGINE.md`, `docs/SECURITY.md`.
