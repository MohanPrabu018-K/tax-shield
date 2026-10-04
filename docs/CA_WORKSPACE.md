# CA Workspace (Phase 11 — BUILT + TESTED)

## Implementation
- `backend/app/practice.py` + API: clients, tasks (open/in_progress/done/cancelled),
  doc-requests (requested/uploaded/verified/rejected), reviews with enforced chain
  `auto → needs_review → accountant/ca → approved` (illegal jumps 422),
  `GET /practice/overview` (clients/open-tasks/pending-reviews).
- `app/tenancy.py` carries Organization/Workspace/Business/Membership roles
  (owner/admin/accountant/ca/employee/client/viewer) for the org migration.
- Complex disputes/litigation/audits always escalate to a qualified professional —
  TaxShield never claims to replace a CA. Flag: `FEATURE_CA_WORKSPACE=on`.
