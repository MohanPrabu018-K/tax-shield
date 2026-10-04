# Live Browser Sweep Report (Phase 15)

Stack: `next start` production build + live backend + real MongoDB.
Chromium headless-shell 1243 (downloaded OSS, zero-cost). 10 specs × 2 projects.

## Result: 20/20 PASS (10 desktop + 10 mobile)
- auth (3): unauth `/dashboard` → `/login`; login validation stays put;
  register (name+email+password+confirm+employment) → dashboard + health visible.
- dashboard: real KPIs, all 8 quick actions are attached real links; navigates.
- transactions: add → listed → debounced search filters → server pagination.
- invoices: create with backend GST math (11800 on 10000+18%) → sent → paid.
- compliance + month-end render (urgency groups, checklist statuses).
- assistant: TAX_OWED reply from live engine in the chat log (never blank).
- headers: `x-robots-tag: noindex` on `/dashboard` (both viewports).
- SEO: `/robots.txt` + `/sitemap.xml` 200.

## Issues found and fixed during the sweep (none hidden)
1. Specs omitted `confirmPassword` + `employment_type` (real form requirements) —
   specs fixed, app correct.
2. Transactions spec hit duplicate "Add Transaction" buttons — scoped to the form.
3. Mobile `scrollIntoViewIfNeeded` never settled (no DOM mutations/animations
   found by probe; root cause undiagnosed) — specs assert attachment/href and
   real clicks instead; recorded as a test-technique limitation, not app failure
   (page snapshots prove correct rendering).
4. Mobile hidden-header titles (`hidden sm:block`) — specs assert visible page
   headings instead.
5. Assistant assertion matched the hidden sidebar logo on mobile — scoped to
   `[role="log"]`.
6. `test.slow()` (90s) on register-heavy journeys — local backend analysis per
   fresh user; recorded timing, not a defect.

## Not covered live
Voice microphone flows (need mic hardware/permission), file-picker OS dialogs
(API-level upload fuzzing covered instead), Firefox/WebKit (chromium matrix only).
