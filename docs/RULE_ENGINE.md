# Rule Engine — TaxShield (Phase 2)

## Principle
Core tax/accounting numbers are **deterministic + versioned + tested + explainable**.
AI never produces statutory truth; it may only explain deterministic results
(see `docs/AI_POLICY.md`).

## Registry (`backend/app/rules.py`)
- `RuleRegistry` with seed v1 = exact values the engine uses today
  (slabs old/new, 87A limits, surcharge bands, 4% cess, thresholds, readiness weights).
- `slab_params(regime, tax_period)` — engine lookup with fail-closed fallback to legacy tables.
- Lifecycle: `propose()` → DRAFT → `mark(VALIDATING/TESTED/APPROVED)` → `activate()`
  (only TESTED/APPROVED/ACTIVE may activate) → `rollback(v)` re-activates history.
  History is never deleted. Every snapshot carries a sha256 `checksum`.
- Reads: `GET /api/rules/versions`, `GET /api/rules/active`, `GET /api/rules/tax-periods`.

## Tax periods (`backend/app/tax_periods.py`)
- `parse_fy("2024-25")`, `fy_from_date()`, `ay_from_fy()` / `fy_from_ay()`,
  `normalize_regime()`, `current_fy()`. Every future rule carries
  `tax_periods: ["2024-25", ...]`; engine validates the period parses as FY
  and never applies a rule outside its effective range.

## Provenance (required for every new statutory value)
authority, source title/URL/document, publication + effective + retrieved dates,
section/reference, extracted rule, version, checksum, validation + activation status.
No invented rates/thresholds/dates — official sources only (see `docs/TAX_DATA_PIPELINE.md`).

## Tests
`backend/tests/test_foundation.py`: persona liabilities (750k→39000, 930k→67080,
3.725M→889200), rebate cliffs, registry parity/lifecycle/rollback, fail-closed
activation. Every rule update must re-run this gate; on failure, do not activate.
