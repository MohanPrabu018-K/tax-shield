# TDS Engine (Phase 6 — BUILT + TESTED)

## Implementation
- `backend/app/tds.py`: 10-section table (192 salary slab-based, 194A/C/H/I/J/Q
  with rates + thresholds), `compute_tds` (threshold gate, 20% no-PAN rule),
  payable-vs-paid summary. Each record stores section+rate+threshold (explainable).
- API: `GET /tds/sections`, `POST /tds/compute`, `POST|GET /tds-records`,
  `GET /tds/summary`. 26AS TDS comparison lives in reconciliation (Phase 0 engine).
  Flag: `FEATURE_TDS=on`.
