# Production Runbook (pilot)

## Stack
- MongoDB (persistent volume) ← FastAPI (uvicorn, 1 worker) :8000 ← Next.js
  `next start` :3000. `docker-compose.prod.yml` — no dev mounts, no reload.
- Secrets via env: `SECRET_KEY`, `BACKUP_SEAL_SECRET`, `ADMIN_EMAILS`,
  `MONGODB_URL`, `FRONTEND_URL`. Never defaults in production.

## Deploy
```bash
git pull
cd backend && pip install -r requirements.txt      # free PyPI only
cd ../frontend && npm ci && npm run build          # audit: npm audit --omit=dev
docker compose -f docker-compose.prod.yml up -d --build
```

## Health checks
- `GET /health` → `{"status":"healthy"}` (liveness)
- `GET /ready` → `{"status":"ready"}` (DB reachable)
- `GET /api/admin/health` (admin JWT) → API + DB probe detail
- Frontend: `GET /robots.txt`, `/sitemap.xml` return 200.

## Backup (HMAC-sealed)
```bash
cd backend && py scripts/backup.py        # writes backup dir + sealed manifest
BACKUP_SEAL_SECRET=... py scripts/backup.py --verify <dir>   # refuses tampering
```
Schedule nightly; retain per policy (billing 7y, audit 12m, backups per ops).
Restore drill: `docs/LIVE_BACKUP_RESTORE_REPORT.md`.

## Routine ops
| Task | Command / path |
|------|----------------|
| Rotate `SECRET_KEY` | set env → restart → all users re-login (version-safe) |
| Revoke all sessions | users re-login after deploy; per-user: `POST /api/auth/logout-all` |
| Activate tested rules | Admin → Rules (gate enforced) |
| Enable admins | `ADMIN_EMAILS=you@example.com` |
| Rate-limit tuning | `AUTH_RATE_LIMIT`, `AUTH_RATE_WINDOW_SECONDS` env |
| View audit | Admin → Audit (`GET /api/admin/audit`) |
| Incident | `POST /api/admin/incidents` → see `INCIDENT_RESPONSE.md` |

## Scaling notes (known limits)
- Single uvicorn worker + per-read analysis: pilot-scale. Watch p95 from
  `docs/PERFORMANCE_AUDIT.md`; add workers/caching before multi-tenant growth.
- Memory-server Mongo is **test-only**; production must use persistent Mongo.

## Rollback
1. `git checkout <last-good>` → rebuild containers.
2. If data suspect: restore sealed backup (verify first), then audit trail.
3. Open an incident record; notify users in-app if SEV1/SEV2.
