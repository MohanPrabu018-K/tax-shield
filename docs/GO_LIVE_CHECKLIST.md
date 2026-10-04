# Go-Live Checklist

## Blocking (must pass every release)
- [x] `py -m pytest backend/tests` → **104 passed** (incl. 6 live commercial journeys)
- [x] `tsc --noEmit` → 0 errors
- [x] `next build` → success
- [x] `next lint` → no warnings/errors
- [x] Playwright desktop+mobile → **22/22** against production `next start`
- [x] Playwright Firefox (`PLAYWRIGHT_FIREFOX=1 --project=firefox`) → **11/11**
- [x] Playwright WebKit (`PLAYWRIGHT_WEBKIT=1 --project=webkit`) → **11/11**
- [x] `npm audit --omit=dev` → **0 vulnerabilities** (next 15.5.24, react 19,
      axios 1.20, postcss override 8.5.28; leftover 7 are dev-tool-only with
      no upstream fix — see LICENSE/zero-cost audit)
- [x] Live commercial journeys (billing, entitlements, identity, deletion,
      admin, support, ITR prep) green against a running stack

## Secrets & config
- [ ] `SECRET_KEY` real value (not the dev default)
- [ ] `BACKUP_SEAL_SECRET` set; backup `--verify` succeeds
- [ ] `ADMIN_EMAILS` = operator admin (comma-separated)
- [ ] `FRONTEND_URL` matches public origin (CORS)
- [ ] `.env` never committed; `.env.example` has placeholders only
- [ ] Mongo persistent volume + auth enabled; not memory-server

## Runtime
- [ ] `docker-compose.prod.yml` (no dev mounts, no `--reload`)
- [ ] `GET /health` + `/ready` green; uptime check wired
- [ ] Backup job scheduled; restore drill done this quarter
- [ ] TLS terminated at proxy; HTTP→HTTPS redirect
- [ ] Log rotation on uvicorn/docker logs

## Commercial readiness
- [ ] Plans/pricing confirmed (`/pricing` matches `commerce.PLANS`)
- [ ] Refund/privacy/terms/cookie/acceptable-use/disclaimer pages reviewed
- [ ] Support inbox monitored; admin console access verified
- [ ] Trial/checkout wording reviewed (test adapter never shown as real charge)
- [ ] ITR preparation still `READY_FOR_AUTHORIZED_INTEGRATION` (no filing claim)

## Explicit non-claims
- No MFA, no automatic email delivery, no real payment processing, no
  government filing integration. Do not market any of these as shipped.
