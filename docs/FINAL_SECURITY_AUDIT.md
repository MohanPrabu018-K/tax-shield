# Final Security Audit (Phase 16)

Method: static auth/authz tests + live HTTP matrix against the running stack
(real server, synthetic users only), plus dependency audit.

## Results — all green

### Identity
- Password change requires correct current password (401 otherwise); bumps
  `token_version` → **all older JWTs immediately 401** (live-verified).
- Password reset: SHA-256-hashed single-use 30-min token; replay → 400
  (live-verified). Dev token returned only when no mail transport exists.
- `POST /auth/logout-all` bumps version, returns a fresh working token; every
  subsequent use of the old token 401s (live-verified).
- `PATCH /me` allowlists 5 fields; unknown keys silently dropped, response
  reports only the fields actually updated (live-verified).
- Sessions endpoint returns only the caller's own events.

### Authorization / tenancy
- Non-admin → 403 on every `/admin/*` endpoint (live-verified for overview;
  same guard `_require_admin` on all).
- Support ticket GET is owner-scoped (other users → 404).
- Rule activation: unknown version → 422; activation writes audit record with
  checksum (live-verified).
- All collections filtered by `user_id` (structural, phase-0 invariant).

### Abuse controls
- Auth rate limit 200/15min/IP; support 20/hour/user; chat limiter — all 429
  with machine-readable detail (observed live during suite runs).
- Uploads capped 10 MB; downloads ownership-checked + attachment disposition.

### Integrity
- Backup manifests HMAC-sealed; tampered data file and tampered manifest
  metadata both detected (tests in `test_hardening.py`).
- Audit events immutable to users; retained 12 months; deletion response
  explicitly lists them as retained.

### Dependencies
- `npm audit --omit=dev`: **0 vulnerabilities** (next 15.5.24, react 19,
  axios 1.20, postcss override 8.5.28).
- Dev-only leftovers: 7 highs in the tailwind 3 / eslint toolchain where the
  upstream advisory (braces ≤3.0.3) has **no fixed release** — build-time
  only, not shipped in the production bundle (First Load JS contains app code,
  not tailwind CLI). Accepted with this note; upgrade to tailwind 4 sequenced.
- Backend requirements unchanged from Phase 15 (all permissive licenses).

## Non-claims
No MFA, no WAF, no external pen-test in Phase 16 (prior `LIVE_PENTEST_REPORT`
stands). Single-worker pilot posture; see `SECURITY_OPERATIONS.md`.
