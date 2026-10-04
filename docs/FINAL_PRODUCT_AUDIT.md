# Final Product Audit (Phase 16)

Scope: does the shipped product match its marketing? Every claim traced to
code + test. Anything untested is marked honestly.

## Verdict: product is sellable with the stated non-claims

## Page → backend traceability
| Page | Backed by | Tested |
|------|-----------|--------|
| `/` marketing, features, FAQ | static server component + real nav links | Playwright (renders, links resolve) |
| `/pricing` | `GET /api/billing/plans` (config) | live tests + page render |
| `/billing` portal (plan, usage, checkout, trial, cancel, history) | billing endpoints | `test_billing_lifecycle_test_adapter` |
| `/support` ticket desk | support CRUD | `test_consents_notifications_support_live` |
| `/notifications` | notifications API (9 categories) | same |
| `/admin` console (7 tabs) | admin endpoints, 403 for non-admin | `test_admin_console_live` |
| `/help /security /privacy /terms /refund-policy /acceptable-use /disclaimer /cookie-policy` | static, linked from footer + sitemap | sitemap/robots tests |
| Settings: password/sessions/consents/deletion | identity + privacy endpoints | `test_password_sessions_live`, deletion live test |

## Honesty checks (no fakes)
- Checkout: `manual` → pending activation (no charge); `test` → labelled
  "TEST ADAPTER: no real payment occurred." Unknown provider → 422.
- ITR prep endpoint: status `READY_FOR_AUTHORIZED_INTEGRATION`, disclaimer in
  payload — never "filed".
- MFA: absent from UI and docs; Settings states it is not shipped.
- Email: `EmailProvider` records in-app only, `delivered: false`.
- Cookie notice: real acknowledgement persisted in localStorage (tested).
- Rule activation: gate enforced live (unknown version 422).

## Known limitations (documented, not hidden)
1. Single uvicorn worker; dashboard p95 grows with per-read analysis.
2. Dev-only npm advisories with no upstream fix (braces/micromatch chain in
   tailwind 3 + eslint plugin); production dependency audit is 0.
3. Voice backend endpoints are live-tested (transcribe/synthesize/422), but
   actual microphone capture cannot be automated headless — manual device
   check required before marketing voice (see `TESTING.md` voice matrix).
4. Manual billing provider requires operator activation (by design).

## Test inventory
104 pytest (incl. 6 live commercial) + 22 Chromium browser (desktop+mobile) +
11 Firefox + 11 WebKit + prior-phase drills (backup/tamper, load, pentest)
= **all green, 0 failed.** Cross-engine note: a WebKit-only hydration race
in form specs was found and fixed properly (test-side hydration gate in
`tests/helpers.ts`) — not skipped or weakened.
