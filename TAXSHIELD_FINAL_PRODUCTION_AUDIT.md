# TaxShield Final Production Audit (Phases 0–2 complete)

## Architecture
Monolith preserved (Next 14 + FastAPI + Mongo 7); additive foundation only.
Fat-router split, workers, and org migration deferred with plans in place.

## Features (live, tested)
Auth, transactions (+bulk/CSV with caps + import summary), investments,
deductions (non-negative validated), documents (capped/validated uploads,
ownership-checked downloads), obligations/deadlines (PATCH compat + clean 404s),
scenarios + compare, tax-payments, AIS/26AS, reconciliation, risks/actions,
tax-detail, dashboard, readiness, demo seed (GET compat + POST), chat/voice
(EN/TA/HI), rules/flags/tax-period read APIs, audit events, notifications model.

## Tax engine
Deterministic; registry v1 shadows live values with checksums; engine reads
registry with exact fallback. Persona proofs: 750k→39000, 930k→67080,
3.725M→889200; rebate cliffs verified. No AI in statutory path.

## GST / TDS / Accounting / CA / Inventory / POS
Not built; honest target specs in `docs/GST_ENGINE.md`, `TDS_ENGINE.md`,
`ACCOUNTING_ENGINE.md`, `CA_WORKSPACE.md`. Nothing simulated as real.

## Documents / Reconciliation
Upload validation + tenant-fixed linking + evidence model present; OCR/
classification/extraction pipeline is Phase 8 work (Tesseract/PyMuPDF, async).

## Security
Isolation hole fixed; rate limits; headers; request IDs; error envelope;
`audit_events`; secrets discipline. Remaining: refresh rotation, `sub=user_id`,
lockout, admin 2FA (documented).

## Privacy
Policy pages exist; consent split, export/delete, AI-default-off documented.
In-app deletion/export endpoints are later-phase work.

## SEO / Performance / Accessibility
`robots.ts`/`sitemap.ts`/edge noindex on private routes; new indexes;
pagination params; tsc clean. Remaining: dynamic charts, server pagination v2,
keyboard/contrast pass, PWA shell.

## AI / Provenance / Cost
Offline deterministic assistant; AI-policy gate defined; provenance schema set;
zero paid deps; caps enforced. COST_AUDIT + LICENSE_AUDIT current.

## Testing
24/24 pytest foundation green; tsc clean; all files compile; E2E suites
untouched and contract-compatible (defaults return full lists).

## Deployment
Compose + Windows scripts + `.env.example`s; `/health` + new `/ready`.

## Known limitations
Single-tenant `user_id` ownership until org migration; synchronous full
re-analysis per write; unbounded-default lists; dev servers in containers;
no refresh tokens; no OCR yet; `alembic/` unused. Each has a sequenced plan above.
