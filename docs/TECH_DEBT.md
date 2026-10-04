# Tech Debt — TaxShield (Phase 0)

Prioritized, evidence-linked. P0 = fix now; P1 = this transformation; P2 = later.

## P0 (breaks build/correctness)
- `frontend/src/app/reports/page.tsx:149-154` — `map(([k,v]) => (` closed with `)}`; `next build`/`tsc` fails. Fix parens.
- `frontend` Badge misuse: `variant={... as any}` with color-class strings (`transactions`, `scenarios`, `obligations`, `documents`) — renders unknown classes. Pass `low|medium|high|...` only.
- `backend/app/auth.py:11` `tokenUrl="/api/auth/login"` — real route is `/api/login`. Docs-only bug; fix to `/api/login`.
- `GET /api/demo/seed` (`app/api.py:609`) wipes 7 collections via GET. Keep GET alias for compat, add canonical `POST /demo/seed`.

## P1 (transformation scope)
- Duplicated date parsing ×4 (`models.py:36,212,262,477`); tax math in 3 places (`analysis.py`, `api.py:488,591`, `chat.py`); risk derivation re-queried per caller.
- `extra="allow"` on 10/12 models — arbitrary client fields persisted to Mongo. Restrict to known fields on writes.
- Invalid `ObjectId` hex → 500 on transaction/obligation/deadline/scenario paths (docs paths already 404). Add helper returning 404/422.
- `modified_count==0 → 404` misfires on no-op PATCH. Check existence first.
- CSV upload silent row skips, in-memory `file.read()`, no size/row caps. Add summary counts + limits.
- Analysis re-runs on reads; unbounded lists; stale deadlines never deleted; missing `investments`/`deductions` indexes.
- Frontend: client-only guards (add `middleware.ts` + `noindex` on private routes), per-page metadata, `normalize()` kept, remove `date-fns`, lazy-load `recharts`, centralize category/FY constants, fix transaction-edit duplicate bug (`transactions/page.tsx:59-61` calls create on edit).
- Empty dirs: `alembic/`, `backend/tests/`, `frontend/tests/`, `src/hooks/`, `src/components/forms/` (missing). Add pytest suite; remove or document Alembic (Mongo needs none).

## P2 (later phases)
- Split `api.py` by domain; materialized dashboard summaries; background jobs for OCR/imports/recon; idempotency keys; refresh-token rotation; Tally/Excel adapters; PWA/offline shell.
