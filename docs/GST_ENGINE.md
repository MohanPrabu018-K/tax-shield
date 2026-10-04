# GST Engine (Phase 6 — BUILT + TESTED)

## Implementation
- `backend/app/gst.py`: mod-36 GSTIN checksum (GSTN-published algorithm,
  verified against real fixtures `27AAPFU0939F1ZV`, `33AAACC1206D1ZN`,
  `27AAACR5055K1Z7`), CGST/SGST/IGST split, HSN check, GSTR-1 (rate-wise
  outward) + GSTR-3B (output − ITC = net payable) **preparation summaries**,
  books↔portal reconciliation with explanations.
- API: `POST /gst/validate`, `POST /gst/reconcile`, `GET /gst/summary`;
  invoices compute GST per line at creation (`backend/app/invoicing.py`).
- Preparation ≠ filing: every summary carries a review disclaimer.
  e-Invoice/e-Way Bill remain `not_available` adapters (`GET /integrations/status`).
  Flag: `FEATURE_GST=on`.
