# Security Operations

## Authentication
- bcrypt-hashed passwords; JWT Bearer (HS256), 24h expiry, `SECRET_KEY` from env.
- **Token-version binding**: every token carries `v` = user's `token_version`.
  Password change, password reset, and logout-all increment it → all older
  tokens 401 immediately (stateless global revocation).
- Sessions: JWT is stateless; `GET /auth/sessions` lists recorded sign-in/
  auth events; `POST /auth/logout-all` bumps the version and returns a fresh
  working token.
- Password reset: single-use, SHA-256-stored, 30-minute tokens. In dev (no
  email transport) the response includes `dev_reset_token`; reuse → 400.
- Password policy: min 8 chars (`MIN_PASSWORD_LEN`).
- No MFA shipped — **deliberately shown as absent**, never simulated.

## Authorization
- Tenant isolation: every query filtered by `user_id`; downloads are
  ownership-checked (no public URLs).
- Admin console (`/admin/*`) gated by `_require_admin`: `is_admin` flag or
  `ADMIN_EMAILS` env allowlist. Non-admin → 403 (live-tested).
- Rule activation (`POST /admin/rules/activate`) requires a `TESTED` rule
  version; unknown version → 422; every activation is audited with checksum.

## Abuse controls
- Rate limits: login/register 200 attempts / 15 min / IP; chat separate limiter.
  Exceed → 429 with retry guidance.
- Upload cap `MAX_UPLOAD_BYTES` (10 MB); upload MIME/extension validation;
  `Content-Disposition: attachment` on downloads; no path traversal
  (filenames server-generated).
- 429/401/403/422 handled with machine-readable `detail`; request IDs on
  error responses for support tracing.
- CORS locked to `FRONTEND_URL`.

## Integrity
- Backup manifests sealed with HMAC (`BACKUP_SEAL_SECRET`); verify detects
  both data-file and manifest-metadata tampering.
- Audit trail (`audit_events`) records register/login/password/profile/billing/
  admin actions with request IDs; retained 12 months, never user-deletable
  (shown in the deletion response as retained-with-reason).

## Verification
Static auth/IDOR/upload/injection tests + live matrix in
`test_live_commercial.py` (version revocation, reset single-use, admin 403,
rule-gate 422). Prior phases: `LIVE_PENTEST_REPORT.md`, `SECURITY_AUDIT.md`.
