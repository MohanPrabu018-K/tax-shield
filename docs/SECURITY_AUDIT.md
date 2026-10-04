# Security Audit — TaxShield (Phase 0)

## 1. Tenant isolation
- PASS almost everywhere: every data route filters `user_id` (verified across transactions/investments/deductions/documents/obligations/deadlines/scenarios/payments/AIS/26AS/chat).
- FAIL (1): `POST /documents` links `related_transaction_id` via `transactions.update_one({"_id": ...})` (`app/api.py:294-298`) with no `user_id` check — User A knowing User B's transaction id can overwrite its `document_id`. Fix: add `user_id` to that filter (done in Phase 1 hardening where touched; full fix scheduled with tenancy migration).
- No org-level isolation yet (single-user ownership). New `Organization/Workspace/Business/Membership` models added as future layer; all authorization stays server-side, never trusts frontend IDs.

## 2. Auth/session
- bcrypt hashing, JWT HS256, 24h expiry, `sub=email` (should migrate to user id). No refresh rotation/revocation; logout is client-only. Login/register have no rate limit (chat only: 30/min in-memory, non-distributed). `login()` auto-registers on 401 (frontend) — account-creation without validation; backend correctly returns 401.
- `tokenUrl` docstring wrong (`/api/auth/login` vs real `/api/login`) — fixed.

## 3. Uploads/downloads
- Traversal mitigated (`Path.name` + Windows char strip) but no allowlist, no size/MIME/extension caps, full `await file.read()` in memory, predictable `{userId}_{name}` paths. Downloads are authenticated + ownership-checked (good — never public `/uploads/...`).
- Phase 1 adds: `MAX_UPLOAD_BYTES` (10MB default), MIME/extension allowlist helper, invalid-ObjectId → 404, CSV row caps. Malware-scan interface stubbed (no paid AV; hook for ClamAV/Tesseract later).

## 4. Injection/validation
- Motor queries use dicts with server-side `user_id`; `extra="allow"` lets clients persist arbitrary fields — tighten on writes.
- Negative amounts only rejected for transactions/tax-payments; deductions/investments/scenarios/AIS accept negatives — add non-negative validation on financial writes.
- Enum coercion (`ObligationStatus(...)`) uncaught → 500 on bad values — return 422.
- No secrets in frontend bundle (only `NEXT_PUBLIC_API_URL`); `.env`/`.env.local` git-ignored; compose bakes dev `SECRET_KEY` (dev-only; prod must inject via environment, never commit).

## 5. Headers/transport
- CORS single-origin (good). Missing: CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame-ancestors. Phase 1 adds safe-default headers middleware (no breaking of Next dev).
- No CSRF token (JWT Bearer, no cookies — acceptable; revisit if cookies introduced). No account lockout/backoff yet — Phase 1 adds generous in-memory auth rate limit (high ceiling so E2E unaffected).

## 6. Logging/privacy
- No request IDs, no audit log (only `chat_messages` persisted). Phase 1 adds `X-Request-ID` middleware + `audit_events` collection (best-effort, never breaks writes) + consistent error envelope `{error, code, request_id}` without stack traces.

## 7. Frontend productization (update)
- Public env limited to `NEXT_PUBLIC_API_URL` (+ optional site URL); `.env.example` added.
- 401 → clear + redirect; logout clears session; no credentials in URLs/logs; no `dangerouslySetInnerHTML`.
- Downloads/exports via authenticated `fetch` + blob; uploads validated server-side (caps enforced); filenames sanitized server-side.
- Fake surfaces removed (no fake password/2FA/sessions/deletion). Playwright `auth.spec.ts` covers guards + register→dashboard; tenant isolation via fresh-user E2E design.
