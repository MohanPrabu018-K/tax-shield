# Data Audit — TaxShield (Phase 0)

## 1. Collections (Mongo `tax_shield`)
users, transactions, investments, deductions, documents, obligations, deadlines, scenarios, tax_payments, ais_records, form26as_records, chat_messages. New in Phase 1: `audit_events`, `tax_rules` (registry snapshots), `feature_flags` (optional seed), `notifications` (model only, endpoints later).

## 2. Reference datasets (`datasets/`)
- `01_tax_rules` (rates, deductions, capital gains, TDS, business/profession), `02_compliance` (ITR applicability, deadlines, payments), `03_itr` (forms/fields/validations), `04_tax_information` (AIS/26AS fields), `05_evidence` (doc types, requirements, mapping), `06_intelligence` (project-owned risk/readiness/scenario config — NOT law), `07_synthetic_demo` (20 synthetic CSVs, clearly marked, no PII).
- Gap: engine hardcodes slabs/thresholds and never loads `01_tax_rules` at runtime; responses carry no `rule_version`. Phase 2 seeds `tax_rules` from current hardcoded values + dataset checksums, with provenance + effective FY ranges + rollback. Official sources required before any new statutory value (see `docs/RULE_ENGINE.md`, `docs/TAX_DATA_PIPELINE.md`).

## 3. Test fixtures
- `tests/taxshield_persona_test_cases.json`: 3 personas + expected totals + slab reference + readiness weights (30/25/20/15/10). E2E runners are script-style (`python *.py`), not pytest; `tests/unit|integration`, `backend/tests`, `frontend/tests` empty.
- Phase 1 adds `backend/tests/test_foundation.py` (pytest): tax math vs persona expectations, FY utilities, rule registry + rollback, feature flags, pagination slicing, upload validation. E2E suites unchanged and must keep passing.

## 4. Retention/privacy
- `uploads/` on local disk (dev) → abstract `DocumentStorage` (Local now, object-storage adapter later; never public URLs).
- `audit_events` + security logs retained per `docs/DATA_RETENTION.md`; temporary training/ingestion dirs (`temporary_*`, `training_*`) must be empty after jobs (see `docs/AI_POLICY.md`). Never delete rule snapshots, provenance, production artifacts, user docs, or audit records during cleanup.

## 5. Migration plan (additive, no downtime)
1. Add new collections/models with defaults; existing `user_id` queries untouched.
2. Backfill `tax_period`/`rule_version` on new writes; old docs remain valid.
3. Org migration later: `Organization → Workspace → Business → Membership`, data keyed by `(org_id, user_id)` with compat shim. No destructive rewrites without a migration script + backup.
