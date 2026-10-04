# Security — TaxShield ( implemented Phase 0–2 )

## Implemented
- JWT Bearer + bcrypt; server-side auth on every data route; tenant scoping by
  `user_id` (traversal hole in document→transaction linking fixed).
- `X-Request-ID` middleware, security headers (nosniff, referrer-policy,
  permissions-policy, SAMEORIGIN framing), consistent error envelope, no stack traces.
- Invalid ObjectId → 404; enum coercion → 422; existence-check before PATCH 404s.
- Upload caps (10MB, extension/MIME allowlist, UTF-8 + 5000-row CSV caps with
  imported/skipped summary); authenticated ownership-checked downloads only.
- Generous auth rate limiting (login/register 200/15min/IP; chat 30/min/user).
- `audit_events` collection (best-effort LOGIN/REGISTER/mutations).
- Secrets: only `NEXT_PUBLIC_API_URL` in frontend; `.env` ignored; compose dev
  key must be replaced in prod via environment.

## Still required (later phases)
Refresh rotation/revocation, `sub=user_id` migration, account lockout/backoff,
admin 2FA architecture, malware-scan hook activation, per-org isolation tests.
See `docs/SECURITY_AUDIT.md`, `backend/tests/test_foundation.py`.
