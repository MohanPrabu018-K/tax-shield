# Development — TaxShield (Windows + Docker)

## Prereqs
Node 18+, Python 3.11+, MongoDB 6+ (or Docker).

## Native Windows
`setup-windows.ps1` (or `.bat`): creates `backend\.venv`, installs
`backend\requirements.txt`, copies `.env.example → .env`, `npm install`.
Run: `run-backend.ps1` (uvicorn :8000) + `run-frontend.ps1` (`npm run dev` :3000).

## Docker (zero-cost local)
`docker compose up -d` → mongodb:27017, backend:8000, frontend:3000.
Linux containers; `venv/bin` paths inside images are correct on Windows hosts.

## Tests
- Unit: `py -m pytest backend/tests -q` (24 foundation tests, no DB).
- E2E (needs stack): `py tests/e2e/full_production_sweep.py`,
  `py tests/e2e/persona_e2e_api.py` (override via `TAXSHIELD_API_URL`).
- Frontend: `node node_modules/typescript/bin/tsc --noEmit` in `frontend/`.

## Conventions
Additive changes only to live paths; fail-closed validation; every mutation
considers DB + API + frontend + authZ + tests + docs (no dead buttons).
