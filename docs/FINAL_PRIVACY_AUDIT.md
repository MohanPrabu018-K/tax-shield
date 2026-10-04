# Final Privacy Audit (Phase 16)

## Data collection — minimized and enumerated
| Data | Purpose | Retention |
|------|---------|-----------|
| account (email, name, employment/regime prefs) | auth + product | until deletion |
| financial records (tx, invoices, docs, ledgers) | product core | until deletion (never auto-purged meanwhile) |
| support tickets | support | 24 months |
| notifications, chat | product UX | 12 months |
| audit events | security/compliance | 12 months, survives deletion |
| subscriptions | billing law | 7 years, survives deletion |
| tax rules | regulatory evidence | never deleted |
| consents + history | GDPR-style proof | until deletion |

No third-party analytics, ads, trackers, or error-reporting beacons exist in
the codebase (source grep in zero-cost audit). Cookie notice truthfully says
"essential sign-in session plus on-device preferences".

## User controls — shipped, not promised
- **Consent**: 5 purposes, server-side history, withdrawable (Settings →
  Privacy). Unknown purpose rejected. Live-tested.
- **Export**: CSV/JSON export endpoints tenant-scoped (phase-10 tests).
- **Deletion**: self-serve 3-request flow — request (7-day grace) → status →
  execute (`confirm: DELETE`). Purges 28 collections **and uploaded files**;
  response itemizes retained collections with reasons. Live-tested end-to-end:
  user can no longer log in afterwards.
- **Retention policy** endpoint mirrors the real `RETENTION` table (no
  marketing-vs-reality drift).

## Processing honesty
- Assistant: deterministic tool-based, **zero external LLM calls**, so no
  financial data leaves the server for AI purposes. The `ai_processing`
  consent exists for future model-based flows and is recorded but currently
  gates nothing — stated as such, not overstated.
- Email: templates rendered, recorded in-app; `delivered: false` — no
  silent pretending.
- Fixtures/seed data: PII-free synthetic personas.

## Legal pages (live, in sitemap)
privacy, terms, refund-policy, acceptable-use, disclaimer, cookie-policy,
security, help — all linked from the marketing footer and `/sitemap.xml`.

## Residual
- Deletion grace override (`skip_grace`) is intentionally possible for the
  data subject after confirming "DELETE" — audited.
- Backup files outside Mongo retain deleted data until backup rotation —
  documented in `DATA_RETENTION.md`; restore drills cover it.
